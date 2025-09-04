import requests
from PIL import Image
from langchain_core.tools import tool
from transformers import BlipProcessor, BlipForConditionalGeneration

class ImageCaptioning:
    def __init__(self):
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to("cuda")
    
    def convert_raw_image(self, img_url: str) -> Image.Image:
        if img_url.startswith(('http://', 'https://')):
            return Image.open(requests.get(img_url, stream=True).raw).convert('RGB')
        else:
            # Handle local file paths
            return Image.open(img_url).convert('RGB')
    
    def conditional_image_captioning(self, text: str, raw_image: Image.Image) -> str:
        #conditional image captioning means we are providing a text prompt to the model
        inputs = self.processor(raw_image, text, return_tensors="pt").to("cuda")
        out = self.model.generate(**inputs)
        return self.processor.decode(out[0], skip_special_tokens=True)

image_captioning = ImageCaptioning()

@tool
def get_image_caption(img_url: str, prompt: str = "An image of") -> str:
    """Get the caption of an image to understand the environment the user is in.
        Args:
            img_url: The URL or local file path of the image to get the caption of
            prompt: The prompt to use to help the model understand the image. Default is "An image of".
        Returns:
            A string with the caption of the image content
    """
    raw_image = image_captioning.convert_raw_image(img_url)
    return image_captioning.conditional_image_captioning(prompt, raw_image)

def get_local_context_tools():
    """Get all the local context tools for the agent"""
    tools = []
    tools.append(get_image_caption)
    return tools
