from pydantic import BaseModel
from openai import OpenAI
from typing import List

client = OpenAI()

class BrollDescription(BaseModel):
    start: float
    end: float
    description: str
    video_path: str = None
    static_description: str = None
    motion_prompt: str = None

class BrollCount(BaseModel):
    count: int

def estimate_broll_count(transcript):
    prompt = f"""
Transcript:
{transcript}

How many B-roll scenes should be inserted in this video? Please respond with just an integer.
"""
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Decide how many B-rolls are necessary for the given transcript. Respond with just an integer. Integer should ideally be less than or equal to 3, unless you feel like it is necessary to have more"},
            {"role": "user", "content": prompt},
        ],
        response_format=BrollCount
    )

    # Parse the response as JSON and extract the count
    import json
    result = json.loads(response.choices[0].message.content)
    return result.get('count', 3)  # Default to 3 if parsing fails

def generate_single_broll(transcript, history: List[BrollDescription]):
    # Ensure history is a list
    if history is None:
        history = []
    
    # Format history text
    history_text = "None yet."
    if history:
        history_text = "\n".join(
            [f"- {b.start:.2f}s to {b.end:.2f}s: {b.description}" for b in history]
        )

    prompt = f"""
Transcript:
{transcript}

Selected B-rolls so far:
{history_text}

Now choose one more B-roll scene (that doesn't overlap with the above), and describe what should be shown during that segment, just keep it simple.
You may also choose a broll that runs over multiple segment, just make sure you specified the start and end time.
"""

    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a video editor's assistant. Choose and describe one new B-roll scene for the transcript, just keep the scene simple Respond with a JSON object containing 'start' (float), 'end' (float), and 'description' (string)."},
            {"role": "user", "content": prompt},
        ],
        response_format=BrollDescription
    )

    # Parse the response as JSON and return as a BrollDescription instance
    import json
    result = json.loads(response.choices[0].message.content)
    return BrollDescription(**result)

def generate_all_brolls(transcript) -> List[BrollDescription]:
    count = estimate_broll_count(transcript)
    brolls: List[BrollDescription] = []

    for _ in range(min(3, count)):
        new_broll = generate_single_broll(transcript, brolls)
        brolls.append(new_broll)

    return brolls

if __name__ == "__main__":
    transcript = """
        [{'start': 0.0, 'end': 3.28, 'text': 'Tired of worrying about hydration and hygiene on the go?'}, 
        {'start': 3.28, 'end': 5.36, 'text': 'Meet the Acqua Pure Smart bottle,'}, 
        {'start': 5.36, 'end': 9.08, 'text': 'your ultimate solution for clean, safe and convenient hydration.'}, 
        {'start': 9.08, 'end': 11.36, 'text': 'Crafted with sleek, modern design,'}, 
        {'start': 11.36, 'end': 13.32, 'text': 'Acqua Pure is a health-focused,'}, 
        {'start': 13.32, 'end': 15.4, 'text': 'tech-driven hydration companion.'}, 
        {'start': 15.4, 'end': 21.68, 'text': 'Its UV-C sterilization cap kills 99.99% of bacteria with a tap.'}, 
        {'start': 21.68, 'end': 26.64, 'text': 'Keeps drinks hot or cold for 24 hours in stylish, insulated stainless steel.'}, 
        {'start': 26.96, 'end': 31.44, 'text': 'Sink with our app for hydration reminders and wellness optimization.'}, 
        {'start': 31.44, 'end': 34.56, 'text': 'Experience ultimate convenience with automatic cleaning.'}, 
        {'start': 34.56, 'end': 37.52, 'text': 'Stay focused, energised and eco-friendly.'}, 
        {'start': 37.52, 'end': 39.84, 'text': 'Say goodbye to single-use plastics.'}, 
        {'start': 39.84, 'end': 45.04, 'text': 'Exclusive launch offer, 20% off for first-time buyers with a free replacement filter.'}, 
        {'start': 45.04, 'end': 49.28, 'text': 'Hurry, limited time only, elevate your hydration game,'}, 
        {'start': 49.28, 'end': 53.28, 'text': 'order your Acqua Pure Smart bottle now and step into the future of hydration.'}]
    """
    brolls = generate_all_brolls(transcript)
    for broll in brolls:
        print(broll.json())
