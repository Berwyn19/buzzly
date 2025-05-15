import whisper

def transcribe_audio(audio_path):
    model = whisper.load_model("base")  # or "small", "medium"
    result = model.transcribe(audio_path)

    segments_data = []
    for segment in result['segments']:
        entry = {
            "start": round(segment["start"], 2),
            "end": round(segment["end"], 2),
            "text": segment["text"].strip()
        }
        segments_data.append(entry)

    return segments_data

if __name__ == "__main__":
    transcript = transcribe_audio("demo_audio.mp3")
    print(transcript)
    
