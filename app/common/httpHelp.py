import urllib2,json,urllib,requests

from hmac import new as hmac
from config import Config
import hashlib
def searchRequest(url,message,privatekey):
    sig = hmac(privatekey, message, hashlib.sha1).hexdigest()
    url = '{}/?sig={}&{}'.format(url,urllib.quote_plus(sig), message)
    data = urllib2.urlopen(url)
    data = json.loads(data.read())
    return data

from .alopex_auth_sdk import SignatureGeneration


def codeHubRequest(uri,method='get',url=None,headers=None,params=None,data=None,secret_key=""):
    if url is None:
        url = Config.CODEHUB_URL
    fullurl = url + uri
    if data:
        sign = SignatureGeneration(data,secret_key)
    elif params:
        sign = SignatureGeneration(params,secret_key)
    else:
        sign = SignatureGeneration(secret_key=secret_key)

    if sign:
        head = {'PRIVATE-TOKEN': Config.CODEHUB_TOKEN,'X-Signature':sign}
    else:
        head = {'PRIVATE-TOKEN': Config.CODEHUB_TOKEN}
    if headers:
        head.update(headers)
    request = {
        'get': requests.get,
        'post': requests.post,
        'put': requests.put,
        'delete': requests.delete,
    }

    res = request[method](url=fullurl, headers=head,params=params,data=data)
    return res