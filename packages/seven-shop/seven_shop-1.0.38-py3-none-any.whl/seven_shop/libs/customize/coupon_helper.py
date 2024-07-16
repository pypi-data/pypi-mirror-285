# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-05-31 15:02:38
:LastEditTime: 2024-06-20 15:31:47
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop.models.db_models.coupon.coupon_goods_model import *
from seven_shop.models.db_models.coupon.coupon_model_ex import *
from seven_shop.models.db_models.coupon.coupon_record_model import *
from seven_shop.models.db_models.order.order_model_ex import *
from seven_shop.models.db_models.order.order_goods_model import *
from seven_shop.models.db_models.order.order_refund_goods_model import *
import seven_framework.config as config


class CouponHelper:

    @classmethod
    def get_user_info(self,act_id,open_id):
        """
        :description: 获取用户信息
        :last_editors: KangWenBin
        """
        param = {
            "timestamp": TimeHelper.get_now_timestamp(),
            "act_id": act_id,
            "open_id": open_id
        }
        sign_key = config.get_value("sign_key")
        
        param["sign"] = SignHelper.params_sign_md5(param, sign_key, False, False, False)

        domain_url = config.get_value("domain_url")
        result = requests.post(f"{domain_url}/client/user/check_user_info",json=param)       
        if result.status_code == 200:
            result_data = json.loads(result.text)
            if result_data["result"] == 1:
                return result_data["data"]
            else:
                return None
        else:
            return None

    @classmethod
    def get_user_grant_coupon(self, user_code, open_id, shop_id, act_id):
        """
        :description: 获取用户可领取的优惠券
        :last_editors: KangWenBin
        """        

        coupon_conn = CouponModelEx()

        ret_list = []
        # 获取正在投放的优惠券
        coupon_list = coupon_conn.get_grant_coupon_list(shop_id)
        if not coupon_list:
            return ret_list
        
        for item in coupon_list:
            item["grant_type"] = json.loads(item["grant_type"])
        
        coupon_ids = [x["id"] for x in coupon_list]
        # 获取当前用户已获取的优惠券
        user_coupon_list = CouponRecordModel().get_dict_list(where="coupon_id in %s and user_code=%s", params=[coupon_ids, user_code])

        # # 去除已领取的优惠券
        # coupon_list = [x for x in coupon_list if x["id"] not in [y["coupon_id"] for y in user_coupon_list]]
        
        if not coupon_list:
            return ret_list
        
        user_data = None
        if [x for x in coupon_list if 0 in x["grant_type"] or 3 in x["grant_type"]]:
            user_data = self.get_user_info(act_id,open_id)
        
        is_pay = None
        if [x for x in coupon_list if 1 in x["grant_type"] or 2 in x["grant_type"]]:
            order_model = OrderModel().get_dict(where="user_code=%s and pay_time > 0 and pay_order_id!=''", params=[user_code])
            if order_model:
                is_pay = True
            else:
                is_pay = False  
        
        # 判断优惠券类型
        for item in coupon_list:
            # 验证用户是否已领取过
            item["user_receive"] = 1 if [x for x in user_coupon_list if x["coupon_id"] == item["id"]] else 0
            if item["user_receive"]:
                ret_list.append(item)
                continue

            # grant_type 投放人群 0 新用户 1 未消费用户 2 已消费用户 3 会员用户
            if 0 in item["grant_type"] and user_data and user_data["is_new"] == 1: # 新用户
                pass
            elif 1 in item["grant_type"] and is_pay == False: # 未消费用户
                pass
            elif 2 in item["grant_type"] and is_pay == True: # 已消费用户
                pass 
            elif 3 in item["grant_type"] and user_data and user_data["is_member"] == 1: # 会员用户
                pass
            else:
                continue

            # 优惠券发放
            ret_list.append(item)

            
        return ret_list
    
    @classmethod
    def refund_coupon_check(self, coupon_id, order_id):
        """
        :description: 检测优惠券是否可退
        :last_editors: KangWenBin
        """        
        if coupon_id > 0:
            order_goods_count = OrderGoodsModel().get_total(where="order_id = %s", params=[order_id])
            order_refund_goods_count = OrderRefundGoodsModel().get_total(where="order_id = %s", params=[order_id])
            if order_goods_count == order_refund_goods_count:
                # 退还优惠券
                CouponRecordModel().update_table("order_id = '',use_time = 0,status = 0","id = %s",[order_id,coupon_id])
