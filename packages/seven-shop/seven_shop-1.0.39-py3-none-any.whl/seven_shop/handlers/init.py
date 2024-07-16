# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-06-06 16:29:52
:LastEditTime: 2024-06-18 17:02:32
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop.handlers.seven_base import *
from seven_shop.models.db_models.shop.shop_model import *

class InitHandler(SevenBaseHandler):
    @filter_check_params(["shop_id"])
    def get_async(self):
        """
        :description: 获取店铺默认配置
        :last_editors: KangWenBin
        """
        shop_id = self.request_params["shop_id"]
        shop_model = ShopModel().get_dict_by_id(shop_id,"wait_pay_time,logistics_time,consignee,phone,address_info,shipping_method,remark,coupon_remark,refund_audit")
        if not shop_model:
            return self.reponse_json_error("初始化信息异常")
        self.reponse_json_success(shop_model)
