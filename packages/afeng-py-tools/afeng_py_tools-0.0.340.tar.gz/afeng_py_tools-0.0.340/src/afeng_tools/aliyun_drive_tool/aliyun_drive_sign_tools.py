"""
阿里云盘签到工具
pip install aligo -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""

from aligo import Aligo


class SignInAligo(Aligo):
    def sign_in_list(self):
        return self.post(
            '/v1/activity/sign_in_list',
            host='https://member.aliyundrive.com',
            body={'isReward': True},
            params={'_rx-s': 'mobile'}
        )

    def sign_in_reward(self, day):
        return self.post(
            '/v1/activity/sign_in_reward',
            host='https://member.aliyundrive.com',
            body={'signInDay': day},
            params={'_rx-s': 'mobile'}
        )

    def sign_in_festival(self):
        return self.post(
            '/v1/activity/sign_in_list',
            host='https://member.aliyundrive.com',
            body={},
            params={'_rx-s': 'mobile'}
        )


def get_sign_in_list(alipan_sign_api: SignInAligo) -> int:
    """获取签到列表"""
    log = alipan_sign_api._auth.log
    # 获取签到列表
    resp = alipan_sign_api.sign_in_list()
    result = resp.json()['result']
    signInCount = result['signInCount']
    log.info("本月签到次数: %d", signInCount)
    return signInCount


def do_sign_in(alipan_sign_api: SignInAligo):
    """执行签到"""
    log = alipan_sign_api._auth.log
    # 获取签到列表
    resp = alipan_sign_api.sign_in_list()
    result = resp.json()['result']
    signInCount = result['signInCount']
    log.info("本月签到次数: %d", signInCount)
    sign_in_resp = alipan_sign_api.sign_in_reward(signInCount)
    if sign_in_resp.status_code==200:
        log.info(sign_in_resp.json()['result']['notice'])
    else:
        log.error(sign_in_resp.text)


if __name__ == '__main__':
    ali = SignInAligo()
    # get_sign_in_list(ali)
    do_sign_in(ali)
