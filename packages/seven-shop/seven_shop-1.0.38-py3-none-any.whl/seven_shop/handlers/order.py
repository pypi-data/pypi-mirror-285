# -*- coding: utf-8 -*-
"""
:Author: Kangwenbin
:Date: 2021-12-01 14:39:13
:LastEditTime: 2024-07-16 10:25:58
:LastEditors: KangWenBin
:Description: 
"""

from seven_shop.handlers.seven_base import *
from seven_shop.models.db_models.cart.cart_model import *
from seven_shop.models.db_models.order.order_model_ex import *
from seven_shop.models.db_models.order.order_goods_model_ex import *
from seven_shop.models.db_models.goods.goods_model_ex import *
from seven_shop.models.db_models.shop.shop_model_ex import *
from seven_shop.models.db_models.inventory.inventory_change_model import *
from seven_shop.models.db_models.order.order_refund_model_ex import *
from seven_shop.models.db_models.order.order_refund_goods_model_ex import *
from seven_shop.libs.customize.wechat_helper import *
from seven_shop.libs.customize.order_helper import *
from seven_shop.libs.customize.coupon_helper import *
from decimal import Decimal


class OrderPrepareHandler(SevenBaseHandler):
    @filter_check_params(["buy_list","user_code","shop_id"])
    def post_async(self):
        """
        :description: 订单明细展示
        :last_editors: Kangwenbin
        """        
        buy_list = self.request_params["buy_list"]
        province_name = self.request_params.get("province_name","")
        user_code = self.request_params["user_code"]
        coupon_id = int(self.request_params.get("coupon_id",0))
        shop_id = self.request_params["shop_id"]
        
        check_result = OrderHelper.order_check(shop_id,buy_list,province_name,user_code,coupon_id)
        if check_result["result"] == 1:
            return self.reponse_json_success(check_result["data"])
        
        self.reponse_json_error(check_result["desc"])
                

class OrderCreateHandler(SevenBaseHandler):
    @filter_check_params(["buy_list","address_info","user_code","pay_price","channel_id","open_id","shop_id"])
    def post_async(self):
        """
        :description: 下单
        :last_editors: Kangwenbin
        """        
        address_info = self.request_params["address_info"]
        buy_list = self.request_params["buy_list"]
        remark = self.request_params.get("remark","")
        user_code = self.request_params["user_code"]
        open_id = self.request_params["open_id"]
        pay_price = str(self.request_params["pay_price"])
        channel_id = self.request_params["channel_id"] # 订单来源 1 商品页 2 购物车
        coupon_id = int(self.request_params.get("coupon_id",0))
        shop_id = self.request_params["shop_id"]

        try:
            order_conn = OrderModelEx()
            inventory_conn = InventoryModelEx()
            # 订单验证
            check_result = OrderHelper.order_check(shop_id,buy_list,address_info["province_name"],user_code,coupon_id)
            if check_result["result"] == 0:
                return self.reponse_json_error(check_result["desc"])
            order_data = check_result["data"]

            # 验证订单状态
            if order_data["order_status"] == 0:
                return self.reponse_json_error("订单无法支付")  
            
            # 验证金额
            if Decimal(pay_price) != order_data["pay_price"]:
                return self.reponse_json_error("订单金额异常")
            
            # 扣除库存
            total_buy_count = 0
            for goods in order_data["goods_list"]:
                # 购买总数量添加
                total_buy_count += goods["buy_count"]
                # 直接修改库存
                row_count = inventory_conn.update_check_inventory(goods["goods_id"],goods["sku_id"],goods["buy_count"])
                if row_count == 0:
                    goods_name = f"{goods['goods_name']}" if goods["sku_name"]=="" else f"{goods['goods_name']}({goods['sku_name']})"
                    return self.reponse_json_error(f"商品{goods_name}库存不足")

            db_transaction = DbTransaction(config.get_value("db_shopping_center"))
            # 创建事务链接
            transaction_order_model = OrderModel(db_transaction=db_transaction)
            transaction_order_goods_model = OrderGoodsModel(db_transaction=db_transaction)
            transaction_coupon_model = CouponRecordModel(db_transaction=db_transaction)
            transaction_inventory_change_model = InventoryChangeModel(db_transaction=db_transaction)
            transaction_cart_model = CartModel(db_transaction=db_transaction)

            # 开始事务
            db_transaction.begin_transaction()
            
            # 添加主订单信息
            order_id = OrderHelper.create_order_number()
            order_entity = Order()
            order_entity.shop_id = shop_id
            order_entity.order_id = order_id
            order_entity.pay_channel = 0
            order_entity.channel_id = channel_id
            order_entity.pay_order_id = ""
            order_entity.user_code = user_code
            order_entity.open_id = open_id
            order_entity.province_name = address_info["province_name"]
            order_entity.city_name = address_info["city_name"]
            order_entity.district_name = address_info["district_name"]
            order_entity.consignee = address_info["consignee"]
            order_entity.phone = address_info["phone"]
            order_entity.address_info = address_info["address_info"]
            order_entity.buy_count = total_buy_count
            order_entity.price = order_data["goods_price"]
            order_entity.real_pay_price = order_data["pay_price"]
            order_entity.postage = order_data["postage"]
            order_entity.coupon_id = coupon_id
            order_entity.coupon_price = order_data["coupon_price"]
            order_entity.add_time = TimeHelper.get_now_timestamp()
            order_entity.pay_time = 0
            order_entity.status = 0
            order_entity.remark = remark 
            transaction_order_model.add_entity(order_entity)

            # 添加订单商品信息
            for goods in order_data["goods_list"]:
                order_goods_entity = OrderGoods()
                order_goods_entity.order_id = order_id
                order_goods_entity.goods_id = goods["goods_id"]
                order_goods_entity.sku_id = goods["sku_id"]
                order_goods_entity.sku_name = goods["sku_name"]
                order_goods_entity.goods_picture = goods["goods_picture"]
                order_goods_entity.user_code = user_code
                order_goods_entity.goods_name = goods["goods_name"]
                order_goods_entity.buy_count = goods["buy_count"]
                order_goods_entity.price = goods["total_price"]
                order_goods_entity.real_pay_price = goods["total_price"] - goods["coupon_price"]
                order_goods_entity.coupon_id = goods["coupon_id"]
                order_goods_entity.coupon_price = goods["coupon_price"]
                order_goods_entity.goods_code = goods["goods_code"]
                order_goods_entity.add_time = TimeHelper.get_now_timestamp()
                transaction_order_goods_model.add_entity(order_goods_entity)

                # 添加商品库存变更表
                inventory_change_entity = InventoryChange()
                inventory_change_entity.order_id = order_id
                inventory_change_entity.goods_id = goods["goods_id"]
                inventory_change_entity.sku_id = goods["sku_id"]
                inventory_change_entity.change_inventory = 0 - goods["buy_count"]
                inventory_change_entity.add_time = TimeHelper.get_now_timestamp()
                inventory_change_entity.add_user = user_code
                inventory_change_entity.remark = ""
                transaction_inventory_change_model.add_entity(inventory_change_entity)

                # 更改优惠券状态
                if order_entity.coupon_id > 0:
                    transaction_coupon_model.update_table(update_sql="status = 1,use_time = %s,order_id = %s",where="id = %s",params=[TimeHelper.get_now_timestamp(),order_id,order_entity.coupon_id])

                # 如果是从购物车入口来的，删除购物车对应商品
                if int(channel_id ) == 2:
                    transaction_cart_model.del_entity(where="user_code = %s and goods_id = %s and sku_id = %s",params=[user_code,goods["goods_id"],goods["sku_id"]])
                    
            # 事务提交
            transaction_result = db_transaction.commit_transaction(True)
            if transaction_result[0]:
                # 下单成功扩展方法
                try:
                    self.order_create_success_extend(order_id)
                    # self.order_pay_success_extend(order_id)
                except:
                    self.logger_error.error(f"下单成功扩展方法异常：order_id:{order_id},error_msg:{traceback.format_exc()}")

                # 存在需要支付的金额为0的情况
                if order_entity.real_pay_price <= 0:
                    # 修改订单状态为已支付
                    pay_time = TimeHelper.get_now_timestamp()
                    if order_conn.update_table(update_sql="status = 2,pay_time = %s",where="order_id = %s and user_code = %s",params = [pay_time,order_id,user_code]):
                        try:
                            self.order_pay_success_extend(order_id)
                        except:
                            self.logger_error.error(f"无需支付下单成功扩展方法异常：order_id:{order_id},error_msg:{traceback.format_exc()}")
                        return self.reponse_json_success(
                            {
                                "pay_type": 2, # 支付类型 1 需要第三方支付 2 无需第三方支付
                                "order_id": order_id,
                                "pay_request_data": None
                            }
                        )
                    else:
                        self.logger_error.error(f"订单更新失败：{order_id}")
                        return self.reponse_json_error("订单支付失败")

                else:
                    # 微信小程序支付
                    pay_request_data = WechatPayHelper().wechat_jsapi_pay(order_id,"商品购买",int(order_entity.real_pay_price*100),open_id)
                    if pay_request_data["result"] == 1:
                        ret_data = {
                            "pay_type": 1, # 支付类型 1 需要第三方支付 2 无需第三方支付
                            "order_id": order_id,
                            "pay_request_data":pay_request_data["data"]
                        }
                        # 将支付信息写入redis
                        self.redis_init.set(f"shopping_center:pay_data:{order_id}",json.dumps(pay_request_data["data"]),ShopModelEx().get_pay_wait_time(shop_id)*60)
                        return self.reponse_json_success(ret_data)
                    else:
                        self.logger_error.error(f"支付信息异常：order_id:{order_id},desc:{pay_request_data['desc']}")
                        return self.reponse_json_error("支付信息异常")
            else:
                self.logger_error.error(transaction_result[1])
                return self.reponse_json_error("订单创建异常")
        except:
            # 记录错误日志
            self.reponse_json_error("订单创建失败")
            self.logger_error.error(traceback.format_exc())
        finally:
            inventory_conn.check_goods_inventory_list(buy_list)

    def order_create_success_extend(self, order_id):
        """
        :description: 下单成功扩展方法
        :last_editors: KangWenBin
        """        
        pass

    def order_pay_success_extend(self, order_id):
        """
        :description: 无需支付下单成功扩展
        :last_editors: KangWenBin
        """        
        pass


class OrderaddressHandler(SevenBaseHandler):
    @filter_check_params(["order_id","address_info","shop_id"])
    def post_async(self):
        """
        :description: 修改物流地址
        :last_editors: Kangwenbin
        """     
        order_id = self.request_params["order_id"]
        address_info = self.request_params["address_info"]
        shop_id = self.request_params["shop_id"]

        order_model = OrderModel().get_dict(where="order_id = %s and shop_id = %s",params=[order_id,shop_id],field="status,postage")
        if not order_model:
            return self.reponse_json_error("无法获取订单信息")
        
        # 验证当前订单状态
        if order_model["status"] not in (0,2):
            return self.reponse_json_error("订单状态无法修改地址信息")
        
        # 验证原订单邮费和变更后是否需要邮费
        postage = ShopModelEx().get_postage(address_info["province_name"],shop_id)
        if postage < 0:
            return self.reponse_json_error("店铺配置信息错误,请联系客服")
        
        # 验证原订单邮费和变更后是否相等
        if order_model["postage"] != postage:
            return self.reponse_json_error("当前修改地址与原地址运费不一致，请联系客服修改或重新下单")
            
        # 修改订单地址
        OrderModel().update_table("province_name=%s,city_name=%s,district_name=%s,consignee=%s,phone=%s,address_info=%s","order_id = %s",params=(address_info["province_name"],address_info["city_name"],address_info["district_name"],address_info["consignee"],address_info["phone"],address_info["address_info"],order_id))
            
        return self.reponse_json_success(desc="提交成功")


class RestartPayHandler(SevenBaseHandler):
    @filter_check_params(["order_id","shop_id"])
    def get_async(self):
        """
        :description: 重新唤起支付
        :last_editors: Kangwenbin
        """        
        order_id = self.request_params["order_id"]
        shop_id = self.request_params["shop_id"]

        order_conn = OrderModel()
        order_model = order_conn.get_dict(where="order_id = %s and shop_id = %s",params=[order_id,shop_id], field="status")
        if not order_model:
            return self.reponse_json_error("无法获取订单信息,请重新下单")
        # 验证当前订单状态
        if order_model["status"] != 0:
            return self.reponse_json_error("订单无法支付，请重新下单")
        # 判断是否redis中已存在支付信息
        pay_model = self.redis_init.get(f"shopping_center:pay_data:{order_id}")
        if pay_model:
            ret_data = {
                "pay_request_data": json.loads(pay_model)
            }
            return self.reponse_json_success(ret_data)
        
        self.reponse_json_error("订单超时支付，请重新下单")


class PayCallbackHandler(SevenBaseHandler):
    def post_async(self):
        """
        @description: 微信支付回调
        @last_editors: KangWenBin
        """
        wechat_helper = WechatPayHelper()
        # 微信支付验签
        headers = self.request.headers._dict
        timestamp = headers.get("Wechatpay-Timestamp", None)
        nonce = headers.get("Wechatpay-Nonce", None)
        signature = headers.get("Wechatpay-Signature", None)
        # data = b'{"id":"6f1cb858-c6ce-55dd-a2e8-1102a0482299","create_time":"2023-09-18T15:11:44+08:00","resource_type":"encrypt-resource","event_type":"TRANSACTION.SUCCESS","summary":"\xe6\x94\xaf\xe4\xbb\x98\xe6\x88\x90\xe5\x8a\x9f","resource":{"original_type":"transaction","algorithm":"AEAD_AES_256_GCM","ciphertext":"BF4Gyw/PLTH2c3aMYnOCKgLbcHEmaSSDfR1rTCguLWVx88gF11Ks65YxftFDEC88rr4LPITtRmBXqbHUkfXjyvp4RABiuR9uFyFfxqWI/wDy5a3GNLzjaIaYt3lsDq5NtPEIOuUPbCHRXhVvnwQvqGph4UD7QC4uj3LtLIbn3qfFLh45yuTQhkLkE1k7dbJqZa9UFIpl042BLPvM6PViSywpRNX1hvNgry3XO5d5zE957ptaBixUg/Z7DbwOrJq4CMe2fSpnrJeo/6iCZ2F3Zd58IOItoQEqiMt6wjKZySDyt5RJl/7buwGLsRt7XbbW+7v7XAl6xRYbChLBsoDbCTWmIEqHgmH2BEMVrhY9lQ9jMbe8VYiyGoSScsCLsh2Eje805rOu1dcoYMrjjjfcn87488zGeCAk4lXdCxXqyf6uaIzPXvT65ftVOzbCQmjJrvJnM+vwDmybvho2JkKZAmNHpxfqYXv9aQLIsnKtBU3WluPBhFH82IRGrJ8M1N/TCVTnMa2zYNi1wUFV6h0x2d9ddoj7OmLz/3sEx3cwkbVkfwrSt0pCtPb3D6tR1PoFySwR","associated_data":"transaction","nonce":"sYd7BfNCD6ja"}}'
        data = self.request.body
        self.logger_info.info(f"timestamp:{timestamp},nonce:{nonce},signature:{signature},data:{data}")
        if wechat_helper.check_notify_sign(timestamp,nonce,data,signature):
            # 验签通过
            data = json.loads(data)
            if data["event_type"] == "TRANSACTION.SUCCESS":
                # data解密
                pay_string =  wechat_helper.decode_notify_data(data["resource"]["ciphertext"],data["resource"]["nonce"],data["resource"]["original_type"])
                pay_data = json.loads(pay_string)
                self.logger_info.info(pay_data)
                if pay_data["trade_state"] != "SUCCESS": # 不是成功的数据直接返回
                    return self.write("success")
                
                order_id = pay_data["out_trade_no"]
                pay_time = wechat_helper.iso_to_timestamp(pay_data["success_time"])

                # mysql链接初始化
                order_conn = OrderModelEx()
                goods_conn = GoodsModel()
                
                # 进行业务处理
                order_model = order_conn.get_dict(where="order_id = %s",params = order_id, field="status,real_pay_price")
                if not order_model:
                    self.logger_error.error(f"微信支付回调:无法获取订单信息,order_id:{order_id}")
                    return self.write("error")
                
                if order_model["status"] != 0:
                    self.logger_error.error(f"微信支付回调:订单状态异常,order_id:{order_id}")
                    return self.write("error")

                # 验证订单金额和微信支付金额
                if int(order_model["real_pay_price"]*100) != pay_data["amount"]["total"]:
                    self.logger_error.error(
                        f"微信支付订单[{order_id}] 金额不匹配疑似刷单.数据库金额:{order_model['real_pay_price']*100} 平台回调金额:{pay_data['amount']['total']};")
                    return self.write("error")

                

                # 修改订单状态
                if order_conn.update_table(update_sql="status = 2,pay_time = %s,pay_order_id = %s",where="order_id = %s",params = [pay_time,pay_data["transaction_id"],order_id]):
                    # 修改商品销量
                    try:
                        # 商品销量变更
                        order_goods_list = OrderGoodsModelEx().get_dict_list(where="order_id = %s",params=order_id,field="goods_id,buy_count")
                        for item in order_goods_list:
                            goods_conn.update_table("goods_sold = goods_sold + %s","id = %s",params=[item["buy_count"],item["goods_id"]])
                        # 订单支付成功业务处理
                        try:
                            self.order_pay_success_extend(order_id)
                        except:
                            self.logger_error.error(f"订单支付成功业务处理失败,order_id:{order_id},error_msg:{traceback.format_exc()}")

                    except:
                        pass
                    return self.write("success")
                
                else:
                    return self.write("error")
                
        else:
            self.logger_error.error(f"微信验签失败,data:{data}")
            return self.write("success")
        

        self.write("success")


    def order_pay_success_extend(self,order_id):
        """
        :description: 支付成功方法扩展
        :last_editors: KangWenBin
        """        
        pass


class PayResultHandler(SevenBaseHandler):
    @filter_check_params(["order_id","shop_id"])
    def post_async(self):
        '''
        @description: 订单支付结果轮询接口
        @author: KangWenBin
        '''
        order_id = self.request_params["order_id"]
        shop_id = self.request_params["shop_id"]

        order_model = OrderModel().get_dict(where="order_id = %s and shop_id = %s",params = [order_id,shop_id],field="status")
        if not order_model:
            return self.reponse_json_error("无法获取订单数据")
            
        ret_model = {
            "pay_status": order_model["status"] # 0 未支付 1 已取消 2 已支付
        }

        self.reponse_json_success(ret_model)


class OrderListHandler(SevenBaseHandler):
    @filter_check_params(["user_code","shop_id"])
    def get_async(self):
        """
        :description: 订单列表
        :last_editors: Kangwenbin
        """    
        user_code = self.request_params["user_code"]
        page_index = int(self.request_params.get("page_index",0))
        page_size = int(self.request_params.get("page_size",10))
        status_type = int(self.request_params["status_type"]) # 状态 -1 全部 0 未支付 2 已支付(待发货) 3 已发货 4 已完成
        shop_id = self.request_params["shop_id"]

        condition = "user_code = %s and shop_id = %s"
        param_list = [user_code,shop_id]
        if status_type != -1:
            condition += " and status = %s"
            param_list.append(status_type)
        
        order_list,is_next = OrderModel().get_dict_page_list(field="order_id,status,add_time,real_pay_price,postage,coupon_price,logistics_company,logistics_number",page_index=page_index,page_size=page_size,where=condition,params=param_list,order_by="add_time desc",page_count_mode="next")
        if order_list:
            # 订单id
            order_id_list = [x["order_id"] for x in order_list]
            # 订单商品列表
            order_goods_list = OrderGoodsModelEx().get_order_goods_list(order_id_list)
            
            for item in order_list:
                # 获取订单商品详情
                item["goods_list"] = [x for x in order_goods_list if x["order_id"] == item["order_id"]]

        ret_data = {
            "is_next": is_next,
            "model_list": order_list
        }
        
        self.reponse_json_success(ret_data)
                
                
class CancelOrderHandler(SevenBaseHandler):
    @filter_check_params(["order_id","shop_id"])
    def post_async(self):
        """
        :description: 取消订单
        :last_editors: Kangwenbin
        """        
        order_id = self.request_params["order_id"]
        shop_id = self.request_params["shop_id"]
        
        order_model = OrderModelEx().get_dict(where="order_id = %s and shop_id = %s",params=[order_id,shop_id],field="status,coupon_id")
        if not order_model:
            return self.reponse_json_error("无法获取订单信息")
        
        if order_model["status"] != 0:
            return self.reponse_json_error("当前订单无法取消")

        # 更改订单状态、释放库存、释放优惠券
        db_transaction = DbTransaction(config.get_value("db_shopping_center"))
        # 创建事务链接
        transaction_order_model = OrderModel(db_transaction=db_transaction)
        transaction_inventory_model = InventoryModel(db_transaction=db_transaction)
        transaction_inventory_change_model = InventoryChangeModel(db_transaction=db_transaction)
        transaction_coupon_model = CouponRecordModel(db_transaction=db_transaction)
       
        # 开始事务
        db_transaction.begin_transaction()
        # 订单修改
        transaction_order_model.update_table("status = 1,finish_time = %s","order_id = %s",params=[TimeHelper.get_now_timestamp(), order_id])
        # 优惠券修改
        if order_model["coupon_id"] > 0:
            transaction_coupon_model.update_table("status = 0, order_id = '', use_time = 0","id = %s",params=order_model["coupon_id"])

        # 库存处理
        inventory_change_list = transaction_inventory_change_model.get_dict_list(where="order_id = %s",params=order_id)
        if inventory_change_list:
            for item in inventory_change_list:
                transaction_inventory_model.update_table(update_sql="inventory = inventory + %s",where="goods_id = %s and sku_id = %s",params=[abs(item["change_inventory"]),item["goods_id"],item["sku_id"]])
            transaction_inventory_change_model.del_entity("order_id = %s",order_id)
        
        transaction_result = db_transaction.commit_transaction(True)
        if transaction_result[0]:
            InventoryModelEx().check_goods_inventory_list(inventory_change_list)
            return self.reponse_json_success(desc = "提交成功")
        else:
            self.logger_error.error(transaction_result[1])
            return self.reponse_json_error("提交失败")


class OrderReceiptHandler(SevenBaseHandler):
    @filter_check_params(["order_id","shop_id"])
    def post_async(self):
        """
        :description: 确认收货
        :last_editors: Kangwenbin
        """        
        order_id = self.request_params["order_id"]
        shop_id = self.request_params["shop_id"]
        order_conn = OrderModelEx()

        order_model = order_conn.get_dict(where="order_id = %s and shop_id = %s",params=[order_id,shop_id],field="status")
        if not order_model:
            return self.reponse_json_error("无法获取订单信息")
        
        if order_model["status"] != 3:
            return self.reponse_json_error("当前订单无法确认收货")
        
        if order_conn.update_table(update_sql="status = 4,is_complete = 1,finish_time = %s",where="order_id = %s",params=[TimeHelper.get_now_timestamp(),order_id]):
            try:
                self.order_complete_success_extend(order_id)
            except:
                self.logger_error.error(f"订单完成扩展方法异常：order_id:{order_id},error_msg:{traceback.format_exc()}")
            return self.reponse_json_success(desc = "提交成功")
        
        self.reponse_json_error("提交失败")

    def order_complete_success_extend(self, order_id):
        """
        :description: 订单完成扩展方法
        :last_editors: KangWenBin
        """        
        pass


class OrderDetailHandler(SevenBaseHandler):
    @filter_check_params(["order_id","shop_id"])
    def get_async(self):
        """
        :description: 订单详细
        :last_editors: Kangwenbin
        """        
        order_id = self.request_params["order_id"]
        shop_id = self.request_params["shop_id"]

        order_conn = OrderModelEx()
        
        order_model = order_conn.get_dict(where="order_id = %s and shop_id = %s",params=[order_id,shop_id],field = "pay_order_id,price,real_pay_price,postage,coupon_price,add_time,pay_time,status,logistics_company,logistics_number,logistics_time,remark,province_name,city_name,district_name,consignee,phone,address_info")
        if not order_model:
            return self.reponse_json_error("无法获取订单信息")

        order_model["goods_list"] = OrderGoodsModelEx().get_order_goods_list([order_id])

        self.reponse_json_success(order_model)


class RefundGoodsHandler(SevenBaseHandler):
    @filter_check_params(["order_id","shop_id"])
    def get_async(self):
        """
        :description: 退款商品选择
        :last_editors: Kangwenbin
        """        
        order_id = self.request_params["order_id"]
        shop_id = self.request_params["shop_id"]

        order_model = OrderModelEx().get_dict(where="order_id = %s and shop_id = %s",params=[order_id,shop_id],field="status,is_refund")
        if not order_model:
            return self.reponse_json_error("无法获取订单信息")

        if order_model["status"] not in (2,3,4,5):
            return self.reponse_json_error("此订单无法退款、退货")

        ret_model = {
            "refund_goods_list":[],
            "status": order_model["status"] # 2 已支付 4 已完成
        }

        # 获取订单商品列表
        order_goods_list = OrderGoodsModelEx().get_refund_goods_list(order_id)
        if not order_goods_list:
            return self.reponse_json_error("无法获取商品订单信息")

        ret_model["refund_goods_list"] = order_goods_list
        return self.reponse_json_success(ret_model)


class ApplyRefundHandler(SevenBaseHandler):
    @filter_check_params(["order_id","refund_info","user_code","shop_id"])
    def post_async(self):
        """
        :description: 退款单创建
        :last_editors: Kangwenbin
        """        
        order_id = self.request_params["order_id"]
        refund_info = self.request_params["refund_info"]
        user_code = self.request_params["user_code"]
        shop_id = self.request_params["shop_id"]
        
        order_model = OrderModelEx().get_dict(where="order_id = %s and shop_id = %s",params=[order_id,shop_id],field="status,postage,real_pay_price,price,coupon_price,coupon_id,logistics_number")
        if not order_model:
            return self.reponse_json_error("无法获取订单信息")

        if order_model["status"] not in (2,3,4,5):
            return self.reponse_json_error("此订单无法退款、退货")
            
        if not refund_info["goods_list"]:
            return self.reponse_json_error("无法获取退款商品信息")
        
        # 获取需退款的商品信息
        refund_goods_list = OrderGoodsModelEx().get_refund_goods_list(order_id,refund_info["goods_list"])
        
        # 验证当前是否有商品已退款过 
        if [x for x in refund_goods_list if x["refund_status"] == 1]:
            return self.reponse_json_error("退款商品异常")

        # 商品退款总额
        refund_goods_price = Decimal(sum([x["real_pay_price"] for x in refund_goods_list])) 

        # 运费
        refund_postage = 0
        # 如果订单为已发货，不退运费
        if order_model["logistics_number"] == "":

            order_goods_count = OrderGoodsModelEx().get_total(where="order_id = %s", params=[order_id])
            order_refund_goods_count = OrderRefundGoodsModel().get_total(where="order_id = %s", params=[order_id])
            
            if order_goods_count == order_refund_goods_count + len(refund_info["goods_list"]):
                refund_postage = order_model["postage"]


        db_transaction = DbTransaction(config.get_value("db_shopping_center"))
        # 创建事务链接
        transaction_refund_model = OrderRefundModel(db_transaction=db_transaction)
        transaction_order_model = OrderModel(db_transaction=db_transaction)
        transaction_refund_goods_model = OrderRefundGoodsModel(db_transaction=db_transaction)

        # 开始事务
        db_transaction.begin_transaction()

        # 添加退款订单
        refund_order_id = "T" + OrderHelper.create_order_number()
        refund_entity = OrderRefund()
        refund_entity.shop_id = shop_id
        refund_entity.order_id = order_id
        refund_entity.refund_order_id = refund_order_id
        refund_entity.refund_type = refund_info["refund_type"]
        refund_entity.goods_refund_price = refund_goods_price
        refund_entity.real_refund_price = refund_goods_price+refund_postage
        refund_entity.postage = refund_postage
        refund_entity.reason = refund_info["reason"]
        refund_entity.status = 0
        refund_entity.add_time = TimeHelper.get_now_timestamp()
        refund_entity.user_code = user_code
        transaction_refund_model.add_entity(refund_entity)
        
        # 更改原订单退款状态
        transaction_order_model.update_table("is_refund = 1","order_id = %s",order_id)

        # 添加退款商品表
        for item in refund_goods_list:
            refund_goods_entity = OrderRefundGoods()
            refund_goods_entity.order_id = order_id
            refund_goods_entity.refund_order_id = refund_order_id
            refund_goods_entity.goods_id = item["goods_id"]

            refund_goods_entity.sku_id = item["sku_id"]
            refund_goods_entity.sku_name = item["sku_name"]
            refund_goods_entity.goods_name = item["goods_name"]
            refund_goods_entity.goods_picture = item["goods_picture"]
            refund_goods_entity.refund_count = item["buy_count"]
            refund_goods_entity.refund_price = item["real_pay_price"]
            refund_goods_entity.add_time = TimeHelper.get_now_timestamp()
            refund_goods_entity.goods_code = item["goods_code"]
            transaction_refund_goods_model.add_entity(refund_goods_entity)
        

        # 事务提交
        transaction_result = db_transaction.commit_transaction(True)
        if transaction_result[0]:
            ret_data = {
                "refund_order_id": refund_order_id
            }
            return self.reponse_json_success(ret_data)        
        else:
            self.logger_error.error(transaction_result[1])
            return self.reponse_json_error("提交失败")
    

class RefundDetailHandler(SevenBaseHandler):
    @filter_check_params(["refund_order_id","shop_id"])
    def get_async(self):
        """
        :description: 退款单详细
        :last_editors: Kangwenbin
        """        
        refund_order_id = self.request_params["refund_order_id"]
        shop_id = self.request_params["shop_id"]

        refund_model = OrderRefundModel().get_dict(where="refund_order_id = %s and shop_id = %s",params=[refund_order_id,shop_id],field="order_id,refund_order_id,refund_type,goods_refund_price,real_refund_price,postage,reason,status,add_time,pass_time,pass_remark,fail_remark,logistics_company,logistics_number,logistics_time")
        if not refund_model:
            return self.reponse_json_error("无法获取退款服务单信息")

        # 获取退款商品信息
        refund_order_goods_list = OrderRefundGoodsModel().get_dict_list(where="refund_order_id = %s",params=refund_order_id,field="goods_id,sku_id,sku_name,goods_name,goods_picture,refund_count,refund_price")
        refund_model["refund_goods_list"] = refund_order_goods_list
        
        self.reponse_json_success(refund_model)


class RefundCancelHandler(SevenBaseHandler):
    @filter_check_params(["refund_order_id","shop_id"])
    def post_async(self):
        """
        :description: 取消退款申请
        :last_editors: Kangwenbin
        """
        refund_order_id = self.request_params["refund_order_id"]
        shop_id = self.request_params["shop_id"]

        refund_conn = OrderRefundModel()
        refund_model = refund_conn.get_dict(where="refund_order_id = %s and shop_id = %s", params=[refund_order_id,shop_id],field="status")
        if not refund_model:
            return self.reponse_json_error("无法获取退款单信息")

        # 判断退款单状态
        if refund_model["status"] not in[0,1]:
            return self.reponse_json_error("退款单无法撤销")
        
        # 撤销退款单
        if refund_conn.update_table(update_sql="status = 4",where="refund_order_id = %s",params=refund_order_id):
            return self.reponse_json_success(desc="提交成功")
        
        self.reponse_json_error("提交失败")


class RefundLogisticsHandler(SevenBaseHandler):
    @filter_check_params(["refund_order_id","logistics_number","logistics_company","shop_id"])
    def post_async(self):
        """
        :description: 退款申请单买家发货
        :last_editors: Kangwenbin
        """        
        refund_order_id = self.request_params["refund_order_id"]
        logistics_number = self.request_params["logistics_number"]
        logistics_company = self.request_params["logistics_company"]
        shop_id = self.request_params["shop_id"]
        refund_conn = OrderRefundModel()

        refund_model = refund_conn.get_dict(where="refund_order_id = %s and shop_id = %s", params=[refund_order_id,shop_id],field="status")
        if not refund_model:
            return self.reponse_json_error("无法获取退款服务单信息")

        # 判断退款单状态    
        if refund_model["status"] != 1:
            return self.reponse_json_error("退款单状态异常")
        
        # 验证单号是否准确
        # 验证是否是顺丰
        if logistics_number.find("SF") == 0:
            shop_model = ShopModel().get_dict(where="id = %s",params=shop_id,field="phone")
            if shop_model:
                logistics_number = f"{logistics_number}:{shop_model['phone'][-4:]}"
            else:
                return self.reponse_json_error("顺丰单号异常")

        appcode = config.get_value("logistics_appcode")
        url = config.get_value("logistics_url")
        headers = {
            'Authorization': 'APPCODE ' + appcode
        }
        param = {
            "no": logistics_number
        }

        try:
            ret = requests.get(url, headers=headers,data=param)
            if ret.status_code == 200:
                ret = json.loads(ret.text)
                if ret["status"] == "201":
                    return self.reponse_json_error(ret["msg"])
        except:
            self.logger_error.error(f"物流接口请求失败，error:{traceback.format_exc()}")
        
        
        # 更新到退款单
        if refund_conn.update_table(update_sql="logistics_number = %s,logistics_company = %s,logistics_time = %s,status = 3",where="refund_order_id = %s",params=[logistics_number,logistics_company,TimeHelper.get_now_timestamp(),refund_order_id]):
            return self.reponse_json_success("提交成功")

        self.reponse_json_error("提交失败")
        

class RefundListHandler(SevenBaseHandler):
    @filter_check_params(["user_code","shop_id"])
    def get_async(self):
        """
        :description: 退款单列表
        :last_editors: Kangwenbin
        """        
        page_index = int(self.request_params.get("page_index",0))
        page_size = int(self.request_params.get("page_size",10))
        user_code = self.request_params["user_code"]
        shop_id = self.request_params["shop_id"]

        refund_order_list,is_next = OrderRefundModel().get_dict_page_list(where="user_code = %s and shop_id = %s",params=[user_code,shop_id],page_index=page_index,page_size=page_size,field="order_id,refund_order_id,status,goods_refund_price,real_refund_price,postage",order_by="id desc",page_count_mode="next")
        if refund_order_list:
            # 退款单id
            order_id_list = [x["refund_order_id"] for x in refund_order_list]
            # 退款单商品列表
            order_goods_list = OrderRefundGoodsModel().get_dict_list(where="refund_order_id in %s",params=(order_id_list,),field="refund_order_id,goods_id,sku_id,sku_name,goods_name,goods_picture,refund_count,refund_price")
            
            for item in refund_order_list:
                # 获取订单商品详情
                item["refund_goods_list"] = [x for x in order_goods_list if x["refund_order_id"] == item["refund_order_id"]]


        ret_data = {
            "is_next": is_next,
            "model_list": refund_order_list
        }

        self.reponse_json_success(ret_data)

          
class LogisticsHandler(SevenBaseHandler):
    @filter_check_params(["order_id","shop_id"])
    def get_async(self):
        """
        :description: 物流查询接口
        :last_editors: Kangwenbin
        """        
        order_id = self.request_params["order_id"]
        shop_id = self.request_params["shop_id"]

        # 判断是否存在redis中
        redis_logistics = self.redis_init.get(f"shopping_center:logistics:{order_id}")
        if redis_logistics:
            return self.reponse_json_success(json.loads(redis_logistics))

        order_model = OrderModel().get_dict(where="order_id = %s and shop_id = %s",params=[order_id,shop_id],field="status,logistics_number,phone")
        if not order_model:
            return self.reponse_json_error("无法获取订单信息")

        if order_model["status"] not in [3,4]:
            return self.reponse_json_error("无法获取物流信息")

        if not order_model["logistics_number"]:
            return self.reponse_json_error("无法获取物流单号")

        logistics_number = order_model["logistics_number"]
        # 验证是否是顺丰
        if logistics_number.find("SF") == 0:
            logistics_number = f"{logistics_number}:{order_model['phone'][-4:]}"

        appcode = config.get_value("logistics_appcode")
        url = config.get_value("logistics_url")
        headers = {
            'Authorization': 'APPCODE ' + appcode
        }
        param = {
            "no": logistics_number
        }

        ret = requests.get(url, headers=headers,data=param)
        # 验证物流接口意外错误
        if ret.status_code != 200:
            msg = ret.headers.get('X-Ca-Error-Message')
            self.logger_error.error(f"logistics_number:{logistics_number}查询错误：{msg}")
            return self.reponse_json_error("查询失败[001]")
            
        ret_json = json.loads(ret.text)

        if ret_json["status"] == "0":
            # 查询成功
            ret_data = {
                "company": ret_json["result"]["expName"],
                "number": ret_json["result"]["number"].split(':')[0],
                "data": ret_json["result"]["list"]
            }
            self.redis_init.set(order_id, json.dumps(ret_data), ex = 3600)
            return self.reponse_json_success(ret_data)
        else:
            # 查询失败
            self.logger_error.error(f"order_id:{order_id},logistics_number:{logistics_number},error:{ret.text}")
            return self.reponse_json_error("查询失败[002]")



            
            

            
            
            
        



        


        
   
        

        