# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-05-08 16:12:39
:LastEditTime: 2024-06-04 16:51:23
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop.models.db_models.cart.cart_model import *

class CartModelEx(CartModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key, sub_table, db_transaction, context)

    def get_user_cart_page_list(self,user_code,shop_id,page_index,page_size):
        """
        :description: 获取用户购物车列表
        :param user_code 用户标识
        :param page_index 
        :param page_size 
        :last_editors: KangWenBin
        """        
        has_next = 0
        limit = f"limit {(page_index)*page_size},{page_size+1}"

        sql = f'''SELECT a.id,a.goods_id,b.goods_short_name,a.sku_id,c.sku_name,a.buy_count,b.price AS goods_price,c.price AS sku_price,
            b.status as goods_status,c.status as sku_status,d.inventory,b.goods_main_images,c.sku_picture FROM cart_tb a JOIN goods_tb b ON a.goods_id = b.id LEFT JOIN
              goods_sku_tb c ON a.sku_id = c.id LEFT JOIN inventory_tb d ON a.goods_id = d.goods_id AND a.sku_id=d.sku_id WHERE a.user_code = %s and b.shop_id = %s 
              ORDER BY a.add_time Desc {limit}'''
        ret_list = self.db.fetch_all_rows(sql,[user_code, shop_id])
        if len(ret_list) == page_size + 1:
            ret_list = ret_list[:-1]
            has_next = 1
        return ret_list,has_next
    
    def get_user_cart_count(self,user_code,shop_id):
        """
        :description: 获取用户购物车数量
        :param user_code 用户标识
        :param shop_id 店铺标识
        :last_editors: KangWenBin
        """
        sql = f'''SELECT COUNT(*) as count FROM cart_tb a left join goods_tb b on a.goods_id = b.id WHERE a.user_code = %s and b.shop_id = %s'''
        
        return self.db.fetch_one_row(sql,[user_code,shop_id])["count"]
        
