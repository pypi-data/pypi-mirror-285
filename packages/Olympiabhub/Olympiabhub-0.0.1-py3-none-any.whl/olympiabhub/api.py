import requests

class OlympiaAPI:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.olympia.bhub.cloud"
        self.Nubonyxia_proxy = "172.16.0.53:3128"
        self.Nubonyxia_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"

    def _get_headers(self):
        return {
            "accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def ChatNubonyxia(self, model_name: str, prompt: str) -> dict:
        url = f"{self.base_url}/generate"
        headers = self._get_headers()
        data = {"model": model_name, "prompt": prompt}

        proxies = {
            "http": self.Nubonyxia_proxy,
            "https": self.Nubonyxia_proxy
        }

        session = requests.Session()
        session.get_adapter("https://").proxy_manager_for(f"http://{self.Nubonyxia_proxy}").proxy_headers[
            "User-Agent"
        ] = self.Nubonyxia_user_agent
        session.proxies.update(proxies)

        try:
            response = session.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if response is not None:
                print(f"Response status code: {response.status_code}")
                print(f"Response text: {response.text}")
            raise

    def Chat(self, model_name: str, prompt: str) -> dict:
        url = f"{self.base_url}/generate"
        headers = self._get_headers()
        data = {"model": model_name, "prompt": prompt}

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if response is not None:
                print(f"Response status code: {response.status_code}")
                print(f"Response text: {response.text}")
            raise

