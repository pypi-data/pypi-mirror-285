import requests
from .auth import _token
from .auth import _credentials
from .auth import _request_headers
from .utils import _get_private_ip
from .utils import _system_id

_access_key, _secret_key, _email = _credentials()
_public_ip = requests.get('https://devnull.cn/ip').json()['origin']
_private_ip = _get_private_ip()
_system_id = _system_id()

def token():
    try:
        return _token(_email, _access_key, _secret_key)
    except:
        return {
            'rc': 205,
            'msg': 'unhealthy service.'
        }
def authorization_header():
    return _request_headers(token=token())