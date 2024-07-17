import socket
import hashlib
import requests as __requests

def _private_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    private_ip_string = s.getsockname()[0]
    s.close()
    return private_ip_string

def _public_ip():
    return __requests.get('https://devnull.cn/ip').json()['origin']

def _system_id():
    try:
        with open('/etc/machine-id', 'r') as f:
            rr_string = hashlib.md5(f.read().encode()).hexdigest()
    except:
        rr_string = hashlib.md5(socket.gethostname().encode()).hexdigest()
    return rr_string

def _hostname():
    return socket.gethostname()
