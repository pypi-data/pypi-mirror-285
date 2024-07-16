# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-05-08 09:41:31
:LastEditTime: 2024-06-05 10:23:06
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop.handlers.seven_base import *
from seven_shop.models.db_models.shop.shop_category_model_ex import *

class CategoryListHandler(SevenBaseHandler):
    @filter_check_params(["shop_id"])
    def get_async(self):
        """
        :description: 
        :param 获取商城分类信息 
        :last_editors: Kangwenbin
        """        
        shop_id = self.request_params["shop_id"]
        # 获取商品相关信息
        ret_data = {
            "category_list": []
        }
        category_list = ShopCategoryModel().get_dict_list(where="status = 1 and shop_id = %s",params=shop_id,field="id,category_name",order_by="sort desc",limit="0,5")
        category_list.append({
            "id": 0,
            "category_name": "全部商品"
        })
        ret_data["category_list"] = category_list
        
        # 获取相关库存信息
        self.reponse_json_success(ret_data)


class CategorySeriesListHandler(SevenBaseHandler):
    @filter_check_params(["category_id","shop_id"])
    def get_async(self):
        """
        :description: 获取系列
        :last_editors: KangWenBin
        """      
        category_id = int(self.request_params["category_id"])
        page_index = int(self.request_params.get("page_index",0))
        page_size = int(self.request_params.get("page_size",10))
        shop_id = int(self.request_params["shop_id"])

        # 验证当前分类状态
        category_model = ShopCategoryModel().get_dict(where="id = %s and shop_id = %s",params=[category_id,shop_id],field="status")
        if not category_model or category_model["status"] != 1:
            return self.reponse_json_error("分类异常")
        
        series_list,is_next = ShopCategoryModelEx().get_category_series_list(category_id,shop_id,page_index,page_size)
        
        ret_data = {
            "model_list": series_list,
            "is_next": is_next
        }

        self.reponse_json_success(ret_data)


