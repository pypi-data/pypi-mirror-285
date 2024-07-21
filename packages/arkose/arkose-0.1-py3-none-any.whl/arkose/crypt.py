import hashlib
import json
import string
import random
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

BLOCK_SIZE = 16

def generate_salt(length=8):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length)).encode()

def derive_key_and_iv(password, salt, key_length=32, iv_length=16):
    d = d_i = b''
    while len(d) < key_length + iv_length:
        d_i = hashlib.md5(d_i + password.encode() + salt).digest()
        d += d_i
    return d[:key_length], d[key_length:key_length + iv_length]

def encrypt(data, password):
    salt = generate_salt()
    key, iv = derive_key_and_iv(password, salt)

    data = pad(data.encode(), BLOCK_SIZE)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(data)

    encrypted_dict = {
        "ct": base64.b64encode(encrypted_data).decode('utf-8'),
        "iv": iv.hex(),
        "s": salt.hex()
    }
    return json.dumps(encrypted_dict, separators=(',', ':'))

# Example usage:
# encrypted = encrypt("your data here", "yourpassword")
# print(encrypted)
