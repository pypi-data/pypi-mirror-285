# -*- coding: utf-8 -*-
"""
:Author: Kangwenbin
:Date: 2021-12-02 21:35:16
:LastEditTime: 2024-07-16 11:39:21
:LastEditors: KangWenBin
:Description: 
"""

from seven_shop.models.db_models.order.order_goods_model import *

class OrderGoodsModelEx(OrderGoodsModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key=db_connect_key, sub_table=sub_table, db_transaction=db_transaction, context=context)

    def get_order_goods_list(self,order_id_list):
        """
        :description: 获取订单商品相关信息
        :last_editors: Kangwenbin
        """
        
        sql = "SELECT a.order_id,a.goods_id,a.sku_id,a.sku_name,a.goods_picture,a.goods_name,a.buy_count,a.price,a.real_pay_price,c.status as refund_status FROM order_goods_tb a LEFT JOIN order_refund_goods_tb b ON a.order_id = b.order_id AND a.goods_id = b.goods_id AND a.sku_id = b.sku_id LEFT JOIN order_refund_tb c ON b.refund_order_id = c.refund_order_id where a.order_id in %s"
        goods_list = self.db.fetch_all_rows(sql, (order_id_list,))
        # 数据处理(去重)
        unique_data = {}
        for item in goods_list:
            order_id = item['order_id']
            goods_id = item['goods_id']
            sku_id = item['sku_id']
            # 检查当前的goods_id和sku_id组合是否已经存在于字典中
            if (order_id, goods_id, sku_id) not in unique_data or unique_data[(order_id, goods_id, sku_id)]['refund_status'] == 4:
                # 如果不存在或者refund_status为4，则更新字典
                unique_data[(order_id, goods_id, sku_id)] = item

        # 将字典转换回列表形式，如果需要
        goods_list = list(unique_data.values())
        if goods_list:
            # 排除已撤销的退款单
            for item in goods_list:
                # 商品退款状态 # 0 无退款 1 退款中 2 退款成功 3 退款失败
                if item["refund_status"] is None or item["refund_status"] == 4:
                    item["refund_status"] = 0
                elif item["refund_status"] in [0,1,3]:
                    item["refund_status"] = 1
                elif item["refund_status"] == 5:
                    item["refund_status"] = 2
                elif item["refund_status"] in [2,6]:
                    item["refund_status"] = 3
        return goods_list

    def get_refund_goods_list(self,order_id,goods_list = []):
        """
        :description: 获取需要退货的商品列表
        :last_editors: KangWenBin
        """        
        condition = "a.order_id = %s"
        param_list = [order_id]
        # 如果有商品列表，构建商品的查询条件
        if goods_list:
            goods_conditions = []
            for item in goods_list:
                goods_conditions.append("(a.goods_id = %s and a.sku_id = %s)")
                param_list.extend([item["goods_id"], item["sku_id"]])
            condition += " and (" + " or ".join(goods_conditions) + ")"
        sql = f"SELECT a.goods_id,a.sku_id,a.sku_name,a.goods_picture,a.goods_code,a.goods_name,a.buy_count,a.real_pay_price,IF(c.status IS NULL,0,c.status) AS refund_status FROM order_goods_tb a LEFT JOIN order_refund_goods_tb b ON a.order_id = b.order_id AND a.goods_id=b.goods_id AND a.sku_id = b.sku_id LEFT JOIN order_refund_tb c ON b.refund_order_id = c.refund_order_id WHERE {condition}"
        goods_list = self.db.fetch_all_rows(sql, param_list)
        # 排除退款撤销的商品
        unique_data = {}
        for item in goods_list:
            goods_id = item['goods_id']
            sku_id = item['sku_id']
            # 检查当前的goods_id和sku_id组合是否已经存在于字典中
            if (goods_id, sku_id) not in unique_data or unique_data[(goods_id, sku_id)]['refund_status'] == 4:
                # 如果不存在或者refund_status为4，则更新字典
                unique_data[(goods_id, sku_id)] = item

        # 将字典转换回列表形式，如果需要
        goods_list = list(unique_data.values())
        # 状态大于0的设置为1
        if goods_list:
            for goods in goods_list:
                if goods["refund_status"] > 0 and goods["refund_status"] != 4:
                    goods["refund_status"] = 1
        
        return goods_list
    

        
        
        