# -*- coding: utf-8 -*-
"""
:Author: KangWenBin
:Date: 2024-06-12 11:54:39
:LastEditTime: 2024-06-18 14:28:38
:LastEditors: KangWenBin
:Description: 
"""
# -*- coding: utf-8 -*-

# 框架引用

from seven_shop.handlers.goods import *
from seven_shop.handlers.cart import *
from seven_shop.handlers.order import *
from seven_shop.handlers.init import *
from seven_shop.handlers.category import *
from seven_shop.handlers.coupon import *

def seven_shop_route():
    return [
        # 店铺
        (r"/client/init/info", InitHandler), # 店铺信息

        # 分类
        (r"/client/category/list", CategoryListHandler),

        # 系列
        (r"/client/series/list", CategorySeriesListHandler),
        
        # 商品相关
        (r"/client/goods/list", GoodsListHandler),
        (r"/client/goods/info", GoodsInfoHandler), # 商品信息
        (r"/client/goods/search", GoodsSearchHandler), # 商品搜索
        (r"/client/goods/detail", GoodsDetailListHandler), # 商品搜索
        (r"/client/goods/recommend", GoodsRecommentListHandler), # 商品推荐
        
        
        
        (r"/client/sku/info", SkuInfoHandler), # sku信息
        # 购物车
        (r"/client/cart/info", UserCartManageHandler), # 用户购物车管理
        (r"/client/cart/count", CartCountHandler), # 用户购物车数量
        
        #优惠券
        (r"/client/grant/info", CouponGrantInfoHandler), # 用户首页投放
        (r"/client/grant/list", CouponGrantListHandler), # 用户投放列表
        (r"/client/coupon/record", CouponRecordListHandler), # 用户优惠券列表
        (r"/client/coupon/order", CouponOrderListHandler), # 用户优惠券订单列表
        (r"/client/coupon/list", CouponListHandler), # 优惠券列表
        (r"/client/coupon/receive", CouponReceiveHandler), # 优惠券领取

        # 订单
        (r"/client/order/prepare", OrderPrepareHandler), # 订单确认
        (r"/client/order/detail", OrderDetailHandler), # 订单详情
        (r"/client/order/create", OrderCreateHandler), # 订单下单
        (r"/client/order/list", OrderListHandler), # 订单列表
        (r"/client/order/cancel", CancelOrderHandler), # 取消订单
        (r"/client/order/receipt", OrderReceiptHandler), # 确认收货
        (r"/client/order/callback", PayCallbackHandler), # 支付回调
        (r"/client/order/pay", RestartPayHandler), # 唤醒支付
        (r"/client/order/result", PayResultHandler), # 支付结果
        (r"/client/order/logistics", LogisticsHandler), # 物流信息接口 
        (r"/client/order/address", OrderaddressHandler), # 修改物流地址 
        
        
        # 退款
        (r"/client/refund/goods", RefundGoodsHandler), # 退款申请商品列表
        (r"/client/refund/apply", ApplyRefundHandler), # 退款申请单
        (r"/client/refund/detail", RefundDetailHandler), # 退款单详情
        (r"/client/refund/cancel", RefundCancelHandler), # 退款单撤销
        (r"/client/refund/logistics", RefundLogisticsHandler), # 退款单买家发货
        (r"/client/refund/list", RefundListHandler), # 退款单列表
    ]
