# -*- coding: utf-8 -*-
"""
:Author: Kangwenbin
:Date: 2021-11-29 20:24:36
:LastEditTime: 2024-07-01 14:15:42
:LastEditors: KangWenBin
:Description: 
"""

from seven_shop.handlers.seven_base import *
from seven_shop.models.db_models.goods.goods_model_ex import *
from seven_shop.models.db_models.cart.cart_model_ex import *

class UserCartManageHandler(SevenBaseHandler):
    @filter_check_params(["user_code","shop_id"])
    def get_async(self):
        """
        :description: 用户购物车列表
        :last_editors: Kangwenbin
        """        
        page_index = int(self.request_params.get("page_index",0))
        page_size = int(self.request_params.get("page_size",10))
        user_code = self.request_params["user_code"]
        shop_id = self.request_params["shop_id"]
        
        
        ret_list = []
        user_cart_list,has_next = CartModelEx().get_user_cart_page_list(user_code,shop_id,page_index,page_size)
        if user_cart_list:
            # 数据整理
            for item in user_cart_list:
                cart_info = {
                    "id": item["id"],
                    "goods_id":item["goods_id"],
                    "goods_name": item["goods_short_name"],
                    "sku_id": item["sku_id"],
                    "sku_name": "" if item["sku_id"] == 0 else item["sku_name"],
                    "buy_count": item["buy_count"],
                    "price": item["goods_price"] if item["sku_id"] == 0 else item["sku_price"],
                    "total_price":item["goods_price"]*item["buy_count"] if item["sku_id"] == 0 else item["sku_price"]*item["buy_count"],
                    "inventory": item["inventory"],
                    "goods_picture": "",
                    "goods_status": 0, # 商品状态 0 异常 1 正常     控制商品失效状态
                    "sku_status": 0 # sku状态 0 异常 1 正常        控制sku重选状态
                }
                # 商品图处理
                if item["sku_id"] > 0:
                    cart_info["goods_picture"] = item["sku_picture"]
                else:
                    try:
                        cart_info["goods_picture"] = json.loads(item["goods_main_images"])[0]
                    except:
                        cart_info["goods_picture"] = ""

                # 商品状态验证
                if item["goods_status"] == 1:
                    cart_info["goods_status"] = 1
                    # sku状态验证
                    if item["sku_status"] == 1:
                        cart_info["sku_status"] = 1
                
                ret_list.append(cart_info)

        ret_data = {
            "model_list": ret_list,
            "has_next": has_next
        }

        self.reponse_json_success(ret_data)

    @filter_check_params(["user_code","goods_id","buy_count","shop_id"])
    def post_async(self):
        """
        :description: 添加/修改购物车
        :last_editors: Kangwenbin
        """        
        user_code = self.request_params["user_code"]
        cart_id = int(self.request_params.get("cart_id",0)) # 0 新增 1 修改
        goods_id = self.request_params["goods_id"]
        sku_id = int(self.request_params.get("sku_id",0))
        buy_count = self.request_params["buy_count"]
        shop_id = self.request_params["shop_id"]
        
        # 获取购物车信息

        cart_conn = CartModelEx()
        
        price = 0
        # 先获取商品信息
        goods_model = GoodsModel().get_dict_by_id(goods_id,"price,status,shop_id")
        if goods_model and goods_model["status"] == 1:
            price = goods_model["price"]
        else:
            return self.reponse_json_error("商品已失效")
        
        if goods_model and goods_model["shop_id"] != shop_id:
            return self.reponse_json_error("商品归属异常")
        
        
        if sku_id > 0:
            sku_model = GoodsSkuModel().get_dict_by_id(sku_id,"price,status")
            if sku_model and sku_model["status"] == 1:
                price = sku_model["price"]
            else:
                return self.reponse_json_error("sku已失效")
            
        if price <= 0:
            return self.reponse_json_error("商品价格异常")
        
        # 获取库存信息
        inventory = 0
        inventory_model = InventoryModel().get_dict(where="goods_id = %s and sku_id = %s",params=[goods_id,sku_id],field="inventory")
        if inventory_model:
            inventory = inventory_model["inventory"]

        if cart_id:
            # 验证库存
            if buy_count > inventory:
                return self.reponse_json_error("库存不足")
            
            # 修改购物车
            cart_model = cart_conn.get_dict(where="user_code = %s and goods_id = %s and sku_id = %s and id != %s", params=[user_code,goods_id,sku_id,cart_id],field="id")
            if cart_model:
                # 存在则合并数据(删除旧的)
                cart_conn.del_entity(where="id = %s",params=cart_model["id"])
            # 修改数据
            if cart_conn.update_table("buy_count = %s,add_time = %s,price = buy_count * %s,sku_id = %s","id = %s",[buy_count,TimeHelper.get_now_timestamp(),price,sku_id,cart_id]):
                return self.reponse_json_success(desc="更新成功",data= None if not cart_model else cart_model["id"])
            return self.reponse_json_error("更新失败")
        else:
            # 新增购物车
            cart_model = cart_conn.get_dict(where="user_code = %s and goods_id = %s and sku_id = %s",params=[user_code,goods_id,sku_id],field="id,buy_count")
            # 如果之前的goods_sku组合已存在，那么直接添加数量，并且修改添加时间
            if cart_model:
                # 验证库存
                if buy_count + cart_model["buy_count"] > inventory:
                    return self.reponse_json_error("商品加购件数（含已加购件数）已超过库存")
                if cart_conn.update_table("buy_count = buy_count + %s,add_time = %s,price = buy_count * %s","id = %s",[buy_count,TimeHelper.get_now_timestamp(),price,cart_model["id"]]):
                    return self.reponse_json_success(desc="添加成功")
            else:
                # 验证库存
                if buy_count > inventory:
                    return self.reponse_json_error("库存不足")
                # 直接添加
                cart_entity = Cart()
                cart_entity.user_code = user_code
                cart_entity.goods_id = goods_id
                cart_entity.sku_id = sku_id
                cart_entity.buy_count = buy_count
                cart_entity.price = buy_count * price 
                cart_entity.add_time = TimeHelper.get_now_timestamp()
                result = cart_conn.add_entity(cart_entity)
                if result:
                    return self.reponse_json_success(desc="添加成功")
                
            return self.reponse_json_success(desc="添加失败")
        
        

        
    @filter_check_params(["user_code","cart_id_list"])
    def delete_async(self):
        """
        :description: 删除购物车物品
        :last_editors: Kangwenbin
        """      
        user_code = self.request_params["user_code"]
        cart_id_list = self.request_params["cart_id_list"]
        if CartModelEx().del_entity(where="user_code = %s and id in %s",params=[user_code,cart_id_list]):
            return self.reponse_json_success(desc="删除成功")
        self.reponse_json_error("删除失败")
        

class CartCountHandler(SevenBaseHandler):
    @filter_check_params(["user_code","shop_id"])
    def get_async(self):
        """
        :description: 购物车数量
        :last_editors: KangWenBin
        """        
        user_code = self.request_params["user_code"]
        shop_id = self.request_params["shop_id"]
        
        cart_count = CartModelEx().get_user_cart_count(user_code,shop_id)
        ret_data = {
            "cart_count": cart_count
        }
        self.reponse_json_success(ret_data)