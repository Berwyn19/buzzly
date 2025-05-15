import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_chat_completion(prompt: str, model: str = "gpt-4.1-2025-04-14", max_tokens: int = 1000) -> str:
    """Get a chat completion from OpenAI API
    
    Args:
        prompt (str): The input prompt for the chat
        model (str): The model to use (default: gpt-4-turbo-preview)
        max_tokens (int): Maximum tokens in the response (default: 1000)
        
    Returns:
        str: The chat completion response
    """
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error getting chat completion: {str(e)}"

if __name__ == "__main__":
    prompt = "Can you explain entropy in thermodynamics"
    response = get_chat_completion(prompt)
    print(response)