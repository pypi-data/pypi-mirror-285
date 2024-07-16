from .auth import _token
from .auth import _credentials
from .auth import _request_headers
# from .utils import _get_private_ip
# from .utils import _get_uuid
from .utils import _update
from .utils import _get


_access_key, _secret_key, _email = _credentials()
_token = _token(_email, _access_key, _secret_key)
_request_headers = _request_headers(token=_token)
def update(key_string, value_string, **kargs):
    return _update(request_headers=_request_headers,
                   pulse_id=kargs.get('pulse_id', None),
                   key_string=key_string,
                   value_string=value_string
                   )

def get(pulse_id=None):
    return _get(request_headers=_request_headers, pulse_id=pulse_id)

# class Init(object):
#     access_key = None
#     secret_key = None
#     email = None
#     public_ip = None
#     private_ip = None
#     token = None
#     request_headers = None
#     def __init__(self):
#         self.access_key, self.secret_key, self.email = _credentials()
#         self.public_ip = requests.get('https://devnull.cn/ip').json()['origin']
#         self.private_ip = _get_private_ip()
#         self.token = _token(self.email, self.access_key, self.secret_key)
#         self.request_headers = _request_headers(token=self.token)
#     def update(self, key_string, value_string, **kargs):
#         return _update(request_headers=self.request_headers,
#                        pulse_id=kargs.get('pulse_id', None),
#                        key_string=key_string,
#                        value_string=value_string
#                        )
#
#     def get(self, pulse_id=None):
#         return _get(request_headers=self.request_headers, pulse_id=pulse_id)