from openai import OpenAI
from .runway import generate_video_from_image
from .broll_image import generate_broll_image
from typing import Dict, Any, List
import os
import base64

client = OpenAI()

# Runway prompt keywords
RUNWAY_CAMERA_STYLES = [
    "low angle", "high angle", "overhead", "FPV", "handheld", "wide angle",
    "close up", "macro cinematography", "over the shoulder", "tracking",
    "establishing wide", "50mm lens", "SnorriCam", "realistic documentary", "camcorder"
]

RUNWAY_LIGHTING = [
    "diffused lighting", "silhouette", "lens flare", "back lit", "side lit",
    "venetian lighting"
]

RUNWAY_MOVEMENT_SPEEDS = [
    "dynamic motion", "slow motion", "fast motion", "timelapse"
]

RUNWAY_MOVEMENT_TYPES = [
    "grows", "emerges", "explodes", "ascends", "undulates", "warps",
    "transforms", "ripples", "shatters", "unfolds", "vortex"
]

RUNWAY_STYLES = [
    "moody", "cinematic", "iridescent", "home video VHS", "glitchcore"
]

def convert_to_static_prompt(dynamic_description: str) -> str:
    """Convert a dynamic video description into a static image prompt using GPT"""
    prompt = f"""
    Convert this dynamic video scene description into a static image prompt that captures the most impactful moment.
    Focus on describing a single frame that best represents the scene, including details about composition, lighting, and focus.
    Make it suitable for DALL-E image generation.

    Video description:
    {dynamic_description}

    Respond with just the static image description, no additional text.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional photographer and art director. Convert dynamic video descriptions into compelling static image prompts."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

def convert_to_runway_prompt(dynamic_description: str) -> str:
    """Convert a dynamic video description into a Runway-compliant motion prompt"""
    prompt = f"""
    Convert this video scene description into a Runway-compliant motion prompt.
    Focus on describing the motion and cinematography, not the contents of the image.
    Use appropriate keywords from these categories (only when relevant):
    - Camera styles: {', '.join(RUNWAY_CAMERA_STYLES)}
    - Lighting: {', '.join(RUNWAY_LIGHTING)}
    - Movement speeds: {', '.join(RUNWAY_MOVEMENT_SPEEDS)}
    - Movement types: {', '.join(RUNWAY_MOVEMENT_TYPES)}
    - Style and aesthetic: {', '.join(RUNWAY_STYLES)}

    Video description:
    {dynamic_description}

    Respond with just the motion prompt, no additional text. Prompt should be purely descriptive, not conversational.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional cinematographer. Create concise motion prompts focusing on camera movement, lighting, and motion effects."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

def generate_broll_scene(dynamic_description: str, output_path: str) -> Dict[str, Any]:
    """Generate both an image and video for a b-roll scene from a dynamic description"""
    try:
        # Convert descriptions for both image and video
        static_description = convert_to_static_prompt(dynamic_description)
        motion_prompt = convert_to_runway_prompt(dynamic_description)
        
        print(f"\n🎨 Generated static prompt: {static_description}")
        print(f"\n🎥 Generated motion prompt: {motion_prompt}")
        
        # Generate the image in portrait mode
        image_b64 = generate_broll_image(
            scene_description=static_description,
            scene_type="product",
            quality="hd",
            size="1024x1792"  # Portrait 9:16 ratio
        )
        
        # Generate the video using the Runway-compliant prompt
        video_path = generate_video_from_image(
            image_base64=image_b64,
            output_path=output_path,
            prompt_text=motion_prompt,
            ratio='720:1280'  # Portrait 9:16 ratio (720p)
        )
        
        return {
            'success': True,
            'static_description': static_description,
            'motion_prompt': motion_prompt,
            'video_path': video_path,
            'image_base64': image_b64
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    # Example usage
    dynamic_description = "Show a close-up of the Acqua Pure Smart bottle cap in action. As a finger lightly taps the cap, a soft blue glow emanates from the UV-C light, symbolizing the sterilization process. The focus is on the cap and the light effect, showcasing its bacteria-killing feature."
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    result = generate_broll_scene(
        dynamic_description=dynamic_description,
        output_path="output/bottle_cap.mp4"
    )
    
    if result['success']:
        print(f"\n✨ Generated video saved to: {result['video_path']}")
        print(f"\n📝 Static description: {result['static_description']}")
        print(f"\n🎥 Motion prompt: {result['motion_prompt']}")
        
        # Save the image too
        img_data = base64.b64decode(result['image_base64'])
        with open('output/bottle_cap.png', 'wb') as f:
            f.write(img_data)
        print(f"\n📁 Saved image to: output/bottle_cap.png")
    else:
        print(f"\n❌ Error: {result['error']}")
