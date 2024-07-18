# -*- coding: utf-8 -*-
"""
:Author: Kangwenbin
:Date: 2021-11-22 18:36:29
:LastEditTime: 2024-06-07 15:23:45
:LastEditors: KangWenBin
:Description: 
"""

from seven_shop.models.db_models.goods.goods_model import *
from seven_shop.models.db_models.goods.goods_sku_model_ex import *


class GoodsModelEx(GoodsModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key, sub_table, db_transaction, context)

    def get_goods_model(self, goods_id, shop_id):
        """
        :description: 商品详情
        :param goods_id 商品id
        :param shop_id 店铺id
        :last_editors: Kangwenbin
        """
        ret_model = {
            "goods_info": None,
            "sku_info": None
        }
        goods_model = self.get_dict(where = "id = %s and shop_id = %s and status = 1",params = [goods_id,shop_id], field = "id,goods_main_images,goods_detail_images,goods_long_name,goods_short_name,goods_parameter,original_price,price,integral,is_integral,goods_service")
        if goods_model:
            goods_model["goods_main_images"] = [] if not goods_model["goods_main_images"] else json.loads(goods_model["goods_main_images"])
            goods_model["goods_detail_images"] = [] if not goods_model["goods_detail_images"] else json.loads(goods_model["goods_detail_images"])
            goods_model["goods_parameter"] = [] if not goods_model["goods_parameter"] else json.loads(goods_model["goods_parameter"])  
            goods_model["goods_service"] = [] if not goods_model["goods_service"] else json.loads(goods_model["goods_service"])  
            
            ret_model["goods_info"] = goods_model

            # 获取sku信息
            sku_info = GoodsSkuModelEx().get_goods_sku(goods_id)
            ret_model["sku_info"] = {
                "sku_list": sku_info["sku_list"],
                "sku_model": sku_info["sku_model"]
            }
            if sku_info["price"] > 0:
                # 验证是否sku价格
                goods_model["original_price"] = sku_info["original_price"]
                goods_model["price"] = sku_info["price"]

        return ret_model

    def get_series_goods_list(self,series_id,shop_id,sort_type,sort_by,page_index,page_size):
        """
        :description: 获取分类商品列表
        :param category_id 分类id 0 全部
        :param sort_type 排序类型 0 综合 1 销量 2 新品 3 价格
        :param sort_by 0 升序 1 降序
        :param page_index 页码
        :param page_size 
        :last_editors: KangWenBin
        """        
        is_next = False
        limit = f"limit {(page_index)*page_size},{page_size+1}"

        order_by = "order by sort desc"
        if sort_type == 1:
            order_by = "order by goods_sold desc"
        elif sort_type == 2:
            order_by = "order by add_time desc"
        elif sort_type == 3:
            order_by = f"order by price {'desc' if sort_by == 1 else 'asc'}"
        
        condition = " and shop_id = %s"
        param_list = [shop_id]
        if series_id > 0:
            condition += f" and series_id = %s"
            param_list.append(series_id)
        
        
        sql = f"SELECT id,goods_main_images as goods_picture,goods_short_name,goods_remark,price FROM goods_tb WHERE status = 1 and is_integral = 0 {condition} {order_by} {limit}"
        goods_list = self.db.fetch_all_rows(sql,param_list)
        if goods_list:
            goods_list = [{**item, 'goods_picture': self.get_goods_picture(item['goods_picture'])} for item in goods_list]
        else:
            goods_list = []
        
        if len(goods_list) == page_size + 1:
            goods_list = goods_list[:-1]
            is_next = True

        return goods_list,is_next
                
    def get_goods_picture(self,goods_main_images):
        """
        :description: 多张主图获取首张作为列表图
        :param goods_main_images 商品主图json
        :last_editors: KangWenBin
        """        
        ret = ""
        try:
            ret = json.loads(goods_main_images)[0]
        except:
            ret = ""
        return ret

    def get_buy_goods_info(self,shop_id,goods_id,sku_id,buy_count):
        """
        :description: 订单商品信息
        :param shop_id 店铺id
        :param goods_id 商品id
        :param sku_id sku_id
        :last_editors: KangWenBin
        """        
        ret_data = {
            "goods_id":goods_id,
            "goods_name": "",
            "sku_id":sku_id,
            "sku_name": "",
            "goods_picture": "",
            "goods_code": "",
            "price": 0,
            "buy_count": buy_count,
            "total_price":0,
            "goods_status": 0,
            "sku_status": 0,
            "status": 0,
            "inventory_status": 0,
            "coupon_id": 0,
            "coupon_price": 0
        }
        goods_status = 1
        sku_status = 1
        goods_model = self.get_dict(where="id = %s and shop_id = %s",params=[goods_id,shop_id],field= "goods_main_images,goods_long_name,price,status,goods_code")
        if goods_model:
            goods_status = goods_model["status"]
            ret_data["goods_status"] = goods_model["status"]
            ret_data["goods_name"] = goods_model["goods_long_name"]
            try:
                ret_data["goods_picture"] = json.loads(goods_model["goods_main_images"])[0]
            except:
                pass
            ret_data["price"] = goods_model["price"]
            ret_data["goods_code"] = goods_model["goods_code"]
            if sku_id:
                # 获取sku信息
                sku_model = GoodsSkuModel().get_dict_by_id(sku_id,"sku_name,status,sku_picture,price,goods_code")
                if not sku_model:
                    return None
                
                sku_status = sku_model["status"]
                ret_data["sku_status"] = sku_model["status"]
                ret_data["sku_name"] = sku_model["sku_name"]
                ret_data["goods_picture"] = sku_model["sku_picture"]
                ret_data["price"] = sku_model["price"]
                ret_data["goods_code"] = sku_model["goods_code"]
        else:
            return None
        ret_data["status"] = 1 if goods_status == 1 and sku_status == 1 else 0
        ret_data["total_price"] = ret_data["price"] * ret_data["buy_count"]
        # 验证库存
        if ret_data["status"] == 1:
            inventory = InventoryModelEx().get_inventory(goods_id, sku_id)
            if buy_count <= inventory:
                ret_data["inventory_status"] = 1
        return ret_data
    
    def get_recommend_goods_list(self,shop_id,page_index,page_size):
        """
        :description: 获取推荐商品列表
        :param shop_id 店铺id
        :param page_index 页码
        :param page_size 
        :last_editors: KangWenBin
        """        
        is_next = False
        limit = f"limit {(page_index)*page_size},{page_size+1}"
        
        sql = f"SELECT a.id,a.goods_main_images as goods_picture,a.goods_short_name,a.goods_remark,a.price FROM goods_tb a join goods_recommend_tb b on a.id = b.goods_id WHERE a.status = 1 and a.shop_id = %s order by a.sort desc {limit}"
        goods_list = self.db.fetch_all_rows(sql,shop_id)
        if goods_list:
            goods_list = [{**item, 'goods_picture': self.get_goods_picture(item['goods_picture'])} for item in goods_list]
        else:
            goods_list = []
        
        if len(goods_list) == page_size + 1:
            goods_list = goods_list[:-1]
            is_next = True

        return goods_list,is_next
        









        



        
