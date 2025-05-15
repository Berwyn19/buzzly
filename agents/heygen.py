import os
import time
import json
import requests
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class HeyGenVideoGenerator:
    def __init__(self):
        self.api_key = os.getenv('HEYGEN_API_KEY')
        if not self.api_key:
            raise ValueError('HEYGEN_API_KEY not found in environment variables')
    
        self.base_url = 'https://api.heygen.com'
        self.headers = {
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def generate_video(
        self,
        avatar_id: str,
        input_text: str,
        voice_id: str = '9e18bbe8306c43da9fd1f598289b03ca',  # Default voice
        avatar_style: str = 'normal',
        voice_speed: float = 1.0,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a video using HeyGen's API.
        
        Args:
            avatar_id (str): ID of the avatar to use
            input_text (str): Text for the avatar to speak
            voice_id (str): ID of the voice to use
            avatar_style (str): Style of the avatar ('normal' or other available styles)
            voice_speed (float): Speed of the voice (0.5 to 2.0)
            output_path (str, optional): Path to save the video
            
        Returns:
            Dict containing:
                - success (bool): Whether generation was successful
                - video_path (str): Path to saved video if successful
                - error (str): Error message if unsuccessful
                - video_id (str): HeyGen video ID for reference
        """
        try:
            # Prepare the request payload
            payload = {
                "video_inputs": [
                    {
                        "character": {
                            "type": "avatar",
                            "avatar_id": avatar_id,
                            "avatar_style": avatar_style
                        },
                        "voice": {
                            "type": "text",
                            "input_text": input_text,
                            "voice_id": voice_id,
                            "speed": voice_speed
                        }
                    }
                ],
                "dimension": {
                    "width": 720,
                    "height": 1280  # 9:16 portrait ratio
                }
            }
            
            # Print request details
            request_url = f"{self.base_url}/v2/video/generate"
            print("\n=== Request Details ===\n")
            print(f"URL: {request_url}")
            print(f"Headers: {json.dumps(self.headers, indent=2)}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            # Initialize video generation
            response = requests.post(
                request_url,
                headers=self.headers,
                json=payload
            )
            
            # Print response details
            print("\n=== Response Details ===")
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
            try:
                print(f"Response Body: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"Response Text: {response.text}")
            
            response.raise_for_status()
            data = response.json()
            
            if 'data' not in data or 'video_id' not in data['data']:
                return {
                    'success': False,
                    'error': 'No video_id in response',
                    'video_path': None,
                    'video_id': None
                }
            
            video_id = data['data']['video_id']
            
            # Poll for video completion
            while True:
                status = self._check_video_status(video_id)
                if status.get('status') == 'completed':
                    break
                elif status.get('status') == 'failed':
                    return {
                        'success': False,
                        'error': f'Video generation failed: {status.get("error", "Unknown error")}',
                        'video_path': None,
                        'video_id': video_id
                    }
                time.sleep(5)  # Wait 5 seconds before checking again
            
            # Download the video if output_path is provided
            if output_path and status.get('video_url'):
                video_url = status['video_url']
                response = requests.get(video_url)
                response.raise_for_status()
                
                # Ensure output directory exists
                output_dir = os.path.dirname(output_path)
                if output_dir:
                    Path(output_dir).mkdir(parents=True, exist_ok=True)
                
                # Save the video
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                return {
                    'success': True,
                    'video_path': output_path,
                    'error': None,
                    'video_id': video_id,
                    'video_url': video_url
                }
            
            return {
                'success': True,
                'video_path': None,
                'error': None,
                'video_id': video_id,
                'video_url': status.get('video_url')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'video_path': None,
                'video_id': None
            }
    
    def _check_video_status(self, video_id: str) -> Dict[str, Any]:
        """Check the status of a video generation task.
        
        Args:
            video_id (str): ID of the video to check
            
        Returns:
            Dict containing status information
        """
        status_url = "https://api.heygen.com/v1/video_status.get"
        response = requests.get(
            status_url,
            headers=self.headers,
            params={'video_id': video_id}
        )
        response.raise_for_status()
        return response.json().get('data', {})

def generate_avatar_video(
    avatar_id: str,
    input_text: str,
    output_name: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Convenience function to generate a video using HeyGen and save it to the videos folder.
    
    Args:
        avatar_id (str): ID of the avatar to use
        input_text (str): Text for the avatar to speak
        output_name (Optional[str]): Name for the output video file (without extension)
        **kwargs: Additional arguments to pass to HeyGenVideoGenerator.generate_video()
        
    Returns:
        Dict: Result dictionary from HeyGenVideoGenerator
    """
    try:
        generator = HeyGenVideoGenerator()
        
        # Create videos directory if it doesn't exist
        videos_dir = 'videos'
        Path(videos_dir).mkdir(exist_ok=True)
        
        # Generate output filename if not provided
        if output_name is None:
            output_name = f"heygen_video_{int(time.time())}"
        
        output_path = os.path.join(videos_dir, f"{output_name}.mp4")
        
        return generator.generate_video(
            avatar_id=avatar_id,
            input_text=input_text,
            output_path=output_path,
            **kwargs
        )
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'video_path': None,
            'video_id': None
        }

def main():
    # Example usage
    avatar_id = "046b2b11e4424b5c81f8d0223d3281d5"  # This would come from LLM in real use
    input_text = """
                    "Step into style. Step into sustainability."

                    "Introducing LuxeStride Eco Sneakers—where cutting-edge fashion meets eco-conscious innovation."

                    "Crafted from recycled ocean plastics and vegan leather, our sneakers deliver style and sustainability. Enjoy breathable comfort with an ergonomic fit for all-day wear."

                    "Perfect for eco-conscious millennials and urban trendsetters, LuxeStride keeps up with your lifestyle—effortlessly taking you from work to play."

                    "For a limited time, get 15% off plus a free organic cotton tote with every order. Don’t miss this exclusive offer!"

                    "Join the movement. Elevate your style with LuxeStride Eco Sneakers today. Shop now."
                 """  
    
    result = generate_avatar_video(
        avatar_id=avatar_id,
        input_text=input_text,
        output_name='demo_video',
        voice_speed=1.1
    )
    
    if result['success']:
        print(f"✨ Video generated successfully!")
        print(f"📁 Saved to: {result['video_path']}")
        print(f"🆔 Video ID: {result['video_id']}")
        if 'video_url' in result:
            print(f"🎥 Video URL: {result['video_url']}")
    else:
        print(f"❌ Error: {result['error']}")

if __name__ == '__main__':
    main()