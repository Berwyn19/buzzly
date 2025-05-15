import os
import time
import base64
import requests
from typing import Optional, Dict, Any
from pathlib import Path
from runwayml import RunwayML
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

load_dotenv()

class VideoGenerator:
    def __init__(self):
        self.runway = RunwayML()
        
    def generate_video(self,
                       image_base64: str,
                       output_path: str,
                       prompt_text: str = '',
                       ratio: str = '720:1280') -> str:
        """Generate a video from an input image using Runway's Gen-4 model.
        
        Args:
            image_path (str): Path to the input image
            output_path (Optional[str]): Path to save the output video. If None, saves to 'output.mp4'
            prompt_text (str): Optional text prompt to guide the video generation
            ratio (str): Aspect ratio of the output video. Default is '16:9'
            
        Returns:
            Dict containing:
                - success (bool): Whether generation was successful
                - video_path (str): Path to saved video if successful
                - error (str): Error message if unsuccessful
                - task_id (str): Runway task ID for reference
        """
        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                
            # Create data URL from base64 string
            data_url = f'data:image/jpeg;base64,{image_base64}'
            
            # Initialize the video generation task
            print(f"\n📝 Runway API Request:")
            print(f"Model: gen4_turbo")
            print(f"Prompt text: {prompt_text}")
            print(f"Ratio: {ratio}")
            
            try:
                task = self.runway.image_to_video.create(
                    model='gen4_turbo',
                    prompt_image=data_url,
                    prompt_text=prompt_text,
                    ratio=ratio
                )
                print(f"\n✅ Task created successfully: {task}")
            except Exception as e:
                print(f"\n⚠️ Runway API Error:")
                print(f"Error type: {type(e).__name__}")
                print(f"Error message: {str(e)}")
                
                # Try to get the response object
                response = None
                if hasattr(e, 'response'):
                    response = e.response
                elif hasattr(e, 'args') and len(e.args) > 0 and hasattr(e.args[0], 'response'):
                    response = e.args[0].response
                
                if response:
                    print(f"Response status: {response.status_code}")
                    print(f"Response headers: {dict(response.headers)}")
                    try:
                        error_json = response.json()
                        print(f"Response body: {json.dumps(error_json, indent=2)}")
                    except:
                        print(f"Response text: {response.text}")
                
                # Print the full error traceback
                import traceback
                print("\nFull error traceback:")
                print(traceback.format_exc())
                
                raise
            task_id = task.id
            
            # Initial wait before polling
            time.sleep(10)
            
            # Poll until task is complete
            task = self.runway.tasks.retrieve(task_id)
            while task.status not in ['SUCCEEDED', 'FAILED']:
                time.sleep(10)
                task = self.runway.tasks.retrieve(task_id)
                
            if task.status == 'FAILED':
                raise Exception(f'Task failed: {task.status}')
            
            # Download and save the video
            if hasattr(task, 'output') and task.output:
                if isinstance(task.output, list) and len(task.output) > 0:
                    video_url = task.output[0]
                    
                    # Download the video
                    response = requests.get(video_url)
                    response.raise_for_status()
                    
                    # Save to specified path
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    
                    return output_path
                else:
                    raise Exception(f'Invalid output format: {task.output}')
            else:
                raise Exception('No output received from task')
            
        except Exception as e:
            raise Exception(f'Error generating video: {str(e)}')

def generate_video_from_image(image_base64: str,
                             output_path: str,
                             prompt_text: str = '',
                             ratio: str = '720:1280',  # Portrait 9:16 ratio
                             **kwargs) -> str:
    """Convenience function to generate a video from an image.
    
    Args:
        image_path (str): Path to the input image
        prompt_text (str): Optional text prompt to guide the video generation
        ratio (str): Aspect ratio of the output video (e.g., '16:9', '1:1', '9:16')
        **kwargs: Additional arguments to pass to VideoGenerator.generate_video()
        
    Returns:
        str: URL of the generated video
    """
    try:
        generator = VideoGenerator()
        
        return generator.generate_video(
            image_base64=image_base64,
            output_path=output_path,
            prompt_text=prompt_text,
            ratio=ratio,
            **kwargs
        )
        
    except Exception as e:
        raise Exception(f'Error generating video: {str(e)}')

def main():
    # Example usage
    try:
        # This would be your base64 image string
        with open('input.jpg', 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode()
            
        output_path = generate_video_from_image(
            image_base64=image_base64,
            output_path='output.mp4',
            prompt_text="A cinematic scene",
            ratio="720:1280"
        )
        print(f"\n✨ Video saved to: {output_path}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == '__main__':
    main()