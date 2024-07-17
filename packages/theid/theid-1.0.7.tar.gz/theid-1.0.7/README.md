# theid-sdk-python


#### Identity for services of https://devnull.cn/

```ipython
>>> import theid

>>> theid.token()
'Bearer <_truncated>'

>>> theid.authorization_headers()
{'Authorization': 'Bearer <_truncated>', 'Content-Type': 'application/json'}

>>> theid.system_id()
'e64ab96324ef1899498889a0e3eabcb4'

>>> theid.email()
'no-reply-devnull@outlook.com'

>>> theid.ip_regulated()
True

>>> theid.is_private_ip('192.168.0.1')
True

>>> theid.is_private_ip('1.168.0.1')
False


```