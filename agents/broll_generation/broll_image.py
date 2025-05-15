import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class BrollImageGenerator:
    def __init__(self):
        """Initialize the BrollImageGenerator with OpenAI client"""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.default_style_keywords = [
            "photorealistic",
            "high detail",
            "professional photography",
            "4K resolution",
            "natural lighting"
        ]
    
    def _construct_prompt(self, scene_description: str, style_keywords: Optional[list] = None) -> str:
        """Construct a clean prompt for realistic image generation"""
        keywords = style_keywords if style_keywords else self.default_style_keywords
        style_suffix = ", " + ", ".join(keywords) if keywords else ""
        return f"{scene_description}{style_suffix}"

    def generate_image(
        self,
        scene_description: str,
        style_keywords: Optional[list] = None,
        size: str = "1024x1024",
        quality: str = "hd"
    ) -> str:
        """Generate a realistic image using DALL-E 3 and return base64 string"""
        
        try:
            prompt = self._construct_prompt(scene_description, style_keywords)
            print(f"\nGenerating image with prompt: {prompt}")
            
            # Generate image with DALL-E 3
            response = self.client.images.generate(
                model="gpt-image-1",
                prompt=f"{prompt}. Compose this as a vertical/portrait shot with 9:16 aspect ratio.",
                size=size,
                quality=quality,
                n=1,
                response_format="b64_json"  # Always request base64
            )
            
            # Return the base64 string
            return response.data[0].b64_json

        except Exception as e:
            raise Exception(f"Error generating image: {str(e)}")


def generate_broll_image(
    scene_description: str,
    scene_type: str = "product",  # product, lifestyle, environment
    size: str = "1024x1792",  # Portrait 9:16 ratio (1024x1792)
    **kwargs
) -> str:
    """Convenience function to generate a b-roll image"""
    generator = BrollImageGenerator()
    
    # No need for file operations since we're just returning the URL
    
    # Add scene-specific style keywords
    style_keywords = kwargs.pop('style_keywords', [])
    if scene_type == "product":
        style_keywords.extend([
            "product photography",
            "studio lighting",
            "commercial quality",
            "white background",
            "professional product shot"
        ])
    elif scene_type == "lifestyle":
        style_keywords.extend([
            "lifestyle photography",
            "candid moment",
            "natural environment",
            "authentic scene",
            "real life setting"
        ])
    elif scene_type == "environment":
        style_keywords.extend([
            "environmental photography",
            "wide angle",
            "establishing shot",
            "scenic view",
            "location photography"
        ])
    
    try:
        generator = BrollImageGenerator()
        
        # Use the provided scene description directly
        
        return generator.generate_image(
            scene_description=scene_description,
            style_keywords=style_keywords,
            **kwargs
        )

    except Exception as e:
        raise Exception(f"Error generating image: {str(e)}")


# Example usage:
if __name__ == "__main__":
    static_description = "A sleek stainless steel water bottle cap with a soft blue UV light glowing from within, captured in a dramatic close-up against a dark background. The cap's modern design and the ethereal blue glow create a high-tech, premium aesthetic."
    try:
        # Example with a static image description
        b64_data = generate_broll_image(
            scene_description=static_description,
            scene_type="product",
            quality="hd",
            size="1024x1792"  # Portrait 9:16 ratio
        )
        print(f"\n✨ Generated base64 image data (first 50 chars): {b64_data[:50]}...")
        
        # Save the image
        img_data = base64.b64decode(b64_data)
        with open('test_output.png', 'wb') as f:
            f.write(img_data)
        print(f"📁 Saved test image to: test_output.png")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
