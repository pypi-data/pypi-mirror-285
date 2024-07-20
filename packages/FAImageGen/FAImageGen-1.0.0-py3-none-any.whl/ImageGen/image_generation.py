import base64
from io import BytesIO
from PIL import Image
from .api_client import APIClient

class ImageGeneration:
    def __init__(self, client: APIClient):
        self.client = client

    def get_image_gen(self, image_path, prompt):
        # Convert image to base64
        image_base64 = self.image_to_base64(image_path)

        # Define the image data payload
        image_data = {
            "image": image_base64,
            "prompt": prompt
        }

        # Make the API call
        response = self.client.post('Image-gen', json_data=image_data)

        # Print response keys for debugging
        print("Response Keys:", response.keys())

        # Save the image and mask image if they exist in the response
        if 'image' in response:
            image_data = response['image']
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            image.save("output_image.png")
            print("Image retrieved and saved as output_image.png.")
        else:
            print("Response does not contain 'image'")

        return response

    @staticmethod
    def image_to_base64(image_path):
        with Image.open(image_path) as img:
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
