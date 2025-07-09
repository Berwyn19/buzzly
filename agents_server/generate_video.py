#!/usr/bin/env python3
import os
from pathlib import Path
from typing import Dict, Any, List
import asyncio

from agents_server.ffmpeg.extract_audio import extract_audio
from agents_server.ffmpeg.transcribe import transcribe_audio
from agents_server.ffmpeg.wrapper import ffmpeg_merge
from agents_server.broll_generation.description_generator import generate_all_brolls
from agents_server.broll_generation.broll import generate_broll_scene, generate_broll_for_product
from agents_server.broll_generation.broll_image import generate_broll_image
from agents_server.script import GenerateScript
from agents_server.heygen import generate_avatar_video
from agents_server.zapcap import ZapCapCaptionGenerator
import base64
import uuid
from datetime import datetime




def ensure_dir(path: str) -> str:
    """Ensure directory exists and return it"""
    os.makedirs(path, exist_ok=True)
    return path

def generate_video_with_broll(
    input_video_path: str,
    output_dir: str = "output",
    final_output_name: str = "final_video.mp4",
    product_image_b64: str = None
) -> Dict[str, Any]:
    """
    Generate a video with B-roll scenes from an input video.
    
    Args:
        input_video_path: Path to the input video file
        output_dir: Directory to store all generated files
        final_output_name: Name of the final output video file
    
    Returns:
        Dictionary containing all the generated paths and metadata
    """
    try:
        # Create output directories
        temp_dir = ensure_dir(os.path.join(output_dir, "temp"))
        broll_dir = ensure_dir(os.path.join(output_dir, "broll"))
        
        # Extract audio from input video
        print("\n🎵 Extracting audio...")
        audio_path = os.path.join(temp_dir, "extracted_audio.wav")
        extract_audio(input_video_path, audio_path)
        
        # Transcribe the audio
        print("\n📝 Transcribing audio...")
        transcript = transcribe_audio(audio_path)
        
        # Generate B-roll descriptions
        print("\n✨ Generating B-roll descriptions...")
        broll_descriptions = generate_all_brolls(transcript)
        
        # Generate each B-roll scene
        broll_scenes = []
        successful_scenes = 0
        total_scenes = len(broll_descriptions)
        
        print(f"\n🎬 Generating {total_scenes} B-roll scenes...")
        for i, broll in enumerate(broll_descriptions):
            print(f"\n📽️ Scene {i+1}/{total_scenes}:")
            print(f"Description: {broll.description[:100]}...")
            
            # Generate the scene
            scene_path = os.path.join(broll_dir, f"broll_{i:03d}.mp4")
            if i != 0:
                result = generate_broll_scene(
                    dynamic_description=broll.description,
                    output_path=scene_path
                )
            else:
                result = generate_broll_for_product(
                    dynamic_description=broll.description,
                    output_path=scene_path,
                    product_image_b64=product_image_b64
                )
            
            if result['success']:
                broll.video_path = result['video_path']
                if i != 0:
                    broll.static_description = result['static_description']
                broll_scenes.append(broll)
                successful_scenes += 1
                print(f"✅ Scene {i+1} generated successfully")
            else:
                print(f"⚠️ Failed to generate scene {i+1}: {result['error']}")
        
        print(f"\n✨ Generated {successful_scenes}/{total_scenes} B-roll scenes successfully")
        
        # Convert broll scenes to format expected by ffmpeg_merge
        print("\n📝 B-roll scenes to merge:")
        for broll in broll_scenes:
            print(f"  - Time: {broll.start:.2f}s to {broll.end:.2f}s")
            print(f"    Video: {broll.video_path}")
        
        broll_data = [
            {
                'start': broll.start,
                'end': broll.end,
                'video_path': broll.video_path
            }
            for broll in broll_scenes
        ]
        
        # Merge everything together
        print("\n🎥 Merging final video...")
        final_output_path = os.path.join(output_dir, final_output_name)
        print(broll_data)
        ffmpeg_merge(
            main_video=input_video_path,
            broll_data=broll_data,
            output_path=final_output_path
        )
        
        return {
            'success': True,
            'input_video': input_video_path,
            'final_video': final_output_path,
            'transcript': transcript,
            'broll_scenes': broll_scenes,
            'temp_dir': temp_dir,
            'broll_dir': broll_dir
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def ensure_unique_output_dir(base_output: str = "output") -> str:
    """Create a unique output directory per request"""
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    unique_id = uuid.uuid4().hex[:8]  # Shorten UUID for readability
    unique_path = os.path.join(base_output, f"{timestamp}_{unique_id}")
    os.makedirs(unique_path, exist_ok=True)
    return unique_path



async def orchestrate(info: dict):
    # 1. Generate script
    generator = GenerateScript(info)
    script = await generator.generate()
    
    # Create a unique output directory for this request
    unique_output_dir = ensure_unique_output_dir()

    # 2. Generate avatar video
    avatar_video_path = os.path.join(unique_output_dir, "demo_video.mp4")
    generate_avatar_video(
        avatar_id="046b2b11e4424b5c81f8d0223d3281d5",
        input_text=script,
        output_name=avatar_video_path,
        voice_speed=1.1
    )

    # 3. Generate b-roll-enhanced final video
    result = generate_video_with_broll(
        input_video_path=avatar_video_path,
        output_dir=unique_output_dir,
        final_output_name="final_video.mp4",
        product_image_b64=info["product_image_b64"]
    )

    if not result.get("success"):
        print("❌ Failed to generate final video:", result.get("error"))
        return result

    # 4. Add captions with ZapCap
    try:
        print("\n🎞️ Adding captions via ZapCap...")
        caption_generator = ZapCapCaptionGenerator()
        input_vid = result['final_video']
        output_vid = os.path.join(unique_output_dir, "captioned_video.mp4")
        template_id = 'd2018215-2125-41c1-940e-f13b411fff5c'  # your template ID
        caption_generator.add_captions(input_vid, template_id, output_vid)
        print("✅ Captioned video saved to:", output_vid)
        result["captioned_video"] = output_vid
    except Exception as e:
        print("❌ Failed to add captions:", str(e))
        result["captioning_error"] = str(e)

    return result


if __name__ == "__main__":
    # Example usage
    info = {
        "product_name": "BreezeNest Air Purifier",
        "language": "English",
        "description": "A sleek, energy-efficient air purifier designed for modern homes. Features a triple-layer HEPA filtration system, real-time air quality monitoring, and whisper-quiet operation. Connects via Wi-Fi and integrates with Apple HomeKit and Google Home.",
        "price": "$129.00",
        "promotion_detail": "Early-bird deal: Save $20 and get 2 extra HEPA filters free with your first purchase.",
        "target_audience": "Health-conscious individuals, young families, and eco-friendly apartment dwellers aged 28–45"
    }

    with open("./breezenest.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        info["product_image_b64"] = encoded_string


    result = asyncio.run(orchestrate(info))
    print(result)
