import json
import requests
from .utils import getBda, default_ua, get_float
import random

def is_token_supress(token):
    token_parts = token.split('|')
    token_dict = dict(part.split('=', 1) for part in token_parts if '=' in part)
    return token_dict.get('sup') == '1'

async def getTOKEN(surl, publicKey, site, data=None, headers=None, proxy=None):
    if headers is None:
        headers = {}
    if "User-Agent" not in headers:
        headers["User-Agent"] = default_ua
    headers["Accept-Language"] = "en-US,en;q=0.9"
    headers["Sec-Fetch-Site"] = "same-origin"
    headers["Accept"] = "*/*"
    headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
    headers["Sec-Fetch-Mode"] = "cors"

    if site is not None:
        headers["Origin"] = surl
        headers["Referer"] = f"{surl}/v2/2.8.2/enforcement.5a2a74a1ccf39f6b2719561c6aad2dcc.html"
    
    bda = getBda(default_ua, site, surl)
    
    rnd = get_float()
    blob = data.get('blob') if data else None
    
    # Construct payload
    payload = {
        "bda": bda,
        "public_key": publicKey,
        "site": site if site else None,
        "userbrowser": default_ua,
        "capi_version": "2.8.2",
        "capi_mode": "inline",
        "style_theme": "default",
        "rnd": rnd,
        "data[blob]": blob,
        "language": "en"
    }
    
    try:
        tok = requests.post(f"{surl}/fc/gt2/public_key/{publicKey}",
                            headers=headers,
                            data=payload,
                            proxies=proxy).json()
        
        return tok
    except Exception as e:
        print(f"An error occurred: {e}")
        return None