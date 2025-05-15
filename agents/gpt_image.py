import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional, Dict, Union
from base64 import b64decode
from pathlib import Path

# Load environment variables
load_dotenv()

class AvatarGenerator:
    def __init__(self):
        """Initialize the AvatarGenerator with OpenAI client"""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.default_style = ""
    
    def _construct_prompt(self, physical_description: str, style: Optional[str] = None) -> str:
        """Construct a clean prompt for realistic avatar generation"""
        style_prompt = style if style else self.default_style
        style_suffix = f". {style_prompt}" if style_prompt else ""
        return f"A photorealistic portrait of {physical_description}{style_suffix}"

    def generate_avatar(
        self,
        physical_description: str,
        style: Optional[str] = None,
        size: str = "1024x1024",
        save_path: Optional[str] = None
    ) -> Dict[str, Union[str, bytes]]:
        """Generate an avatar image using 4o-images"""
        
        try:
            prompt = self._construct_prompt(physical_description, style)
            
            # First get URL for immediate access
            url_response = self.client.images.generate(
                model="4o-images-v1",
                prompt=prompt,
                size=size,
                n=1
            )
            
            result = {
                'url': url_response.data[0].url
            }
            
            # If save_path is provided, get base64 data and save
            if save_path:
                b64_response = self.client.images.generate(
                    model="4o-images-v1",
                    prompt=prompt,
                    size=size,
                    n=1,
                    response_format="b64_json"
                )
                
                image_data = b64decode(b64_response.data[0].b64_json)
                result['base64_image'] = b64_response.data[0].b64_json
                
                # Create directory if it doesn't exist
                save_dir = Path(save_path).parent
                save_dir.mkdir(parents=True, exist_ok=True)
                
                # Save the image
                with open(save_path, 'wb') as f:
                    f.write(image_data)
                result['file_path'] = save_path
            
            return result

        except Exception as e:
            raise Exception(f"Error generating avatar: {str(e)}")


# Example usage:
if __name__ == "__main__":
    generator = AvatarGenerator()
    result = generator.generate_avatar(
        physical_description="An Indonesian young woman with long brown hair, wearing traditional batik with a warm, natural smile",
        save_path="/Users/berwyn/Desktop/ad/agents/gpt_image.png"
    )
    print(f"Image URL: {result['url']}")
    print(f"Image saved to: {result['file_path']}")
    result = generator.generate_avatar(
        physical_description="An Indonesian young woman with long brown hair, wearing batik and with a warm smile",
        save_path="/Users/berwyn/Desktop/ad/agents/gpt_image.png"
    )
    print(f"Image saved to: {result['file_path']}")
