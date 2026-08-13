import requests
import yaml

class CloudflareVerifier:
    def __init__(self):
        with open("config/settings.yml", "r") as f:
            self.cfg = yaml.safe_load(f)

        self.headers = {
            "Authorization": f"Bearer {self.cfg['cloudflare']['api_token']}"
        }

    def verify_all(self):
        return (
            self.verify_zone() and
            self.verify_account()
        )

    def verify_zone(self):
        url = f"https://api.cloudflare.com/client/v4/zones/{self.cfg['cloudflare']['zone_id']}"
        r = requests.get(url, headers=self.headers)
        return r.json().get("success", False)

    def verify_account(self):
        url = f"https://api.cloudflare.com/client/v4/accounts/{self.cfg['cloudflare']['account_id']}"
        r = requests.get(url, headers=self.headers)
        return r.json().get("success", False)
