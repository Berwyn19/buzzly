import subprocess

def extract_audio(video_path, output_path):
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-q:a", "0",
        "-map", "0:a",
        output_path
    ]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    extract_audio("./demo_video.mp4", "./demo_audio.mp3")