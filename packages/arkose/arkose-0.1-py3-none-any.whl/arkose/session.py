import requests
from urllib.parse import unquote
import os

class FuncaptchaSession(object):
    def __init__(self, data, headers=None, proxy=None):
        self.data = data
        self.headers = headers if headers else {}
        self.proxy = proxy if proxy else None
        self._challenge_response = None 

    def get_challenge(self):
        if not self._challenge_response:
            headers = self.headers.copy() 
            headers.update({
                'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0",
                'Accept-Language': "en-US,en;q=0.5",
                'Accept': "*/*",
                'Cache-Control': "no-cache",
                'X-Requested-With': "XMLHttpRequest",
                'X-NewRelic-Timestamp': "170738000608618",
                'Sec-GPC': "1",
                'Sec-Fetch-Dest': "empty",
                'Sec-Fetch-Mode': "cors",
                'Sec-Fetch-Site': "same-origin",
                'Referer': f"https://roblox-api.arkoselabs.com/fc/assets/ec-game-core/game-core/1.22.0/standard/index.html?session={self.data['token']}&r=us-east-1&meta=3&metabgclr=transparent&metaiconclr=%23757575&maintxtclr=%23b8b8b8&guitextcolor=%23474747&pk=476068BF-9607-4799-B53D-966BE98E2B81&at=40&ag=101&cdn_url=https%3A%2F%2Froblox-api.arkoselabs.com%2Fcdn%2Ffc&lurl=https%3A%2F%2Faudio-us-east-1.arkoselabs.com&surl=https%3A%2F%2Froblox-api.arkoselabs.com&smurl=https%3A%2F%2Froblox-api.arkoselabs.com%2Fcdn%2Ffc%2Fassets%2Fstyle-manager&theme=default"
            })

            response = requests.post(
                "https://roblox-api.arkoselabs.com/fc/gfct/",
                headers=headers,
                proxies=self.proxy,
                data={
                    "token": self.data["token"],
                    "sid": "us-west-2",
                    "render_type": "canvas",
                    "lang": "",
                    "isAudioGame": False,
                    "is_compatibility_mode": False,
                    "apiBreakerVersion": "green",
                    "analytics_tier": 40
                }
            )

            try:
                res = response.json()
                self._challenge_response = res["game_data"]
            except ValueError:
                print("Failed to parse challenge response as JSON")
                self._challenge_response = {}

        return self._challenge_response

    def reload_challenge(self):
        # Reset the cached challenge response
        self._challenge_response = None
        return self.get_challenge()

    def challenge_name(self):
        response = self.get_challenge()
        return response['instruction_string']
    
    def wavecount(self):
        response = self.get_challenge()
        challenge_images = response["customGUI"]['_challenge_imgs']
        return len(challenge_images)
    
    def get_challenge_links(self):
        response = self.get_challenge()
        return response["customGUI"]['_challenge_imgs']

    def download_images(self, save_path='challenge_images'):
        response = self.get_challenge()
        challenge_images = response["customGUI"]['_challenge_imgs']

        if not challenge_images:
            print("No challenge images found in the response")
            return

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        downloaded_count = 0
        for i, img_url in enumerate(challenge_images):
            img_response = requests.get(img_url, proxies=self.proxy)
            if img_response.status_code == 200:
                img_path = os.path.join(save_path, f'image_{i}.png')
                with open(img_path, 'wb') as file:
                    file.write(img_response.content)
                downloaded_count += 1

        print(f"Downloaded {downloaded_count} images")

    @property
    def name(self):
        response = self.get_challenge()
        return response.get('game_data', {}).get('challengeID', 'No challengeID found')

    @property
    def instruction_string(self):
        return self.get_challenge().get('instruction_string', 'No instruction_string found')

    def download(self, save_path='images'):
        self.download_images(save_path)

class RequestSession(object):
    def __init__(self, token, headers=None, proxy=None):
        self.token = token
        self.headers = headers if headers else {}
        self.proxy = proxy if proxy else None

    def parse_full_token(self):
        token = "token=" + self.token
        assoc = {}

        for field in token.split("|"):
            s = field.partition("=")
            key, value = s[0], s[-1]
            assoc[key] = value

        return assoc

    def request(self):
        data = self.parse_full_token()
        headers = self.headers.copy()  # Use copy to avoid modifying the original headers
        headers.update({
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0",
            'Accept-Language': "en-US,en;q=0.5",
            'Cache-Control': "no-cache",
            'Sec-Fetch-Dest': "empty",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Site': "same-origin",
            'Referer': f"{unquote(data['surl'])}/v2/2.8.2/enforcement.5a2a74a1ccf39f6b2719561c6aad2dcc.html"
        })

        response = requests.get(
            f"https://roblox-api.arkoselabs.com/fc/gc/?token={data['token']}",
            headers=headers,
            proxies=self.proxy
        )

        return FuncaptchaSession(
            data=data,
            headers=self.headers,
            proxy=self.proxy
        )