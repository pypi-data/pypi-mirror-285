# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-05-28 11:32:24
:LastEditTime: 2024-06-18 15:28:27
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop.models.db_models.coupon.coupon_model import *
from seven_shop.models.db_models.coupon.coupon_record_model import *


class CouponModelEx(CouponModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key, sub_table, db_transaction, context)
    
    def get_grant_coupon_list(self,shop_id):
        """
        :description: 获取正在投放的优惠券列表
        :last_editors: KangWenBin
        """        
        sql = f"SELECT a.*,b.id AS grant_id,b.grant_type,b.grant_picture FROM coupon_tb a JOIN coupon_grant_tb b ON a.id = b.coupon_id WHERE a.status = 1 AND b.status = 1 AND a.shop_id = %s and a.begin_time<= %s AND a.end_time>=%s AND b.begin_time<= %s AND b.end_time>=%s order by b.id DESC"
        param_list = [shop_id, TimeHelper.get_now_timestamp(), TimeHelper.get_now_timestamp(), TimeHelper.get_now_timestamp(), TimeHelper.get_now_timestamp()]
        return self.db.fetch_all_rows(sql, param_list)
        
    
    def update_coupon_inventory(self,coupon_id):
        """
        :description: 修改优惠券库存
        :last_editors: KangWenBin
        """        
        sql = "UPDATE coupon_tb SET record_number = IF(record_number + 1 > coupon_inventory, record_number, record_number + 1) WHERE id = %s"
        row_count = self.db.update(sql,coupon_id)
        return row_count
    
    def check_coupon_inventory(self,coupon_id):
        """
        :description: 检查优惠券库存是否正确
        :last_editors: KangWenBin
        """
        inventory_model = self.get_dict(where="id = %s",params=[coupon_id],field="record_number")
        record_number = CouponRecordModel().get_total(where="coupon_id = %s",params=[coupon_id])
        if not inventory_model:
            return
            
        if inventory_model["record_number"] != record_number:
            self.update_table(update_sql="record_number = %s",where="id = %s",params=[record_number,coupon_id])

    def get_receive_coupon_list(self,user_code,shop_id):
        """
        :description: 获取可领取优惠券列表
        :last_editors: KangWenBin
        """        
        sql = "SELECT a.id,a.coupon_name,a.coupon_type,a.use_price,a.goods_limit,a.coupon_price,a.coupon_discount,a.begin_time,a.end_time,a.using_rule,b.id as receive_id FROM coupon_tb a LEFT JOIN coupon_record_tb b ON a.id = b.coupon_id and (b.user_code = %s OR b.id IS NULL) where a.shop_id = %s and a.status = 1 and a.is_receive = 1 and a.begin_time <= %s and a.end_time > %s"
        param_list = [user_code, shop_id, TimeHelper.get_now_timestamp(), TimeHelper.get_now_timestamp()]
        coupon_list = self.db.fetch_all_rows(sql, param_list)
        coupon_list = [x for x in coupon_list if x["receive_id"] is None]
        return coupon_list
        



    