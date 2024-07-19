# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-05-31 15:02:27
:LastEditTime: 2024-07-19 13:31:05
:LastEditors: KangWenBin
:Description: 
"""

from seven_shop.models.db_models.goods.goods_model_ex import *
from seven_shop.models.db_models.shop.shop_model_ex import *
from seven_shop.models.db_models.coupon.coupon_record_model import *
from seven_shop.models.db_models.coupon.coupon_model_ex import *
import random
from decimal import Decimal
import math

class OrderHelper:
    @classmethod
    def create_order_number(self):
        time_string = TimeHelper.get_now_format_time().replace("-","").replace(" ","").replace(":","")
        random_string = random.randint(100000,999999)
        return f"{time_string}{random_string}"


    @classmethod
    def order_check(self,shop_id,buy_list,province_name,user_code,act_id,coupon_id):
        """
        :description: 订单商品价格验证
        :param shop_id 店铺id
        :param buy_list 购买商品列表
        :param province_name 省份
        :param user_code 用户标识
        :param coupon_id 优惠券id
        :last_editors: KangWenBin
        """
        ret_data = {
            "result": 0,
            "desc": "",
            "data": None
        }

        order_data = {
            "goods_price":0, # 商品价格
            "coupon_price":0, # 优惠券金额
            "postage":0, # 运费金额
            "pay_price":0, # 实付金额
            "order_status":0,
            "goods_list": []
        }

        goods_conn = GoodsModelEx()
        for item in buy_list:
            goods_model = goods_conn.get_buy_goods_info(shop_id,item["goods_id"],item["sku_id"],item["buy_count"])
            if not goods_model:
                ret_data["desc"] = "商品信息错误,请重新选择"
                return ret_data
            
            order_data["goods_list"].append(goods_model)
        
        if not order_data["goods_list"]:
            ret_data["desc"] = "商品信息异常,请重新选择"
            return ret_data
        
        # 计算总费用
        order_data["goods_price"] = sum([x["total_price"] for x in order_data["goods_list"]]) # 计算商品总金额
        order_data["postage"] = 0 if not province_name else ShopModelEx(context=self).get_postage(province_name,shop_id)
        # 计算优惠券金额
        order_data["coupon_price"] = 0 
        if coupon_id:
            # 验证优惠券是否可用
            coupon_model = CouponRecordModel(context=self).get_dict(where="id = %s and status = 0 and user_code = %s and act_id = %s and begin_time <= %s and end_time > %s and shop_id = %s",params=[coupon_id,user_code,act_id,TimeHelper.get_now_timestamp(),TimeHelper.get_now_timestamp(),shop_id],field="coupon_info,use_price,goods_limit,goods_list")
            if not coupon_model:
                ret_data["desc"] = "优惠券无法使用,请重新选择"
                return ret_data

            coupon_info = json.loads(coupon_model["coupon_info"])
            
            # 可用优惠券商品列表
            coupon_goods_list = []
            # 计算优惠券商品限制
            buy_price = -1
            if coupon_model["goods_limit"] == 0:
                buy_price = order_data["goods_price"]
                coupon_goods_list = order_data["goods_list"]
            else:
                # 验证商品是否有交集
                intersection_list = list(set(json.loads(coupon_model["goods_list"])) & set([x["goods_id"] for x in order_data["goods_list"]]))
                if intersection_list:
                    # 获取商品总金额
                    coupon_goods_list = [x for x in order_data["goods_list"] if x["goods_id"] in intersection_list]
                    buy_price = sum([x["total_price"] for x in coupon_goods_list])
            
            if buy_price == -1:
                ret_data["desc"] = "优惠券商品限制,请重新选择"
                return ret_data
            
            # 验证金额条件
            if buy_price >= coupon_model["use_price"]:
                # 判断满减券还是折扣券
                if coupon_info["coupon_type"] == 0: # 满减券
                    order_data["coupon_price"] = Decimal(coupon_info["coupon_price"])
                elif coupon_info["coupon_type"] == 1: # 折扣券
                    order_data["coupon_price"] = round(order_data["goods_price"] * ((10-Decimal(coupon_info["coupon_discount"]))/10),2)

                order_data["coupon_price"] = order_data["coupon_price"] if order_data["coupon_price"] < order_data["goods_price"] else order_data["goods_price"]
            else: 
                ret_data["desc"] = "商品金额未达到优惠券使用条件"
                return ret_data
            
        if order_data["coupon_price"] > 0:
            # 将优惠券金额分配给各商品
            for item in coupon_goods_list:
                item["coupon_id"] = coupon_id
                coupon_price = self.round_half_even(order_data["coupon_price"] * (item["total_price"] / buy_price))
                item["coupon_price"] = coupon_price if coupon_price < item["total_price"] else item["total_price"]

        if order_data["postage"] == -1:
            ret_data["desc"] = "配置信息错误"
            return ret_data
        
        order_data["pay_price"] = order_data["goods_price"] + order_data["postage"] - order_data["coupon_price"]  
        # 验证当前订单是否可支付
        check_model = [x for x in order_data["goods_list"] if x["status"] == 0 or x["inventory_status"] == 0]
        order_data["order_status"] = 1 if not check_model else 0
        ret_data["result"] = 1
        ret_data["data"] = order_data
        return ret_data
    
    @classmethod
    def round_half_even(self, price):
        """
        :description: 数字四舍六入五成双方法
        :last_editors: KangWenBin
        """        
        # 分离整数部分和小数部分
        price = math.floor(price*1000) / 10
        integer_part = math.floor(price)
        decimal_part = price - integer_part

        # 检查小数部分是否为0.5
        if decimal_part > 0.5 or decimal_part < 0.5:
            # 不是0.5，使用标准四舍五入
            rounded_number = round(price)
        else:
            # 是0.5，检查整数部分的奇偶性
            if integer_part % 2 == 0:
                # 整数部分是偶数，不进位
                rounded_number = integer_part
            else:
                # 整数部分是奇数，进位
                rounded_number = integer_part + 1
        
        # 将舍入后的数字除以1000，恢复到原来的小数位
        return Decimal(str(rounded_number / 100))