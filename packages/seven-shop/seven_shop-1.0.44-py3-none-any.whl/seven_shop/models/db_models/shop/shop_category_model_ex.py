# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-05-16 16:41:18
:LastEditTime: 2024-06-04 16:19:28
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop.models.db_models.shop.shop_category_model import *


class ShopCategoryModelEx(ShopCategoryModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key, sub_table, db_transaction, context)

    def get_category_series_list(self,category_id,shop_id,page_index,page_size):
        """
        :description: 获取分类对应系列列表
        :last_editors: KangWenBin
        """        
        is_next = False
        limit = f"limit {(page_index)*page_size},{page_size+1}"
        sql = f"SELECT b.id,b.series_picture,b.series_poster,b.series_name FROM shop_category_series_tb a JOIN shop_series_tb b ON a.series_id = b.id WHERE a.category_id = %s and b.status = 1 and b.shop_id = %s order by sort desc {limit}"
        series_list = self.db.fetch_all_rows(sql,[category_id,shop_id])
        if len(series_list) == page_size + 1:
            series_list = series_list[:-1]
            is_next = True

        return series_list,is_next