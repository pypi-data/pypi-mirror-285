# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-05-28 10:02:20
:LastEditTime: 2024-07-19 18:33:05
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop.handlers.seven_base import *
from seven_shop.models.db_models.coupon.coupon_model_ex import *
from seven_shop.models.db_models.coupon.coupon_record_model import *
from seven_shop.models.db_models.order.order_model import *
from seven_shop.models.db_models.coupon.coupon_goods_model import *
from seven_shop.libs.customize.coupon_helper import *
from seven_shop.libs.customize.order_helper import *

class CouponGrantInfoHandler(SevenBaseHandler):
    @filter_check_params(["user_code","open_id","shop_id"])
    def get_async(self):
        # 获取参数
        user_code = self.request_params["user_code"]
        open_id = self.request_params["open_id"]
        shop_id = self.request_params["shop_id"]
        act_id = str(self.request_params.get("act_id",""))
        ret_data = {
            "coupon_model": None
        }

        coupon_list =  CouponHelper.get_user_grant_coupon(user_code, open_id, shop_id, act_id)
        if coupon_list: 
            # 验证可领取的列表
            coupon_list = [x for x in coupon_list if x["user_receive"] == 0]
            if coupon_list:
                ret_data["coupon_model"] = {
                    "grant_id": coupon_list[0]["grant_id"],
                    "coupon_name": coupon_list[0]["coupon_name"],
                    "coupon_type": coupon_list[0]["coupon_type"],
                    "coupon_price": self.strip_trailing_zeros(coupon_list[0]["coupon_price"]),
                    "grant_picture": coupon_list[0]["grant_picture"],
                    "coupon_discount": self.strip_trailing_zeros(coupon_list[0]["coupon_discount"]),
                    "use_price": self.strip_trailing_zeros(coupon_list[0]["use_price"]),
                    "begin_time": coupon_list[0]["begin_time"],
                    "end_time": coupon_list[0]["end_time"]
                }

        return self.response_json_success(ret_data)

    @filter_check_params(["user_code","open_id","shop_id","grant_id"])
    def post_async(self):
        # 获取参数
        user_code = self.request_params["user_code"]
        open_id = self.request_params["open_id"]
        shop_id = self.request_params["shop_id"]
        grant_id = self.request_params["grant_id"]
        act_id = str(self.request_params.get("act_id",""))

        if self.is_continue_request(f"{user_code}_{act_id}_{shop_id}_coupon_grant_info",3000):
            return self.response_json_error(desc="操作太频繁，请稍后再试")
        
        # 验证用户是否是黑名单
        user_info = UserHelper.get_user_info(act_id,open_id)
        if not user_info:
            return self.response_json_error("无法获取用户信息")
        if user_info["user_state"] == 1:
            # 黑名单无法下单
            return self.response_json_error("用户账号异常\r\n请咨询客服处理")

        coupon_list =  CouponHelper.get_user_grant_coupon(user_code, open_id, shop_id, act_id)

        coupon_model = [x for x in coupon_list if x["grant_id"] == grant_id]
        if not coupon_model:
            return self.response_json_error("该优惠券投放活动已下架")
        
        coupon_model = coupon_model[0]
        # 判断是否已领取
        if coupon_model["user_receive"] == 1:
            return self.response_json_error("当前优惠券已领取")

        # 获取优惠卷限制商品
        goods_list = CouponGoodsModel(context=self).get_dict_list(where="coupon_id = %s", params=coupon_model["id"])

        coupon_conn = CouponModelEx()
        add_result = 0

        # 优惠券发放
        try:
            if coupon_conn.update_coupon_inventory(coupon_model["id"]):
                record_entity = CouponRecord()
                record_entity.shop_id = shop_id
                record_entity.grant_id = coupon_model["grant_id"]
                record_entity.coupon_id = coupon_model["id"]
                record_entity.use_price = coupon_model["use_price"]
                record_entity.goods_limit = coupon_model["goods_limit"]
                record_entity.begin_time = coupon_model["begin_time"]
                record_entity.end_time = coupon_model["end_time"]
                record_entity.user_code = user_code
                record_entity.act_id = act_id
                record_entity.coupon_info = JsonHelper.json_dumps({
                    "coupon_name": coupon_model["coupon_name"],
                    "coupon_type": coupon_model["coupon_type"],
                    "coupon_price": str(coupon_model["coupon_price"]),
                    "coupon_discount": str(coupon_model["coupon_discount"]),
                    "using_rule": coupon_model["using_rule"],
                })
                record_entity.goods_list = json.dumps([x["goods_id"] for x in goods_list if x["coupon_id"] == coupon_model["id"]])
                record_entity.add_time = TimeHelper.get_now_timestamp()
                record_entity.coupon_source = 1
                add_result = CouponRecordModel(context=self).add_entity(record_entity)
            else:
                return self.response_json_error("抱歉~来晚啦\r\n优惠券已领完")
        except:
            self.logger_error.error(f"发放优惠券失败,优惠券信息：{coupon_model}，错误信息：{traceback.format_exc()}")
        finally:
            # 优惠券库存效验
            coupon_conn.check_coupon_inventory(coupon_model["id"])

        if add_result:
            return self.response_json_success(desc="领取成功")
        
        self.response_json_error("领取失败")
    

class CouponGrantListHandler(SevenBaseHandler):
    @filter_check_params(["user_code","open_id","shop_id"])
    def get_async(self):
        # 获取参数
        user_code = self.request_params["user_code"]
        open_id = self.request_params["open_id"]
        shop_id = self.request_params["shop_id"]
        act_id = str(self.request_params.get("act_id",""))
        ret_data = {
            "coupon_list": []
        }

        coupon_list =  CouponHelper.get_user_grant_coupon(user_code, open_id, shop_id, act_id)
        if coupon_list:
            for item in coupon_list:
                ret_data["coupon_list"].append({
                    "coupon_name": item["coupon_name"],
                    "coupon_type": item["coupon_type"],
                    "coupon_price": self.strip_trailing_zeros(item["coupon_price"]),
                    "coupon_discount": self.strip_trailing_zeros(item["coupon_discount"]),
                    "use_price": self.strip_trailing_zeros(item["use_price"]),
                    "begin_time": item["begin_time"],
                    "end_time": item["end_time"],
                    "user_receive": item["user_receive"],
                    "using_rule": item["using_rule"],
                    "inventory_status": 1 if item["coupon_inventory"] - item["record_number"] > 0 else 0 
                })

        return self.response_json_success(ret_data)

    @filter_check_params(["user_code","open_id","shop_id"])
    def post_async(self):
        # 获取参数
        user_code = self.request_params["user_code"]
        open_id = self.request_params["open_id"]
        shop_id = self.request_params["shop_id"]
        act_id = str(self.request_params.get("act_id",""))
       
        ret_data = {
            "coupon_list": []
        }

        if self.is_continue_request(f"{user_code}_{act_id}_{shop_id}_coupon_grant",3000):
            return self.response_json_error(desc="操作太频繁，请稍后再试")
        
        # 验证用户是否是黑名单
        user_info = UserHelper.get_user_info(act_id,open_id)
        if not user_info:
            return self.response_json_error("无法获取用户信息")
        if user_info["user_state"] == 1:
            # 黑名单无法下单
            return self.response_json_error("用户账号异常\r\n请咨询客服处理")
        
        coupon_list =  CouponHelper.get_user_grant_coupon(user_code, open_id, shop_id, act_id)
        # 获取用户未领取列表
        coupon_list = [x for x in coupon_list if x["user_receive"] == 0]
        if not coupon_list:
            return self.response_json_success(ret_data)
        
        coupon_ids = [x["id"] for x in coupon_list]
        # 获取所有优惠卷限制商品
        goods_list = CouponGoodsModel(context=self).get_dict_list(where="coupon_id in %s", params=[coupon_ids])

        coupon_conn = CouponModelEx()
        # 判断优惠券类型
        for item in coupon_list:
            # 优惠券发放
            try:
                if coupon_conn.update_coupon_inventory(item["id"]):
                    record_entity = CouponRecord()
                    record_entity.shop_id = shop_id
                    record_entity.grant_id = item["grant_id"]
                    record_entity.coupon_id = item["id"]
                    record_entity.use_price = item["use_price"]
                    record_entity.goods_limit = item["goods_limit"]
                    record_entity.begin_time = item["begin_time"]
                    record_entity.end_time = item["end_time"]
                    record_entity.user_code = user_code
                    record_entity.act_id = act_id
                    record_entity.coupon_info = JsonHelper.json_dumps({
                        "coupon_name": item["coupon_name"],
                        "coupon_type": item["coupon_type"],
                        "coupon_price": str(item["coupon_price"]),
                        "coupon_discount": str(item["coupon_discount"]),
                        "using_rule": item["using_rule"],
                    })
                    record_entity.goods_list = json.dumps([x["goods_id"] for x in goods_list if x["coupon_id"] == item["id"]])
                    record_entity.add_time = TimeHelper.get_now_timestamp()
                    result = CouponRecordModel(context=self).add_entity(record_entity)
                    if result:
                        ret_data["coupon_list"].append({
                            "coupon_name": item["coupon_name"],
                            "coupon_type": item["coupon_type"],
                            "coupon_price": self.strip_trailing_zeros(item["coupon_price"]),
                            "coupon_discount": self.strip_trailing_zeros(item["coupon_discount"]),
                            "use_price": self.strip_trailing_zeros(item["use_price"]),
                            "begin_time": item["begin_time"],
                            "end_time": item["end_time"]
                        })
                
            except:
                self.logger_error.error(f"发放优惠券失败,优惠券信息：{item}，错误信息：{traceback.format_exc()}")
            finally:
                # 优惠券库存效验
                coupon_conn.check_coupon_inventory(item["id"])

        self.response_json_success(ret_data)


class CouponRecordListHandler(SevenBaseHandler):
    @filter_check_params(["user_code","shop_id"])
    def get_async(self, *args, **kwargs):
        """
        :description: 优惠券用户列表
        :last_editors: KangWenBin
        """
        page_index = int(self.request_params.get("page_index",0))
        page_size = int(self.request_params.get("page_size",10))
        coupon_status = int(self.request_params.get("coupon_status",0)) # 0 未使用 1 已使用 2 已过期
        user_code = self.request_params["user_code"]
        act_id = str(self.request_params.get("act_id",""))
        shop_id = self.request_params["shop_id"]

        condition = "user_code = %s and act_id = %s and shop_id = %s"
        param_list = [user_code,act_id,shop_id]

        if coupon_status == 0: # 未使用
            condition += " and end_time > %s and status = 0"
            param_list.append(TimeHelper.get_now_timestamp())
            
        elif coupon_status == 1: # 已使用
            condition += " and status = 1"
            
        elif coupon_status == 2: # 已过期
            condition += " and end_time < %s and status = 0"
            param_list.append(TimeHelper.get_now_timestamp())
        
        coupon_list,is_next = CouponRecordModel(context=self).get_dict_page_list(field="id,coupon_id,coupon_info,use_price,begin_time,end_time",where=condition,params=param_list,page_index=page_index,page_size=page_size,page_count_mode="next",order_by="id desc")
        if coupon_list:
            for item in coupon_list:
                item["coupon_info"] = json.loads(item["coupon_info"])
                item["coupon_name"] = item["coupon_info"]["coupon_name"]
                item["coupon_type"] = item["coupon_info"]["coupon_type"]
                item["coupon_price"] = self.strip_trailing_zeros(item["coupon_info"]["coupon_price"])
                item["coupon_discount"] = self.strip_trailing_zeros(item["coupon_info"]["coupon_discount"])
                item["use_price"] = self.strip_trailing_zeros(item["use_price"])
                item["using_rule"] = item["coupon_info"]["using_rule"]
                # 删除item["coupon_info"]
                del item["coupon_info"]

        ret_data = {
            "model_list": coupon_list,
            "is_next": is_next
        }
        return self.response_json_success(ret_data)


class CouponListHandler(SevenBaseHandler):
    @filter_check_params(["user_code","shop_id"])
    def get_async(self, *args, **kwargs):
        """
        :description: 优惠券列表
        :last_editors: KangWenBin
        """

        user_code = self.request_params["user_code"]
        act_id = str(self.request_params.get("act_id",""))
        shop_id = self.request_params["shop_id"]

        # 获取可领取的商城优惠券
        coupon_list = CouponModel(context=self).get_dict_list(field="id,coupon_name,coupon_type,use_price,coupon_price,coupon_discount,begin_time,end_time,using_rule,coupon_inventory,record_number", where="shop_id = %s and status = 1 and is_receive = 1 and begin_time <= %s and end_time > %s",params=[shop_id,TimeHelper.get_now_timestamp(),TimeHelper.get_now_timestamp()])
        
        # 获取用户已经领过的列表
        if coupon_list:
            coupon_ids = [x["id"] for x in coupon_list]
            user_coupon_record_list = CouponRecordModel(context=self).get_dict_list(field="coupon_id", where="user_code = %s and act_id = %s and shop_id = %s and coupon_id in %s",params=[user_code,act_id,shop_id,coupon_ids])
            for item in coupon_list:
                item["user_receive"] = 1 if [x for x in user_coupon_record_list if x["coupon_id"] == item["id"]] else 0
                item["use_price"] = self.strip_trailing_zeros(item["use_price"])
                item["coupon_price"] = self.strip_trailing_zeros(item["coupon_price"])
                item["coupon_discount"] = self.strip_trailing_zeros(item["coupon_discount"])
                item["inventory_status"] = 1 if item["coupon_inventory"] - item["record_number"] > 0 else 0 
                
        
        ret_data = {
            "coupon_list": coupon_list
        }

        return self.response_json_success(ret_data)


class CouponReceiveHandler(SevenBaseHandler):
    @filter_check_params(["user_code","shop_id","open_id"])
    def post_async(self, *args, **kwargs):
        """
        :description: 领取优惠券
        :last_editors: KangWenBin
        """
        user_code = self.request_params["user_code"]
        act_id = str(self.request_params.get("act_id",""))
        shop_id = self.request_params["shop_id"]
        open_id = self.request_params["open_id"]

        if self.is_continue_request(f"{user_code}_{act_id}_{shop_id}_coupon_receive",3000):
            return self.response_json_error(desc="操作太频繁，请稍后再试")
        
        # 验证用户是否是黑名单
        user_info = UserHelper.get_user_info(act_id,open_id)
        if not user_info:
            return self.response_json_error("无法获取用户信息")
        if user_info["user_state"] == 1:
            # 黑名单无法下单
            return self.response_json_error("用户账号异常\r\n请咨询客服处理")

        ret_data = {
            "receive_list": []
        }

        # 获取可领取的商城优惠券
        coupon_list =  CouponModelEx(context=self).get_receive_coupon_list(user_code,act_id,shop_id)
        if not coupon_list:
            return self.response_json_error(desc="无可领取优惠券")
        
        coupon_ids = [x["id"] for x in coupon_list]
        # 获取所有优惠卷限制商品
        goods_list = CouponGoodsModel(context=self).get_dict_list(where="coupon_id in %s", params=[coupon_ids])

        coupon_conn = CouponModelEx()
        # 判断优惠券类型
        for item in coupon_list:
            # 优惠券发放
            try:
                if coupon_conn.update_coupon_inventory(item["id"]):
                    record_entity = CouponRecord()
                    record_entity.shop_id = shop_id
                    record_entity.grant_id = 0
                    record_entity.coupon_id = item["id"]
                    record_entity.use_price = item["use_price"]
                    record_entity.goods_limit = item["goods_limit"]
                    record_entity.begin_time = item["begin_time"]
                    record_entity.end_time = item["end_time"]
                    record_entity.user_code = user_code
                    record_entity.act_id = act_id
                    record_entity.coupon_info = JsonHelper.json_dumps({
                        "coupon_name": item["coupon_name"],
                        "coupon_type": item["coupon_type"],
                        "coupon_price": str(item["coupon_price"]),
                        "coupon_discount": str(item["coupon_discount"]),
                        "using_rule": item["using_rule"],
                    })
                    record_entity.goods_list = json.dumps([x["goods_id"] for x in goods_list if x["coupon_id"] == item["id"]])
                    record_entity.add_time = TimeHelper.get_now_timestamp()
                    record_entity.coupon_source = 0
                    result = CouponRecordModel(context=self).add_entity(record_entity)
                    if result:
                        ret_data["receive_list"].append(item["id"])
            except:
                self.logger_error.error(f"领取优惠券失败,优惠券信息：{item},错误信息：{traceback.format_exc()}")
            finally:
                # 优惠券库存效验
                coupon_conn.check_coupon_inventory(item["id"])

        self.response_json_success(ret_data)


class CouponOrderListHandler(SevenBaseHandler):
    @filter_check_params(["user_code","buy_list","shop_id"])
    def post_async(self, *args, **kwargs):
        """
        :description: 订单可用优惠券
        :last_editors: KangWenBin
        """
        user_code = self.request_params["user_code"]
        act_id = str(self.request_params.get("act_id",""))
        buy_list = self.request_params["buy_list"]
        shop_id = self.request_params["shop_id"]

        check_result = OrderHelper.order_check(shop_id,buy_list,"",user_code,act_id,0)
        if check_result["result"] == 1:
            goods_list = check_result["data"]["goods_list"]
            # 计算各商品总金额
            goods_total_price_dict = {}
            for item in goods_list:
                goods_total_price_dict[item["goods_id"]] = goods_total_price_dict.get(item["goods_id"],0) + item["total_price"]

            # 获取用户可用优惠券(有效期内优惠券)
            coupon_list = CouponRecordModel(context=self).get_dict_list(where="user_code = %s and status = 0 and begin_time <= %s and end_time > %s and shop_id = %s",params=[user_code,TimeHelper.get_now_timestamp(),TimeHelper.get_now_timestamp(),shop_id],field="id,coupon_id,coupon_info,use_price,begin_time,end_time,goods_limit,goods_list")
            if coupon_list:
                for item in coupon_list:
                    item["coupon_info"] = json.loads(item["coupon_info"])
                    item["coupon_name"] = item["coupon_info"]["coupon_name"]
                    item["coupon_type"] = item["coupon_info"]["coupon_type"]
                    item["coupon_price"] = self.strip_trailing_zeros(item["coupon_info"]["coupon_price"]) 
                    item["coupon_discount"] = self.strip_trailing_zeros(item["coupon_info"]["coupon_discount"])
                    item["using_rule"] = item["coupon_info"]["using_rule"]
                    # 删除item["coupon_info"]
                    del item["coupon_info"]
                    item["use_price"] = self.strip_trailing_zeros(item["use_price"])

                    # 验证商品限制
                    if item["goods_limit"] == 0:
                        # 验证总金额是否满足
                        if check_result["data"]["goods_price"] >= Decimal(item["use_price"]):
                            item["use_status"] = 1
                            continue
                        else:
                            item["use_status"] = 0
                            continue
                    else:
                        # 获取商品交集
                        intersection_list = list(set(json.loads(item["goods_list"])) & set([x["goods_id"] for x in goods_list]))
                        if intersection_list:
                            # 获取交集商品总金额
                            if sum([goods_total_price_dict[x] for x in intersection_list]) >= Decimal(item["use_price"]):
                                item["use_status"] = 1
                                continue
                            else:
                                item["use_status"] = 0
                                continue

                        else:
                            item["use_status"] = 0
                            continue
                        

                ret_data = {
                    "coupon_list": coupon_list
                }  
                return self.response_json_success(ret_data)
            
        self.response_json_success({"coupon_list":[]})