# -*- coding: utf-8 -*-
"""
:Author: Kangwenbin
:Date: 2021-11-22 19:28:39
:LastEditTime: 2024-06-12 14:50:13
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop.models.db_models.goods.goods_sku_model import *
from seven_shop.models.db_models.inventory.inventory_model_ex import *

class GoodsSkuModelEx(GoodsSkuModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key, sub_table, db_transaction, context)

    def get_goods_sku(self, goods_id):
        """
        :description: 获取商品sku信息
        :param goods_id 商品id
        :last_editors: Kangwenbin
        """        
        ret_model = {
            "sku_list": [],
            "sku_model": {},
            "price": 0,
            "original_price": 0
        }
        goods_sku_list = self.get_dict_list(where = "goods_id = %s and status = 1 ", params = goods_id)
        if goods_sku_list:

            # sku信息处理
            min_price_dict = min(goods_sku_list, key=lambda x: x["price"])
            ret_model["price"] = min_price_dict["price"]
            ret_model["original_price"] = min_price_dict["original_price"]

            for item in goods_sku_list:
                # 不存在sku细项则跳过
                if not item["sku_info"]:
                    continue

                json_sku_list = json.loads(item["sku_info"])
                # 选择项处理
                for sku in json_sku_list:
                    if sku["model_name"] not in ret_model["sku_model"]:
                        ret_model["sku_model"][sku["model_name"]] = []

                    if sku["model_value"] not in ret_model["sku_model"][sku["model_name"]]:
                        ret_model["sku_model"][sku["model_name"]].append(sku["model_value"])

                sku_model = {
                    "sku_name": item["sku_name"],
                    "id": item["id"],
                    "price": item["price"],
                    "original_price":item["original_price"],
                    "integral":item["integral"],
                    "sku_picture": item["sku_picture"],
                    "sku_info": json_sku_list,
                }
                ret_model["sku_list"].append(sku_model)
                
        return ret_model
                        


                        
                    

