from .api_client import APIClient
from .image_generation import ImageGeneration

class ImageGen:
    def __init__(self, base_url, api_key, email):
        self.client = APIClient(base_url, api_key, email)
        self.image_generation = ImageGeneration(self.client)
