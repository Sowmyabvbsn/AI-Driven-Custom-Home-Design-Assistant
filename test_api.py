import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Correct configuration (uses default v1 automatically)
genai.configure(api_key=api_key)

# Show all available models
models = genai.list_models()
print("✅ Available models:")
for model in models:
    print(f"🔹 {model.name} - {model.supported_generation_methods}")

# Try generating content with gemini-pro (text only)
try:
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
 # updated model name
    response = model.generate_content("Say hello from Gemini")
    print("\n✅ Gemini response:", response.text)
except Exception as e:
    print("\n❌ Failed to generate content:", e)
