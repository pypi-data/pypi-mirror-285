import json
import requests
import socket
import hashlib

def _get_private_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    private_ip_string = s.getsockname()[0]
    s.close()
    return private_ip_string

def _get_fqdn_id():
    try:
        with open('/etc/machine-id', 'r') as f:
            rr_string = hashlib.md5(f.read().encode()).hexdigest()
    except:
        rr_string = hashlib.md5(socket.gethostname().encode()).hexdigest()
    return rr_string

def _get_ca(request_headers=None):
    payload = json.dumps({
        "action_type": 'read',
        "cert_type": 'root'
    })
    print(f"Headers: {request_headers}")
    response = requests.post('https://devnull.cn/pca', headers=request_headers, data=payload)
    return response.json()

def _get_certs(request_headers=None):
    payload = json.dumps({
        "action_type": 'list',
    })
    print(f"Headers: {request_headers}")
    response = requests.post('https://devnull.cn/pca', headers=request_headers, data=payload)
    return response.json()


def _create_ca(request_headers=None):
    # first check if ca exists already:
    payload = json.dumps({
        "action_type": 'read',
        "cert_type": 'root'
    })
    response = requests.post('https://devnull.cn/pca', headers=request_headers, data=payload)
    if response.json()['rc'] == 200:
        # print(f"Private CA exists...")
        return response.json()
    else:
        # print(f"Private CA does not exist, creating...")
        payload = json.dumps({
            "action_type": 'create',
            "cert_type": "root"
        })
        response = requests.post('https://devnull.cn/pca', headers=request_headers, data=payload)
        return response.json()

# def _create_cert_disabled(request_headers=None, common_name=None):
#     payload = json.dumps({
#         'action_type': 'create',
#         'cert_type': 'common',
#         'common_name': common_name
#     })
#     response = requests.post('https://devnull.cn/pca', headers=request_headers, data=payload)
#     return response.json()

def _create_cert(request_headers=None, common_names=None):
    payload = json.dumps({
        'action_type': 'create',
        'cert_type': 'common_sans',
        'common_names': common_names
    })
    response = requests.post('https://devnull.cn/pca', headers=request_headers, data=payload)
    return response.json()