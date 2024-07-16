# -*- coding: utf-8 -*-
"""
:Author: Kangwenbin
:Date: 2021-12-06 14:07:02
:LastEditTime: 2024-06-12 14:50:34
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop.models.db_models.order.order_refund_model import *

class OrderRefundModelEx(OrderRefundModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key=db_connect_key, sub_table=sub_table, db_transaction=db_transaction, context=context)

    


        




