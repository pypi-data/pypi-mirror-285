import pathlib
from theid import authorization_headers, system_id, email, private_ip, public_ip, hostname

from ._wanwang import _list_rrs
from ._wanwang import _build_payload
from ._wanwang import _update_rr

_owner = email()
_hostname = hostname()
_system_id = system_id()
_private_ip = private_ip()
_public_ip = public_ip()
_rr_string_private = _system_id + '.private'
_rr_string_public = _system_id + '.public'

def update():
    _update_rr(request_headers=authorization_headers(), rr_record=_rr_string_private,rr_value=_private_ip)
    _update_rr(request_headers=authorization_headers(), rr_record=_rr_string_public,rr_value=_public_ip)
    config_dir = pathlib.Path.home() / '.devnull'
    pathlib.Path(config_dir).mkdir(parents=True, exist_ok=True)
    fqdn_file = config_dir / 'fqdn'
    with fqdn_file.open('wt') as f:
        f.write('\n'.join([_system_id,
                           _hostname,
                           _private_ip,
                           _public_ip,
                           _rr_string_public + '.thedns.cn',
                           _rr_string_private + '.thedns.cn',
                           '']))
    return {
        _rr_string_public + '.thedns.cn': _public_ip,
        _rr_string_private + '.thedns.cn': _private_ip,
        'fqdn': fqdn_file.as_posix(),
        'owner': _owner
    }

# class DDNS(object):
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
#         self.system_uuid = _get_rr_string()
#         self.rr_string_public = self.system_uuid + '.public'
#         self.rr_string_private = self.system_uuid + '.private'
#     def update(self):
#         _update_rr(request_headers=self.request_headers, rr_record=self.rr_string_private,rr_value=self.private_ip)
#         _update_rr(request_headers=self.request_headers, rr_record=self.rr_string_public,rr_value=self.public_ip)
#         config_dir = pathlib.Path.home() / '.devnull'
#         pathlib.Path(config_dir).mkdir(parents=True, exist_ok=True)
#         fqdn_file = config_dir / 'fqdn'
#         with fqdn_file.open('wt') as f:
#             f.write('\n'.join([self.system_uuid,
#                                socket.gethostname(),
#                                self.private_ip,
#                                self.public_ip,
#                                self.rr_string_public + '.thedns.cn',
#                                self.rr_string_private + '.thedns.cn',
#                                '']))
#         return {
#             self.rr_string_public + '.thedns.cn': self.public_ip,
#             self.rr_string_private + '.thedns.cn': self.private_ip,
#             'fqdn': fqdn_file.as_posix(),
#         }
