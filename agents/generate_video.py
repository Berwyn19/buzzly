#!/usr/bin/env python3
import os
from pathlib import Path
from typing import Dict, Any, List

from ffmpeg.extract_audio import extract_audio
from ffmpeg.transcribe import transcribe_audio
from ffmpeg.wrapper import ffmpeg_merge
from broll_generation.description_generator import generate_all_brolls
from broll_generation.broll import generate_broll_scene
from broll_generation.broll_image import generate_broll_image

def ensure_dir(path: str) -> str:
    """Ensure directory exists and return it"""
    os.makedirs(path, exist_ok=True)
    return path

def generate_video_with_broll(
    input_video_path: str,
    output_dir: str = "output",
    final_output_name: str = "final_video.mp4"
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
            result = generate_broll_scene(
                dynamic_description=broll.description,
                output_path=scene_path
            )
            
            if result['success']:
                broll.video_path = result['video_path']
                broll.static_description = result['static_description']
                broll.motion_prompt = result['motion_prompt']
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
                'video': broll.video_path
            }
            for broll in broll_scenes
        ]
        
        # Merge everything together
        print("\n🎥 Merging final video...")
        final_output_path = os.path.join(output_dir, final_output_name)
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

if __name__ == "__main__":
    # Example usage
    result = generate_video_with_broll(
        input_video_path="demo_video.mp4",
        output_dir="output",
        final_output_name="final_video.mp4"
    )
    
    if result['success']:
        print(f"""
✅ Video generation complete!

📁 Files:
- Input video: {result['input_video']}
- Final video: {result['final_video']}
- B-roll directory: {result['broll_dir']}

📊 Statistics:
- Generated {len(result['broll_scenes'])} B-roll scenes
- Transcript length: {len(result['transcript'])} characters
""")
    else:
        print(f"\n❌ Error: {result['error']}")
