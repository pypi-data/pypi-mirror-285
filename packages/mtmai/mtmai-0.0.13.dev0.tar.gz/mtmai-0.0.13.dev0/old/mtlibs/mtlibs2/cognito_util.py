

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

# def jwt_get_username_from_payload_handler(payload):
#     """
#         提示：payload中，没有直接包含详细的用户信息，但是sub字段中包含了用户ID。
#               代码是来自于官方范例。
#     """
#     username = payload.get('sub').replace('|', '.')
#     authenticate(remote_user=username)
#     return username


# def jwt_decode_token(token):
#     header = jwt.get_unverified_header(token)
#     auth0_domain = settings.AUTH0_DOMAIN  # os.environ.get('AUTH0_DOMAIN')
#     jwks = requests.get(
#         'https://{}/.well-known/jwks.json'.format(auth0_domain)).json()
#     public_key = None
#     for jwk in jwks['keys']:
#         if jwk['kid'] == header['kid']:
#             public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

#     if public_key is None:
#         raise Exception('Public key not found.')
#     api_identifier = settings.API_IDENTIFIER

#     issuer = 'https://{}/'.format(auth0_domain)
#     return jwt.decode(token, public_key, audience=api_identifier, issuer=issuer, algorithms=['RS256'])


def jwt_decode_token(token):
    """这个函数同jwt_decode_token， 只是不同的写法，留作参考。"""
    # url = f'https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json'
    url = f'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_cT1Z4oABW/.well-known/jwks.json'
    client_id = '7e7m592m7oceudmca3i12b1vmi'
    audience=client_id,
    jwks_client = PyJWKClient(url)
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=['RS256'],
        audience=audience
    )