from ._auth import _token
from ._auth import _credentials
from ._auth import _request_headers
from ._utils import _public_ip
from ._utils import _private_ip
from ._utils import _system_id
from ._utils import _hostname

_access_key, _secret_key, _email = _credentials()

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

def private_ip():
    return _private_ip()

def public_ip():
    return _public_ip()

def hostname():
    return _hostname()
