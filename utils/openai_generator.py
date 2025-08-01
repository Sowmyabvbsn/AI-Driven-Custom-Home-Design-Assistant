import os
import openai
from dotenv import load_dotenv

# Load the OPENAI_API_KEY from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Layout generation function
def generate_layout_with_openai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or gpt-4 if you have access
            messages=[
                {"role": "system", "content": "You are a professional architect helping users generate home layout plans."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI Error: {e}"
