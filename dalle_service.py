import requests

class DALLEService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/davinci/images"

    def generate_image(self, description):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'prompt': description,
            'max_tokens': 50
        }
        response = requests.post(self.base_url, headers=headers, json=data)
        image_url = response.json()['url']
        return image_url
