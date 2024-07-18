# -*- coding: utf-8 -*-
"""
:Author: Kangwenbin
:Date: 2021-12-02 21:16:08
:LastEditTime: 2024-06-12 14:50:44
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop.models.db_models.shop.shop_model import *
from seven_shop.models.db_models.shop.shop_postage_model import *

class ShopModelEx(ShopModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key=db_connect_key, sub_table=sub_table, db_transaction=db_transaction, context=context)

    def get_postage(self, province_name,shop_id):
        postage = -1
        shop_model = self.get_dict_by_id(shop_id,"postage_type,postage,status")
        if shop_model:
            if shop_model["postage_type"] == 0:
                # 邮费类型 0 统一配置 1 指定配送区域不包邮
                postage = shop_model["postage"]
            else:
                # 查询当前地区是否不包邮
                shop_postage_model = ShopPostageModel().get_dict(where="province_name = %s",params=province_name,field="postage")
                if shop_postage_model:
                    postage = shop_postage_model["postage"]
                else:
                    postage = 0
        return postage
    
    def get_pay_wait_time(self,shop_id):
        """
        :description: 获取店铺支付超时时间
        :last_editors: KangWenBin
        """        
        ret = 15
        shop_model = self.get_dict_by_id(shop_id,"wait_pay_time")
        if shop_model:
            ret = shop_model["wait_pay_time"]
        return ret
    
