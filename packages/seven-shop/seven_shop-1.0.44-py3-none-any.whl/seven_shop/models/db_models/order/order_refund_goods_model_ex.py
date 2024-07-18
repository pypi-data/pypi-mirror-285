# -*- coding: utf-8 -*-
"""
:Author: Kangwenbin
:Date: 2021-12-06 14:33:16
:LastEditTime: 2024-05-14 15:52:14
:LastEditors: KangWenBin
:Description: 
"""

from seven_shop.models.db_models.order.order_refund_goods_model import *

class OrderRefundGoodsModelEx(OrderRefundGoodsModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key=db_connect_key, sub_table=sub_table, db_transaction=db_transaction, context=context)



    