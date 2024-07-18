# -*- coding: utf-8 -*-
"""
:Author: Kangwenbin
:Date: 2021-11-19 14:21:40
:LastEditTime: 2024-07-05 14:56:45
:LastEditors: KangWenBin
:Description: 
"""

from seven_shop.handlers.seven_base import *
from seven_shop.models.db_models.goods.goods_model_ex import *
from seven_shop.models.db_models.shop.shop_series_model import *

class GoodsListHandler(SevenBaseHandler):
    @filter_check_params(["series_id","sort_type","shop_id"])
    def get_async(self):
        """
        :description: 获取商品列表
        :last_editors: KangWenBin
        """      
        shop_id = self.request_params["shop_id"]
        series_id = int(self.request_params["series_id"])
        sort_type = int(self.request_params["sort_type"]) # 0 综合 1 销量 2 新品 3 价格
        sort_by = int(self.request_params.get("sort_by",1)) # 0 升序 1 降序
        page_index = int(self.request_params.get("page_index",0))
        page_size = int(self.request_params.get("page_size",10))

        # 验证当前分类状态
        if series_id:
            series_model = ShopSeriesModel().get_dict(where="id = %s and shop_id = %s",params=[series_id,shop_id],field="status")
            if not series_model or series_model["status"] != 1:
                return self.reponse_json_error("系列异常")
        
        goods_list,is_next = GoodsModelEx().get_series_goods_list(series_id,shop_id,sort_type,sort_by,page_index,page_size)
        
        ret_data = {
            "model_list": goods_list,
            "is_next": is_next
        }
        self.reponse_json_success(ret_data)


class GoodsInfoHandler(SevenBaseHandler):
    @filter_check_params(["goods_id","shop_id"])
    def get_async(self):
        """
        :description: 
        :param 获取商品详情 
        :last_editors: Kangwenbin
        """        
        goods_id = int(self.request_params["goods_id"])
        shop_id = self.request_params["shop_id"] 

        # 获取商品相关信息
        goods_model = GoodsModelEx().get_goods_model(goods_id,shop_id)
        if not goods_model["goods_info"]:
            return self.reponse_json_error("无法获取商品信息")
        
        # 获取相关库存信息
        goods_model = InventoryModelEx().goods_inventory(goods_model)
        self.reponse_json_success(goods_model)


class SkuInfoHandler(SevenBaseHandler):
    @filter_check_params(["goods_id","shop_id"])
    def get_async(self):
        """
        :description: 获取商品sku信息
        :last_editors: Kangwenbin
        """        
        goods_id = self.request_params["goods_id"]
        shop_id = self.request_params["shop_id"]

        goods_conn = GoodsModelEx()
        goods_model = goods_conn.get_dict(where="id = %s and shop_id = %s",params=[goods_id,shop_id], field="status, goods_long_name,goods_main_images,original_price,price")

        # 验证商品信息
        if not goods_model or goods_model["status"] != 1:
            return self.reponse_json_error("商品已失效")
        
        # 获取商品sku信息
        inventory_conn = InventoryModelEx()
        sku_list = GoodsSkuModelEx().get_goods_sku(goods_id)
        sku_list = inventory_conn.sku_inventory(goods_id,sku_list)
        sku_list["goods_long_name"] = goods_model["goods_long_name"]
        sku_list["goods_picture"] = goods_conn.get_goods_picture(goods_model["goods_main_images"])
        if not sku_list["sku_list"]:
            sku_list["price"] = goods_model["price"]
            sku_list["original_price"] = goods_model["original_price"]
            sku_list["inventory"] = inventory_conn.get_inventory(goods_id,0)

        self.reponse_json_success(sku_list)


class GoodsSearchHandler(SevenBaseHandler):
    @filter_check_params(["search_word","shop_id"])
    def get_async(self):
        """
        :description: 商品搜索
        :last_editors: KangWenBin
        """        
        search_word = self.request_params["search_word"]
        shop_id = self.request_params["shop_id"]
        page_index = int(self.request_params.get("page_index",0))
        page_size = int(self.request_params.get("page_size",8))
        goods_list,is_next = GoodsModelEx().get_dict_page_list(field="id,goods_short_name as goods_name,goods_remark,goods_main_images as goods_picture,original_price,price",page_index=page_index,page_size=page_size,where="status=1 and shop_id = %s and (goods_short_name like %s or goods_long_name like %s)",params=[shop_id,f"%{search_word}%",f"%{search_word}%"],order_by="sort desc",page_count_mode="next")
        if goods_list:
            for item in goods_list:
                try:
                    item["goods_picture"] = json.loads(item["goods_picture"])[0]
                except:
                    item["goods_picture"] = ""
                
        ret_data = {
            "model_list": goods_list,
            "is_next":is_next
        }

        self.reponse_json_success(ret_data)


class GoodsDetailListHandler(SevenBaseHandler):
    @filter_check_params(["goods_id_list","shop_id"])
    def post_async(self):
        """
        :description: 根据id获取商品详情
        :last_editors: KangWenBin
        """
        goods_id_list = self.request_params["goods_id_list"]
        shop_id = self.request_params["shop_id"]
        goods_list = GoodsModelEx().get_dict_list(field="id,goods_short_name as goods_name,goods_remark,goods_main_images as goods_picture,price",where="status=1 and id in %s and shop_id = %s",params=(goods_id_list,shop_id),order_by="sort desc")
        if goods_list:
            for item in goods_list:
                try:
                    item["goods_picture"] = json.loads(item["goods_picture"])[0]
                except:
                    item["goods_picture"] = ""
                    
        self.reponse_json_success(goods_list)   


class GoodsRecommentListHandler(SevenBaseHandler):
    @filter_check_params(["shop_id"])
    def get_async(self):
        """
        :description: 获取推荐商品列表
        :last_editors: KangWenBin
        """      
        shop_id = self.request_params["shop_id"]
        page_index = int(self.request_params.get("page_index",0))
        page_size = int(self.request_params.get("page_size",10))

        goods_list,is_next = GoodsModelEx().get_recommend_goods_list(shop_id,page_index,page_size)
        
        ret_data = {
            "model_list": goods_list,
            "is_next": is_next
        }
        self.reponse_json_success(ret_data)


