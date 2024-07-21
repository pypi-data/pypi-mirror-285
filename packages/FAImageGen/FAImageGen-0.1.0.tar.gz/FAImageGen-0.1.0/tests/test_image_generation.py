import unittest
import base64
from io import BytesIO
from PIL import Image
from sdk import InstantLightSDK  # Ensure this import matches your SDK module structure
import logging

logging.basicConfig(level=logging.DEBUG)

def image_to_base64(image_path):
    with Image.open(image_path) as img:
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

class TestImageGeneration(unittest.TestCase):
    def setUp(self):
        self.sdk = InstantLightSDK(
            base_url='https://api.fotographer.ai/instantLight',
            api_key='your api key',
            email='your email'
        )

    def test_get_image_gen(self):
        # Convert images to base64
        foreground_image64 = image_to_base64('C:/Users/Saliou Kane/Downloads/perfume_black.png')
        background_image64 = image_to_base64('C:/Users/Saliou Kane/Downloads/perfume_black.png')

        # Define the image data
        image_data = {
            "foreground_image64": foreground_image64,
            "background_image64": background_image64,
            "prompt": "",
            "mode": 0,
            "prompt_strength": 4.0,
            "inf_factor": 1.00,
            "mask_strength": 0.5,
            "image_width": 1400,
            "image_height": 1400,
            "additional_prompt": "",
            "negative_prompt": "",
            "lights": []
        }

        image_request = {
            "image": foreground_image64,
            "mode": 3,
            "prompt": "on top of a mountain beautiful sunny background"
        }

        # Create a copy of the dictionary excluding the specified keys
        filtered_data = {k: v for k, v in image_data.items() if k not in ["foreground_image64", "background_image64"]}

        # Print the filtered data for debugging
        print("Filtered Data Keys:", filtered_data.keys())

        # Make the API call using the SDK
        #response = self.sdk.image_generation.get_image_gen(image_data)
        response = self.sdk.image_generation.get_image_gen(image_data)
        
        # Print response keys for debugging
        print("Response Keys:", response.keys())
        
        # Print the keys at all levels of the response for debugging
        for key, value in response.items():
            if isinstance(value, dict):
                print(f"Response[{key}] Keys: {value.keys()}")
        
        # Save the image and mask image if they exist in the response
        if 'image' in response:
            image_data = response['image']
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            image.save("output_image.png")
            print("Image retrieved and saved as output_image.png.")
            
            if 'mask_image' in response:
                mask_data = response['mask_image']
                mask_bytes = base64.b64decode(mask_data)
                mask_image = Image.open(BytesIO(mask_bytes))
                mask_image.save("output_mask_image.png")
                print("Mask retrieved and saved as output_mask_image.png.")
        else:
            self.fail("Response does not contain 'image'")
        
        # Save the full response to a log file
        with open("response_log.txt", "w") as log_file:
            log_file.write(str(response))
        
        # Assertions based on expected response structure
        self.assertIn('image', response)

if __name__ == '__main__':
    unittest.main()
