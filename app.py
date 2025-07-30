import streamlit as st
import google.generativeai as genai
import openai
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configure APIs
genai.configure(api_key=GEMINI_API_KEY)
openai.api_key = OPENAI_API_KEY

# Valid home styles
HOME_STYLES = [
    "Modern", "Traditional", "Contemporary", "Minimalist",
    "Rustic", "Industrial", "Mediterranean", "Colonial", "Victorian"
]

# Function: Generate layout from Gemini
def generate_with_gemini(style, size, rooms):
    try:
        prompt = f"Design a {style}-style home of {size} sq ft with {rooms} rooms. Include layout and furniture suggestions."
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        chat = model.start_chat()
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        return None

# Function: Fallback OpenAI generator
def generate_with_openai(style, size, rooms):
    try:
        prompt = f"Design a {style}-style home of {size} sq ft with {rooms} rooms. Include layout and furniture suggestions."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"❌ OpenAI Error: {e}"

# Function: Fetch image from Lexica.art
def fetch_lexica_image(query):
    try:
        res = requests.get(f"https://lexica.art/api/v1/search?q={query}")
        if res.status_code == 200:
            data = res.json()
            if data["images"]:
                return data["images"][0]["srcSmall"]  # or src if you want bigger
        return None
    except Exception as e:
        return None

# Streamlit UI
st.set_page_config(page_title="AI Home Designer", page_icon="🏡")
st.title("🏡 AI-Driven Home Design Assistant")
st.markdown("Generate home design ideas based on selected style, size, and room count.")

# UI Inputs
style = st.selectbox("🏷️ Select Home Style", HOME_STYLES)
size = st.number_input("📐 Home Size (sq ft)", min_value=100, max_value=10000, value=1000)
rooms = st.number_input("🚪 Number of Rooms", min_value=1, max_value=10, value=3)

# Generate Button
if st.button("✨ Generate Design Idea"):
    with st.spinner("🔧 Generating layout with Gemini..."):
        idea = generate_with_gemini(style, size, rooms)

    if idea:
        st.success("✅ Design layout generated!")
        st.markdown("### 📝 Layout Plan")
        st.markdown(idea)

        # Fetch image based on style
        with st.spinner("🖼️ Fetching visual sample..."):
            image_url = fetch_lexica_image(f"{style} home exterior")
        if image_url:
            st.image(image_url, caption=f"{style} Style Home", use_container_width=True)
        else:
            st.warning("⚠️ Couldn't fetch image preview.")
    else:
        st.warning("⚠️ Gemini API failed. Click below to retry with OpenAI.")
        if st.button("🔁 Retry with OpenAI"):
            with st.spinner("Generating design using OpenAI..."):
                alt_idea = generate_with_openai(style, size, rooms)
            st.success("✅ Design idea from OpenAI:")
            st.markdown(alt_idea)
