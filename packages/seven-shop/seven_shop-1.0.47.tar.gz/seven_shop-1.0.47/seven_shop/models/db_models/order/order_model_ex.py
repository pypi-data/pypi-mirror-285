# -*- coding: utf-8 -*-
"""
:Author: Kangwenbin
:Date: 2021-12-02 19:39:04
:LastEditTime: 2024-06-14 10:38:21
:LastEditors: KangWenBin
:Description: 
"""

from seven_shop.models.db_models.order.order_model import *

class OrderModelEx(OrderModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key=db_connect_key, sub_table=sub_table, db_transaction=db_transaction, context=context)

  
    def get_order_list(self, where='', page_index = 0, page_size = 10, params=None):
        """
        :description: 获取订单列表
        :last_editors: Kangwenbin
        """        
        has_more = False
        condition = ""
        if where:
            condition += f"where {where}"

        limit = f" limit {(page_index)*page_size},{page_size + 1}"

        sql = f"SELECT a.order_id,a.shop_id,a.add_time,(a.real_pay_price-a.postage) real_pay_price,a.coin_pay_price,a.status,a.buy_count,a.logistics_number,a.is_refund FROM order_tb a JOIN order_goods_tb b ON a.order_id = b.order_id {condition} {limit}"
        row_list =  self.db.fetch_all_rows(sql,params)
        if len(row_list) == page_size + 1:
            has_more = True
            row_list = row_list[:-1]
        return row_list,has_more
