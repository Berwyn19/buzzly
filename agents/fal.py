import os
import base64
import requests
import fal_client
from dotenv import load_dotenv

load_dotenv()

def download_image(url, filename):
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, "wb") as f:
        f.write(response.content)
    print(f"Image downloaded as {filename}")
    return base64.b64encode(response.content).decode('utf-8')

def try_on(model_image_path, garment_image_path):
    FAL_KEY = os.getenv("FAL_KEY")
    if not FAL_KEY:
        raise ValueError("FAL_KEY environment variable not set")

    # Upload images to Fal and get URLs
    model_url = fal_client.upload_file(model_image_path)
    garment_url = fal_client.upload_file(garment_image_path)

    # Run the try-on model
    response = fal_client.run(
        "fal-ai/fashn/tryon/v1.5",
        arguments={
            "model_image": model_url,
            "garment_image": garment_url
        }
    )

    # Extract output image URL and download
    images = response.get("images", [])
    if images and "url" in images[0]:
        output_url = images[0]["url"]
        filename = os.path.basename(output_url.split("?")[0]) or "output_0.png"
        base64_str = download_image(output_url, filename)
        return base64_str
    else:
        raise ValueError("No output image URL found in result.")

if __name__ == '__main__':
    model_image_path = './model.jpeg'
    garment_image_path = './cloth.png'
    base64_str = try_on(model_image_path, garment_image_path)
    print("Base64 output:", base64_str)
