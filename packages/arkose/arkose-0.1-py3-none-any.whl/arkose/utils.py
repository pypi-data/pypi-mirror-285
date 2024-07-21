import base64
import json
import time
import random
from .fingerprint import getFingerprint, prepareFe, prepareF, getEnhancedFingerprint
from .murmur import murmur_hash
from .crypt import encrypt

default_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"

def random_hex(length=32):
    return ''.join(random.choice('0123456789abcdef') for _ in range(length))

def get_float():
    return random.uniform(0, 1)


def getBda(userAgent, site, surl):
    fp = getFingerprint()
    fe = prepareFe(fp)
    bda = [
        {"key": "api_type", "value": "js"},
        {"key": "f", "value": murmur_hash(prepareF(fp), 31)},
        {"key": "n", "value": base64.b64encode(str(round(time.time())).encode()).decode()},
        {"key": "wh", "value": f"{random_hex()}|{random_hex()}"},
        {"key": "enhanced_fp", "value": getEnhancedFingerprint(site, surl)},
        {"key": "fe", "value": fe},
        {"key": "ife_hash", "value": murmur_hash(', '.join(fe), 38)},
        {"key": "jsbd", "value": json.dumps({
            "HL": 3,
            "NCE": True,
            "DT": "",
            "NWD": "false",
            "DOTO": 1,
            "DMTO": 1,
        })},
    ]
    key = userAgent + str(round(time.time() // 21600))
    s = json.dumps(bda, separators=(',', ':'))
    encrypted = encrypt(s, key)
    return base64.b64encode(encrypted.encode()).decode()