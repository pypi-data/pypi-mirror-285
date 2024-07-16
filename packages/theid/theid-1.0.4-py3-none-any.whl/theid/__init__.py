import requests as __requests
from ._auth import _token
from ._auth import _credentials
from ._auth import _request_headers
from ._utils import _get_private_ip
from ._utils import _system_id

_access_key, _secret_key, _email = _credentials()
_public_ip = __requests.get('https://devnull.cn/ip').json()['origin']
_private_ip = _get_private_ip()

def token():
    try:
        return _token(_email, _access_key, _secret_key)
    except:
        return {
            'rc': 205,
            'msg': 'unhealthy service.'
        }
def authorization_headers():
    return _request_headers(token=token())

def system_id():
    return _system_id()

def email():
    return _email
