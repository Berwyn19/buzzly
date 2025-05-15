import os
import time
import json
import requests
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class HeyGenImageGenerator:
    def __init__(self):
        self.api_key = os.getenv('HEYGEN_API_KEY')
        if not self.api_key:
            raise ValueError('HEYGEN_API_KEY not found in environment variables')
        
        self.url = 'https://api.heygen.com/v2/photo_avatar/photo/generate'
        self.headers = {
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }

    def generate_image(
        self,
        name: str,
        age: str,
        gender: str,
        ethnicity: str,
        appearance: str,
        orientation: str = 'horizontal',
        pose: str = 'half_body',
        style: str = 'Realistic',
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a photo avatar using HeyGen's API.
        
        Args:
            name (str): Name of the person
            age (str): Age category (e.g., 'Young Adult', 'Middle Aged')
            gender (str): Gender of the person (e.g., 'Woman', 'Man')
            ethnicity (str): Ethnicity of the person
            appearance (str): Detailed description of appearance and context
            orientation (str): Image orientation ('horizontal' or 'vertical')
            pose (str): Pose type ('half_body' or other available poses)
            style (str): Image style ('Realistic' or other available styles)
            output_path (str, optional): Path to save the generated image
            
        Returns:
            Dict containing:
                - success (bool): Whether generation was successful
                - image_path (str): Path to saved image if successful
                - error (str): Error message if unsuccessful
                - task_id (str): Task ID for reference
                - image_url (str): URL of the generated image if available
        """
        try:
            # Prepare the request payload
            payload = {
                "name": name,
                "age": age,
                "gender": gender,
                "ethnicity": ethnicity,
                "orientation": orientation,
                "pose": pose,
                "style": style,
                "appearance": appearance
            }
            
            # Print request details for debugging
            print("\n=== Request Details ===\n")
            print(f"URL: {self.url}")
            print(f"Headers: {json.dumps(self.headers, indent=2)}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            # Make the API request
            response = requests.post(
                self.url,
                headers=self.headers,
                json=payload
            )
            print(response)
            
            # Print response details for debugging
            print("\n=== Response Details ===\n")
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
            print(f"Raw Response Text: {response.text}")
            
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                data = response.json()
                print(f"Parsed JSON Response: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {str(e)}")
                return {
                    'success': False,
                    'error': f'Invalid JSON response: {str(e)}',
                    'image_path': None,
                    'generation_id': None,
                    'image_url': None
                }
            
            # Check if we have the generation ID in the response
            if 'data' not in data or 'generation_id' not in data['data']:
                return {
                    'success': False,
                    'error': 'No generation ID in response',
                    'image_path': None,
                    'generation_id': None,
                    'image_url': None
                }
            
            generation_id = data['data']['generation_id']
            
            # Poll for the result
            max_attempts = 30  # Maximum number of polling attempts
            poll_interval = 2  # Time between polls in seconds
            
            for attempt in range(max_attempts):
                time.sleep(poll_interval)
                
                # Check generation status
                status_response = requests.get(
                    f"{self.url}/v2/photo_avatar/photo/status",
                    headers=self.headers,
                    params={'generation_id': generation_id}
                )
                
                try:
                    status_data = status_response.json()
                    print(f"Parsed Status JSON: {json.dumps(status_data, indent=2)}")
                except json.JSONDecodeError as e:
                    print(f"Raw Status Response: {status_response.text}")
                    print(f"Failed to parse status JSON: {str(e)}")
                    continue
                print(f"\n=== Poll Attempt {attempt + 1} ===\n")
                print(f"Status Response: {json.dumps(status_data, indent=2)}")
                
                if status_data.get('error'):
                    return {
                        'success': False,
                        'error': status_data['error'],
                        'image_path': None,
                        'generation_id': generation_id,
                        'image_url': None
                    }
                
                if 'data' in status_data and 'url' in status_data['data']:
                    image_url = status_data['data']['url']
                    break
            else:
                return {
                    'success': False,
                    'error': 'Timeout waiting for image generation',
                    'image_path': None,
                    'generation_id': generation_id,
                    'image_url': None
                }
            
            # Download and save the image if output_path is provided
            if output_path:
                # Download the image
                img_response = requests.get(image_url)
                img_response.raise_for_status()
                
                # Ensure output directory exists
                output_dir = os.path.dirname(output_path)
                if output_dir:
                    Path(output_dir).mkdir(parents=True, exist_ok=True)
                
                # Save the image
                with open(output_path, 'wb') as f:
                    f.write(img_response.content)
                
                return {
                    'success': True,
                    'image_path': output_path,
                    'error': None,
                    'generation_id': generation_id,
                    'image_url': image_url
                }
            
            return {
                'success': True,
                'image_path': None,
                'error': None,
                'task_id': task_id,
                'image_url': image_url
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'image_path': None,
                'generation_id': None,
                'image_url': None
            }


def generate_avatar_image(
    name: str,
    age: str,
    gender: str,
    ethnicity: str,
    appearance: str,
    output_name: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Convenience function to generate an avatar image and save it to the avatars folder.
    
    Args:
        name (str): Name of the person
        age (str): Age category
        gender (str): Gender of the person
        ethnicity (str): Ethnicity of the person
        appearance (str): Detailed description of appearance
        output_name (Optional[str]): Name for the output image file (without extension)
        **kwargs: Additional arguments to pass to HeyGenImageGenerator.generate_image()
        
    Returns:
        Dict: Result dictionary from HeyGenImageGenerator
    """
    try:
        generator = HeyGenImageGenerator()
        
        # Create avatars directory if it doesn't exist
        avatars_dir = 'avatars'
        Path(avatars_dir).mkdir(exist_ok=True)
        
        # Generate output filename if not provided
        if output_name is None:
            output_name = f"{name.lower()}_{int(time.time())}"
        
        output_path = os.path.join(avatars_dir, f"{output_name}.png")
        
        return generator.generate_image(
            name=name,
            age=age,
            gender=gender,
            ethnicity=ethnicity,
            appearance=appearance,
            output_path=output_path,
            **kwargs
        )
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'image_path': None,
            'task_id': None,
            'image_url': None
        }


def main():
    # Example usage
    result = generate_avatar_image(
        name="Jessica",
        age="Young Adult",
        gender="Woman",
        ethnicity="South East Asian",
        appearance="A stylish South East Asian woman in casual attire walking through a bustling city street",
        orientation="horizontal",
        pose="full_body",
        style="Realistic"
    )
    
    if result['success']:
        print(f"✨ Image generated successfully!")
        print(f"📁 Saved to: {result['image_path']}")
        print(f"🔔 Generation ID: {result['generation_id']}")
        print(f"🎨 Image URL: {result['image_url']}")
    else:
        print(f"❌ Error: {result['error']}")


if __name__ == '__main__':
    main()
        