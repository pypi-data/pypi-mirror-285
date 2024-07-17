import pathlib
import base64
from theid import authorization_headers, system_id, email

# from .auth import _token
# from .auth import _credentials
# from .auth import _request_headers
# from .utils import _get_private_ip
# from .utils import _get_fqdn_id
from ._utils import _create_ca
from ._utils import _create_cert
# from .utils import _get_ca
# from .utils import _get_certs


# _access_key, _secret_key, _email = _credentials()
# _public_ip = requests.get('https://devnull.cn/ip').json()['origin']
# _private_ip = _get_private_ip()
# _token = _token(_email, _access_key, _secret_key)
# _request_headers = _request_headers(token=_token)
# _system_id = _get_fqdn_id()
_system_id = system_id()
_common_names = [ _system_id, _system_id + '.private.thedns.cn', _system_id + '.public.thedns.cn']

def __create_ca():
    return _create_ca(request_headers=authorization_headers())
def create_cert():
    try:
        # make sure the CA been created already.
        __create_ca()
        # return _create_cert(request_headers=self.request_headers,common_names=self.common_names)
        data =  _create_cert(request_headers=authorization_headers(),common_names=_common_names)
        # common_name = self.common_names[0]
        config_dir = pathlib.Path.home() / '.devnull' / 'certs'
        pathlib.Path(config_dir).mkdir(parents=True, exist_ok=True)
        key_file = config_dir / 'key.pem'
        crt_file = config_dir / 'crt.pem'
        chain_file = config_dir / 'fullchain.pem'
        ca_file = config_dir / 'ca.pem'
        system_id_file = config_dir / 'system_id'
        ca_id_file = config_dir / 'ca_id'
        sans_file = config_dir / 'subject_alternative_names'
        properties_file = config_dir / 'properties'
        key_string_b64 = data['key']
        crt_string_b64 = data['crt']
        ca_string_b64 = data['ca']
        ca_id = data['ca_id']
        key_string = base64.b64decode(key_string_b64).decode()
        crt_string = base64.b64decode(crt_string_b64).decode()
        ca_string = base64.b64decode(ca_string_b64).decode()
        with crt_file.open('wt') as f:
            f.write(crt_string)
        with key_file.open('wt') as f:
            f.write(key_string)
        with chain_file.open('wt') as f:
            f.write(crt_string + '\n' + ca_string)
        with ca_file.open('wt') as f:
            f.write(ca_string)
        with system_id_file.open('wt') as f:
            f.write(_system_id + '\n')
        with sans_file.open('wt') as f:
            f.write('\n'.join(_common_names) + '\n')
        # with ca_id_file.open('wt') as f:
        #     f.write(ca_id)
        with properties_file.open('wt') as f:
            f.write(f"ca_id: {ca_id}\n"
                    f"ca_owner: {email()}\n"
                    f"system_id: {_system_id}\n"
                    f"signed_sans: {' '.join(_common_names)}\n"
                    )
        return {
            'key': key_file.as_posix(),
            'crt': crt_file.as_posix(),
            'full_chain': chain_file.as_posix(),
            'ca': ca_file.as_posix(),
            # 'system_id': _system_id,
            # 'ca_id': ca_id,
            'signed_sans': _common_names,
            'ca_url': 'https://devnull.cn/getca/'+ ca_id
        }
    except:
        return {
            'rc': 205,
            'msg': 'unhealthy service.'
        }
