from aliyunsdkcore import client

from json import loads
from config import Config
AccessKey=Config.ALIYUN_ID
AccessSecret=Config.ALIYUN_SECRET

def GetClient(regionId="cn-hangzhou"):
    return client.AcsClient(AccessKey, AccessSecret, regionId)


def LoadSDK(sdk_req, regionId="cn-hangzhou"):
    clt = GetClient(regionId)
    req = sdk_req
    req.set_accept_format('json')
    res_json = clt.do_action(req)
    res = loads(res_json)
    return res