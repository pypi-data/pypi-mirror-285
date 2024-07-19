import seven_framework.config as config
from seven_framework.sign import *
from seven_framework.time import *
import requests

class UserHelper:

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