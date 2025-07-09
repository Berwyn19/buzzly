from agents_server.ffmpeg.extract_audio import extract_audio
from agents_server.ffmpeg.transcribe import transcribe_audio
import subprocess
import os
import tempfile
import ffmpeg

DUMMY_DATA = [
    {
        'start': 15.4,
        'end': 21.72,
        'video': './ice.mp4'
    },
    {
        'start': 31.28,
        'end': 37.56,
        'video': './mouse.mp4'
    }
]

def build(video_path, output_path):
    extract_audio(video_path, output_path)
    transcript_json = transcribe_audio(output_path)
    return transcript_json

def get_video_duration(video_path):
    """Get duration of a video file in seconds using ffprobe."""
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    output = subprocess.check_output(cmd).decode().strip()
    return float(output)

def ffmpeg_merge(main_video, output_path, broll_data):
    """
    Overlay b-roll videos visually on top of the main video at specified times,
    always keeping the original main video audio.
    main_video: path to a-roll video (with audio)
    output_path: path to output file
    broll_data: list of dicts, each with 'start', 'end', 'video_path'
    """
    brolls = sorted(broll_data, key=lambda x: x['start'])
    input_args = ['-i', main_video]
    filter_chain = []
    last_label = '[0:v]'
    # Prepare all b-roll video inputs and filter labels
    for idx, b in enumerate(brolls):
        input_args += ['-i', b['video_path']]
    # Build filter_complex with setpts to shift overlay timing
    for idx, b in enumerate(brolls):
        b_idx = idx + 1
        # Shift overlay to start at b["start"]
        filter_chain.append(
            f'[{b_idx}:v]setpts=PTS-STARTPTS+{b["start"]}/TB[broll{b_idx}]'
        )
    # Overlay each b-roll in sequence
    overlay_chain = last_label
    for idx, b in enumerate(brolls):
        b_idx = idx + 1
        out_label = f'[ov{b_idx}]'
        # Only overlay during the interval
        filter_chain.append(
            f'{overlay_chain}[broll{b_idx}]overlay=enable=\'between(t,{b["start"]},{b["end"]})\':eof_action=pass{out_label}'
        )
        overlay_chain = out_label
    filter_complex = ';'.join(filter_chain)
    cmd = [
        'ffmpeg', '-y',
        *input_args,
        '-filter_complex', filter_complex,
        '-map', overlay_chain,  # final video output
        '-map', '0:a',          # always use main video audio
        '-c:v', 'libx264',
        '-c:a', 'aac',
        output_path
    ]
    subprocess.run(cmd, check=True)

    
if __name__ == "__main__":
    video_path = "./demo_video.mp4"
    output_path = "./combined.mp4"
    transcript_json = build(video_path, output_path)
    print(transcript_json)
    # ffmpeg_merge(video_path, output_path, DUMMY_DATA)
    
