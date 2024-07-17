import pathlib
import configparser
import hashlib
import requests
import json
import os

def _credentials():
    try:
        if 'DEVNULL_ACCESS_KEY' and 'DEVNULL_SECRET_KEY' and 'DEVNULL_EMAIL' in os.environ:
            accesskey = os.environ['DEVNULL_ACCESS_KEY']
            secretkey = os.environ['DEVNULL_SECRET_KEY']
            email = os.environ['DEVNULL_EMAIL']
        else:
            config_dir = pathlib.Path.home() / '.devnull'
            pathlib.Path(config_dir).mkdir(parents=True, exist_ok=True)
            _c = config_dir / 'credentials'
            with _c.open('r') as f:
                config = configparser.ConfigParser()
                config.read_file(f)
                accesskey = config['default']['accesskey']
                secretkey = config['default']['secretkey']
                email = config['default']['email']
    except:
        accesskey = 'j6QWLQhtUoNkTZLmzPtjHzm9'
        secretkey = '89GNI4UGgBxLdgELkvYKB6EP'
        email = 'ca-by-devnull@outlook.com'
    return accesskey, secretkey, email


def _token(email, access_key, secret_key):
    hashed_access_key = hashlib.sha256(access_key.encode()).hexdigest()
    hashed_secret_key = hashlib.sha256(secret_key.encode()).hexdigest()
    hashed_email = hashlib.md5(email.encode()).hexdigest()
    _plain = hashed_access_key + hashed_secret_key
    _password = hashlib.sha256(_plain.encode()).hexdigest()
    # print(_password)
    data = json.dumps({
        'email': email,
        'checksum': hashed_email,
        'accesskey': access_key,
        'password': _password,
        'resource_type': 'token'
    })
    headers = {'Content-Type': 'application/json'}
    _= requests.post('https://devnull.cn/identity', data=data, headers=headers).json()
    token_string = 'Bearer ' + _['token']
    return token_string

def _request_headers(token=None):
    return {
        'Authorization': token,
        'Content-Type': 'application/json'
    }