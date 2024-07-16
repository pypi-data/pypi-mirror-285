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

def _get_uuid():
    try:
        with open('/etc/machine-id', 'r') as f:
            rr_string = hashlib.md5(f.read().encode()).hexdigest()
    except:
        rr_string = hashlib.md5(socket.gethostname().encode()).hexdigest()
    return rr_string

def _get_public_ip():
    return requests.get('https://devnull.cn/ip').json()['origin']


def _validate_input(input_data=None):
    try:
        if type(input_data) != str:
            return False
        else:
            return True
    except:
        return False

def _update(request_headers=None, key_string:str=None, value_string:str=None, pulse_id:str=None):
    if not _validate_input(key_string) or not _validate_input(value_string):
        return 'Invalid key/value/id. Only strings allowed.'
    payload = json.dumps({
        "pulse_id": pulse_id,
        "key_string": key_string,
        "value_string": value_string
    })
    response = requests.post('https://devnull.cn/pulse', headers=request_headers, data=payload)
    return response.json()


def _get(request_headers=None, pulse_id:str=None):
    if not _validate_input(pulse_id):
        return 'Invalid pulse_id. Only string allowed.'
    url = f"https://devnull.cn/pulse/{pulse_id}"
    response = requests.get(url, headers=request_headers)
    return response.json()