from openai import OpenAI
from broll_generation.runway import generate_video_from_image
from broll_generation.broll_image import generate_broll_image
from typing import Dict, Any, List
import os
import base64
from fal import try_on
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

# def convert_to_runway_prompt() -> str:
#     """Convert a dynamic video description into a Runway-compliant motion prompt"""
#     prompt = f"""
#     Convert this video scene description into a Runway-compliant motion prompt. Focus on describing the motion and cinematography, not the contents of the image. Use appropriate keywords from these categories (only when relevant):
#     - Camera styles: {', '.join(RUNWAY_CAMERA_STYLES)}
#     - Lighting: {', '.join(RUNWAY_LIGHTING)}
#     - Movement speeds: {', '.join(RUNWAY_MOVEMENT_SPEEDS)}
#     - Movement types: {', '.join(RUNWAY_MOVEMENT_TYPES)}
#     - Style and aesthetic: {', '.join(RUNWAY_STYLES)}

#     Video description: A person with a cloth moves around to showcase the outfit, turning and adjusting the fabric.

#     Respond with just the motion prompt, no additional text. Prompt should be purely descriptive, not conversational.
#     """

#     response = client.chat.completions.create(
#         model="gpt-4",
#         messages=[
#             {"role": "system", "content": "You are a professional cinematographer. Create concise motion prompts focusing on camera movement, lighting, and motion effects."},
#             {"role": "user", "content": prompt}
#         ],
#         temperature=0.7
#     )

#     return response.choices[0].message.content.strip()

# import requests

def generate_broll_scene(image_base64: str, output_path: str) -> Dict[str, Any]:
    """Generate both an image and video for a b-roll scene from a dynamic description. Downloads the video if necessary."""
    try:
        # Convert descriptions for both image and video
        motion_prompt = convert_to_runway_prompt()

        print(f"\n Generated motion prompt: {motion_prompt}")

        # Generate the video using the Runway-compliant prompt
        video_path = generate_video_from_image(
            image_base64=image_base64,
            output_path=output_path,
            prompt_text=motion_prompt,
            ratio='720:1280'  # Portrait 9:16 ratio (720p)
        )

        # Download if video_path is a URL
        if isinstance(video_path, str) and video_path.startswith("http"):
            print(f"Downloading video from {video_path} to {output_path}...")
            r = requests.get(video_path, stream=True)
            r.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            video_path = output_path

        return {
            'success': True,
            'motion_prompt': motion_prompt,
            'video_path': video_path
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    model_image_path = './model.jpeg'
    garment_image_path = './cloth.png'
    base64_str = try_on(model_image_path, garment_image_path)
    print("Base64 output:", base64_str)
    
    generate_broll_scene(base64_str, "output/broll.mp4")