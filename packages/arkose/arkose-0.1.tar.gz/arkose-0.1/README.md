# Arkose (Funcaptcha)

Arkose is a Python package designed to interact with Funcaptcha (Arkose Labs) to get CAPTCHA challenges programmatically. This package is useful for automating the interaction with Funcaptcha's challenge system, including token retrieval, challenge handling, and image downloading.

## Installation

To install Arkose, use pip:

```bash
pip install arkose
```

## Usage

Here is a basic example of how to use the `arkose` package to interact with Funcaptcha:

```python
import asyncio
import requests
import json
import base64
import arkose

async def main():
    headers1 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "https://www.roblox.com",
    }
    gxcsrf = requests.post("https://auth.roblox.com/v2/signup", headers=headers1)
    token1 = gxcsrf.headers.get("x-csrf-token")
    
    if not token1:
        print("No x-csrf-token found in headers.")
        return

    headers2 = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Roblox/WinInet",
        "X-CSRF-TOKEN": token1,
    }
    datamicx = {
        "username": "dsads",
        "password": "dasdsadas",
    }
    gblob = requests.post("https://auth.roblox.com/v2/signup", headers=headers2, json=datamicx)
    
    # Extract and decode rblx-challenge-metadata from headers
    rblx_challenge_metadata = gblob.headers.get("rblx-challenge-metadata")
    if rblx_challenge_metadata:
        rblx_challenge_metadata = json.loads(base64.b64decode(rblx_challenge_metadata).decode())
    else:
        print("No rblx-challenge-metadata found in headers.")
        return

    fcid = gblob.headers.get("rblx-challenge-id")
    if not fcid:
        print("No rblx-challenge-id found in headers.")
        return

    blob = rblx_challenge_metadata.get("dataExchangeBlob")
    if not blob:
        print("No dataExchangeBlob found in rblx-challenge-metadata.")
        return

    token_response = await arkose.getTOKEN(
        surl="https://roblox-api.arkoselabs.com",
        publicKey="476068BF-9607-4799-B53D-966BE98E2B81",
        site="https://www.roblox.com/login",
        data={"blob": blob},
        headers={"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
    )
    
    token = token_response.get('token')
    if not token:
        print("No token found in response.")
        return

    print(token)

    if arkose.is_token_supress(token):
        print("Token is supress")
        return
    
    fc = arkose.RequestSession(token).request()
    
    challenge = fc.get_challenge()
    
    fc.download_images(save_path="./challenge")
    print(f"Challenge name: {fc.challenge_name()}")
    print(f"Challenge wave: {fc.wavecount()}")
    print(f"Challenge link: {fc.get_challenge_links()}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Functions

- `arkose.getTOKEN(surl, publicKey, site, data, headers)`: Retrieves a token from the Arkose API.
- `arkose.is_token_supress(token)`: Checks if the token is suppressed.
- `arkose.RequestSession(token)`: Creates a session for making requests with the provided token.

## Requirements

- `requests`
- `asyncio`
- `json`
- `base64`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or feedback, please open an issue on the [GitHub repository](https://github.com/Micxzy/arkose).
