from .api_client import APIClient

class ImageGeneration:
    def __init__(self, api_client):
        self.api_client = api_client

    def get_image_gen(self, image_data):
        return self.api_client.post('get_relight', json_data=image_data)
