# theid-sdk-python


### Generate JWT
Identity Service URL: https://devnull.cn/identity

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
>>> 

```