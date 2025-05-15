import os
import time
import json
import requests
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class ZapCapCaptionGenerator:
    def __init__(self):
        self.api_key = os.getenv('ZAPCAP_API_KEY')
        if not self.api_key:
            raise ValueError('ZAPCAP_API_KEY not found in environment variables')
        self.api_base = 'https://api.zapcap.ai'
    
    def add_captions(self, video_path, template_id, output_path):
        try:
            # Upload video
            print('Uploading video...')
            with open(video_path, 'rb') as f:
                upload_response = requests.post(
                    f'{self.api_base}/videos',
                    headers={'x-api-key': self.api_key},
                    files={'file': f}
                )
                upload_response.raise_for_status()
                video_id = upload_response.json()['id']
                print('Video uploaded, ID:', video_id)

                # Create task
                print('Creating task...')
                task_response = requests.post(
                    f'{self.api_base}/videos/{video_id}/task',
                    headers={
                        'x-api-key': self.api_key,
                        'Content-Type': 'application/json'
                    },
                    json={
                        'templateId': template_id,
                        'autoApprove': True,
                        'language': 'en'
                    }
                )
                task_response.raise_for_status()
                task_id = task_response.json()['taskId']
                print('Task created, ID:', task_id)
                
                # Poll for task completion
                print('Waiting for task to complete...')
                attempts = 0
                while True:
                    status_response = requests.get(
                        f'{self.api_base}/videos/{video_id}/task/{task_id}',
                        headers={'x-api-key': self.api_key}
                    )
                    status_response.raise_for_status()
                    data = status_response.json()
                    status = data['status']
                    
                    if status == 'completed':
                        # Download video
                        print('Task completed, downloading video...')
                        download_response = requests.get(data['downloadUrl'])
                        download_response.raise_for_status()

                        with open(output_path, 'wb') as f:
                            f.write(download_response.content)
                        print('Video downloaded, saved to:', output_path)
                        break
                    
                    elif status == 'failed':
                        raise Exception(f"Task failed: {data.get['error']}")
                    
                    time.sleep(2)
                    attempts += 1
                    
        except Exception as e:
            print(f"Error adding captions: {str(e)}")

if __name__ == '__main__':
    video_path = './output/test_merge.mp4'
    template_id = 'd2018215-2125-41c1-940e-f13b411fff5c'
    output_path = 'captioned.mp4'
    
    caption_generator = ZapCapCaptionGenerator()
    caption_generator.add_captions(video_path, template_id, output_path)
                    
                    
                
                
                            
                
                
                    
