#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import request, g,redirect,make_response,jsonify
from itsdangerous import TimedJSONWebSignatureSerializer as JwtSerializer
import functools
from ApiResponse import ApiResponse,ResposeStatus
from config import Config
import hashlib,time
APP_ID = Config.APP_ID
APP_SECRET = Config.APP_SECRET
AUTH_SERVER_HOST = Config.AUTH_SERVER_HOST
AUTH_SERVER_LOGIN_URL = Config.AUTH_SERVER_LOGIN_URL
AUTH_SERVER_LOGOUT_URL = Config.AUTH_SERVER_LOGOUT_URL


class AccessTokenModel(object):
    def __init__(self, client_id, user):
        self.client_id = client_id
        self.user = user

    @classmethod
    def token2cls(cls, token,client_secret=APP_SECRET):
        if token:
            s = JwtSerializer(client_secret)
            try:
                data = s.loads(token)
                print data
                if "client_id" in data and "user" in data:
                    return cls(data["client_id"], data["user"])
                else:
                    return None
            except Exception,e:
                print e
                return None
        else:
            return None


def get_access_token():
    access_token = request.headers.get("Authorization")
    access_token = request.args.get("accesstoken") if access_token is None else access_token
    access_token = request.cookies.get("accesstoken") if access_token is None else access_token
    access_token = request.form.get("accesstoken") if access_token is None else access_token
    return access_token


def authorize(access_token):
    token_obj = AccessTokenModel.token2cls(access_token)

    if token_obj:
        return token_obj
    else:
        return None

def SignatureGeneration(res_dict={}, secret_key="", time_out=300):
    key_list = res_dict.keys()
    key_list.sort()
    str = u''
    for key in key_list:
        if not isinstance(res_dict.get(key), (dict, list)):
            str += unicode(res_dict.get(key))
    sign_str = secret_key + str
    sign = hashlib.md5(sign_str).hexdigest()[8:-8]
    return sign

def need_sign():
    def decorator(func):
        @functools.wraps(func)
        def auth(*args, **kwargs):
            access_token = request.headers.get("Authorization")
            signature = request.headers.get("X-Signature")
            access = False

            if access_token:
                user_obj = authorize(access_token)
                if user_obj:
                    access = True
                else:
                    return ApiResponse(None, ResposeStatus.AuthenticationFailed)

            elif signature:
                req = {}
                if request.form:
                    req = dict(req, **request.form.to_dict())
                if request.args:
                    req = dict(req, **request.args.to_dict())
                if request.json:
                    req = dict(req, **request.json)
                if signature == SignatureGeneration(req):
                    access = True
                else:
                    return ApiResponse(None, ResposeStatus.SignFail)

            if access:
                response = func(*args, **kwargs)
                return response
            else:
                return ApiResponse(None, ResposeStatus.SignFail)
        return auth

    return decorator



def logout():
    """
    用户退出引入方法
    :return:
    """
    response = make_response(redirect("{0}?appid={1}&callback={2}".format(AUTH_SERVER_LOGOUT_URL, APP_ID, request.host)))
    response.delete_cookie('accesstoken')
    return response

def need_login2(roles=[],save_token_at_cookie=True):
    """
    身份验证装饰器
    :param save_token_at_cookie:
    :return:
    """
    def decorator(func):
        @functools.wraps(func)
        def auth(*args, **kw):
            access_token = get_access_token()
            user_obj = authorize(access_token)
            if user_obj:
                # 已登录
                g.user = user_obj.user
                g.userID = user_obj.user.get('id')
                #response = make_response(jsonify(func(*args, **kw)))
                # if save_token_at_cookie:
                #     if (not request.cookies.get("accesstoken")) or (access_token!=request.cookies.get("accesstoken")) :
                #         response.set_cookie("accesstoken", access_token)
                if roles and roles.__len__()>0:
                    if g.user.get("role") in roles:
                        return func(*args, **kw)
                else:
                    return func(*args, **kw)

                return ApiResponse('No permission', ResposeStatus.Powerless)
            # else:
            #     # 未登录或登录失效
            #     return redirect("{0}?appid={1}&callback={2}".format(AUTH_SERVER_LOGIN_URL,APP_ID,request.url))
            else:
                return ApiResponse('Error user', ResposeStatus.AuthenticationFailed)

        return auth

    return decorator