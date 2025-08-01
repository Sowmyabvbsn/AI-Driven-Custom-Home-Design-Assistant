import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load the GEMINI_API_KEY from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=api_key)

# Layout generation function
def generate_layout_with_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")  # Use latest version
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini Error: {e}"
