from .api_client import APIClient
from .image_generation import ImageGeneration

class InstantLightSDK:
    def __init__(self, base_url, api_key, email):
        api_client = APIClient(base_url, api_key, email)
        self.image_generation = ImageGeneration(api_client)
