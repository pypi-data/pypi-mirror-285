# -*- coding: utf-8 -*-
"""
:Author: Kangwenbin
:Date: 2021-11-19 14:42:35
:LastEditTime: 2024-07-19 17:44:01
:LastEditors: KangWenBin
:Description: 
"""

from seven_framework.web_tornado.base_handler.base_api_handler import *
from seven_framework.redis import RedisHelper


class SevenBaseHandler(BaseApiHandler):

    redis_init = RedisHelper.redis_init(config.get_value("redis")["host"],config.get_value("redis")["port"],config.get_value("redis")["db"],config.get_value("redis")["password"])

    def __init__(self, *argc, **argkw):
        """
        @description: 初始化
        @last_editors: Kangwenbin
        """
        super(SevenBaseHandler, self).__init__(*argc, **argkw)

    def write_error(self, status_code, **kwargs):
        """
        :Description: 重写全局异常事件捕捉
        :last_editors: ChenXiaolei
        """
        self.logger_error.error(
            traceback.format_exc(),
            extra={"extra": {
                "request_code": self.request_code if hasattr(self,"request_code") else ""
            }})
        return self.response_json_error()
    
    def send_notice(self,text):
        """
        :description: 消息通知
        :last_editors: KangWenBin
        """        
        NoticeHelper(webhook_key=config.get_value("webhook_key")).send_webhook(text)

    def finish_json_error(self, desc = "error"):
        finish_dict = dict()
        finish_dict["result"] = 0
        finish_dict["desc"] = desc
        finish_dict["data"] = None
        self.finish(JsonHelper.json_dumps(finish_dict))

    def prepare_ext(self):
        """
        @description: 准备方法(签名验证)
        @last_editors: KangWenBin
        """
        if self.request.uri == "/client/order/callback" or self.request.uri == "/client/refund/notify":
            return
        
        try:
            # 签名参数
            sign_params = {}

            if "Content-Type" in self.request.headers and self.request.headers[
                        "Content-type"].lower().find(
                            "application/json") >= 0 and self.request.body:
                json_params = {}
                try:
                    json_params = json.loads(self.request.body)
                except:
                    return self.finish_json_error("params error")
                    
                if json_params:
                    for field in json_params:
                        sign_params[field] = json_params[field]
            if self.request.arguments and len(self.request.arguments)>0:
                for field in self.request.arguments:
                    sign_params[field] = self.get_param(field)

            # 客户端效验规则
            if not sign_params or len(sign_params) < 2 or "timestamp" not in sign_params or "sign" not in sign_params:
                self.finish_json_error("sign params error!")
                return

            # 请求时间效验
            sign_timestamp = int(sign_params["timestamp"])
            if TimeHelper.add_seconds_by_timestamp(sign_timestamp, 60) < TimeHelper.get_now_timestamp():
                self.finish_json_error("timeout")
                return

            # 构建签名
            sign_key = config.get_value("sign_key")
            build_sign = SignHelper.params_sign_md5(
                sign_params, sign_key, False, False, False)

            if not build_sign or build_sign != sign_params["sign"]:
                self.logger_info.info(
                    f"http请求验签不匹配,收到sign:{sign_params['sign']},构建sign:{build_sign} 加密明文信息:{SignHelper.get_sign_params_str(sign_params,sign_key,False,False)}")
                return self.finish_json_error("sign error!")
        except:
            self.logger_error.error(traceback.format_exc())
            return self.finish_json_error("server error!")
        
    def strip_trailing_zeros(self,price):
        """
        :description: 去除小数点后多余的0
        :last_editors: KangWenBin
        """        
        price_str = str(price)
        if '.' in price_str:
            price_str = price_str.rstrip('0').rstrip('.')
        return price_str
    
    def is_continue_request(self, cache_key, expire=500):
        """
        :description: 请求太频繁校验
        :param cache_key：自定义cache_key
        :param expire：过期时间，单位毫秒
        :return: bool true-代表连续请求进行限制，false-代表跳过限制
        """
        post_value = self.redis_init.incr(cache_key,1)
        if post_value > 1:
            return True
        self.redis_init.pexpire(cache_key,expire)
        return False



    