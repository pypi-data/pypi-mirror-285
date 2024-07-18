

# auth0 认证实用工具
#

import email
import json
import os

from django.contrib.auth import authenticate
import jwt
import requests
from django.conf import settings
from jwt import PyJWKClient
from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions


def get_token_auth_header(request):
    """从http header 总获取access_token"""
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    if auth:
        parts = auth.split()
        token = parts[1]
        return token
    return None

def jwt_get_username_from_payload_handler(payload):
    """
        提示：payload中，没有直接包含详细的用户信息，但是sub字段中包含了用户ID。
              代码是来自于官方范例。
    """
    username = payload.get('sub').replace('|', '.')
    authenticate(remote_user=username)
    return username


def jwt_decode_token(token):
    header = jwt.get_unverified_header(token)
    auth0_domain = settings.AUTH0_DOMAIN  # os.environ.get('AUTH0_DOMAIN')
    jwks = requests.get(
        'https://{}/.well-known/jwks.json'.format(auth0_domain)).json()
    public_key = None
    for jwk in jwks['keys']:
        if jwk['kid'] == header['kid']:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    if public_key is None:
        raise Exception('Public key not found.')
    api_identifier = settings.API_IDENTIFIER

    issuer = 'https://{}/'.format(auth0_domain)
    return jwt.decode(token, public_key, audience=api_identifier, issuer=issuer, algorithms=['RS256'])


def jwt_decode_token2(token):
    """这个函数同jwt_decode_token， 只是不同的写法，留作参考。"""
    url = f'https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json'
    jwks_client = PyJWKClient(url)
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=['RS256'],
        audience=f'{settings.API_IDENTIFIER}'
    )


class DrfAuto0Authentication(authentication.BaseAuthentication):
    """ drf 自定义认证
        由于djangorestframework-jwt 不在维护，使用其他jwt框架也显得累赘。所以自定义一个drf 登录验证功能。
        auth0 官方范例，使用djangorestframework-jwt库，显得过时，而且累赘。
        原理：客户端(例如react)使用自己的方式登录auth0后，会得到access_token, 
              客户端通过设置 http authention 头，将access_token传递进来，
              本函数，以jwt的方式解释 access_token并进一步得到用户信息。
              
        
        settings 配置：
        REST_FRAMEWORK = {
            ...
            'DEFAULT_AUTHENTICATION_CLASSES':{
                ...
                mtlibs.auth0Auth.ExampleAuthentication
            }
        }
        
    """
    def authenticate(self, request):
        token = get_token_auth_header(request)
        
        decode_token = jwt_decode_token(token)
        username = jwt_get_username_from_payload_handler(decode_token)
        
        # 思考： 有没有必要将auto0的用户信息，映射到django 的用户信息？
        #        由或者，可以区分用户来自auth0 或者是django 内部用户。
        # if not username:
        #     return None

        try:
            user = User.objects.get(username=username)
            return (user, None) # 第二个 是auth 对象。
        except User.DoesNotExist:
            # 自动创建新用户，与之对应。
            new_user = User.objects.create(username="username",email="a@a.com",password="NJ87#hn@8xss6yd" )
            return (new_user, None) # 第二个 是auth 对象。
            # raise exceptions.AuthenticationFailed('No such user')


        # return (user, None) # 第二个 是auth 对象。
        