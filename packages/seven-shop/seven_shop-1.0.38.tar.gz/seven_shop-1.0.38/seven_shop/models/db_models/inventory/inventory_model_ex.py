# -*- coding: utf-8 -*-
"""
:Author: Kangwenbin
:Date: 2021-11-23 14:58:49
:LastEditTime: 2024-06-12 14:50:19
:LastEditors: KangWenBin
:Description: 
"""
from seven_shop.models.db_models.inventory.inventory_model import *
from seven_shop.models.db_models.inventory.inventory_change_model import *

class InventoryModelEx(InventoryModel):
    def __init__(self, db_connect_key='db_shopping_center', sub_table=None, db_transaction=None, context=None):
        super().__init__(db_connect_key=db_connect_key, sub_table=sub_table, db_transaction=db_transaction, context=context)

    def goods_inventory(self, goods_model):
        """
        :description: 附加库存
        :param goods_model 实体
        :last_editors: Kangwenbin
        """        
        if goods_model["sku_info"]["sku_list"]:
            for item in goods_model["sku_info"]["sku_list"]:
                item["inventory"] = self.get_inventory(goods_model["goods_info"]["id"],item["id"])
            goods_model["goods_info"]["inventory"] = 0
        else:
            goods_model["goods_info"]["inventory"] = self.get_inventory(goods_model["goods_info"]["id"],0)
        
        return goods_model
    
    def sku_inventory(self, goods_id, sku_list):
        """
        :description: 附加库存
        :param sku_list sku列表
        :last_editors: Kangwenbin
        """        
        if sku_list["sku_list"]:
            for item in sku_list["sku_list"]:
                item["inventory"] = self.get_inventory(goods_id,item["id"])
        return sku_list

    def get_inventory(self,goods_id,sku_id = 0):
        """
        :description: 获取商品或sku库存
        :param goods_id 商品id
        :param sku_id sku_id
        :last_editors: Kangwenbin
        """
        ret = 0 
        inventory_model = self.get_dict(where="goods_id = %s and sku_id = %s",params=[goods_id,sku_id],field="inventory")
        if inventory_model:
            ret = inventory_model["inventory"]
        return ret

    def update_check_inventory(self,goods_id,sku_id,inventory_count):
        """
        :description: 
        :param goods_id 商品id
        :param sku_id sku_id
        :param inventory_count 购买的数量
        :last_editors: Kangwenbin
        """        
        sql = "UPDATE inventory_tb SET inventory = IF(inventory < %s, inventory, inventory - %s) WHERE goods_id = %s and sku_id = %s"
        params = [inventory_count,inventory_count,goods_id,sku_id]
        row_count = self.db.update(sql,params)
        return row_count

    def check_goods_inventory_list(self,goods_list):
        """
        :description: 商品库存验证
        :param goods_list 需要验证的商品列表
        :last_editors: Kangwenbin
        """        
        if goods_list:
            inventory_change_conn = InventoryChangeModel()
            for goods in goods_list:
                inventory_model = self.get_dict(where="goods_id = %s and sku_id = %s",params=[goods["goods_id"],goods["sku_id"]],field="inventory")
                sum_inventory_model = inventory_change_conn.get_dict(where="goods_id = %s and sku_id = %s",params=[goods["goods_id"],goods["sku_id"]],field="IFNULL(sum(change_inventory),0) as change_inventory")
                if not inventory_model or not sum_inventory_model:
                    continue
                    
                if inventory_model["inventory"] != sum_inventory_model["change_inventory"]:
                    self.update_table(update_sql="inventory = %s",where="goods_id = %s and sku_id = %s",params=[sum_inventory_model["change_inventory"],goods["goods_id"],goods["sku_id"]])

    def check_goods_inventory(self,goods_id,sku_id):
        """
        :description: 单个商品库存验证
        :last_editors: Kangwenbin
        """        
        inventory_model = self.get_dict(where="goods_id = %s and sku_id = %s",params=[goods_id,sku_id],field="inventory")
        sum_inventory_model = InventoryChangeModel().get_dict(where="goods_id = %s and sku_id = %s",params=[goods_id,sku_id],field="IFNULL(sum(change_inventory),0) as change_inventory")
        if not inventory_model or not sum_inventory_model:
            return
        if inventory_model["inventory"] != sum_inventory_model["change_inventory"]:
            self.update_table(update_sql="inventory = %s",where="goods_id = %s and sku_id = %s",params=[sum_inventory_model["change_inventory"],goods_id,sku_id])


    def get_goods_total_inventory(self,goods_id):
        """
        :description: 获取商品所有库存
        :last_editors: Kangwenbin
        """        
        ret = 0
        inventory_model = self.get_dict(where="goods_id = %s",params=[goods_id],field="ifnull(sum(inventory),0) as inventory")
        if inventory_model:
            ret = inventory_model["inventory"]
        return ret