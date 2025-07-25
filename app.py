import streamlit as st
import os
import google.generativeai as genai
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Define Gemini model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 1024,
    "response_mime_type": "text/plain"
}
model = genai.GenerativeModel(model_name="gemini-pro", generation_config=generation_config)

# Define design generation function
def generate_design_idea(style, size, bedrooms, special_requirements):
    prompt = f"""
    Design a modern house with the following specifications:
    - Style: {style}
    - Size: {size}
    - Number of Bedrooms: {bedrooms}
    - Special Requirements: {special_requirements}

    Provide a detailed layout description in 150-200 words.
    """
    response = model.generate_content(prompt)
    return response.text

# Define image generation from Lexica.art
def generate_image_url(prompt):
    try:
        url = f"https://lexica.art/api/v1/search?q={prompt}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data["images"]:
                return data["images"][0]["srcSmall"]
        return None
    except Exception as e:
        print("Lexica API error:", e)
        return None

# Streamlit UI
st.set_page_config(page_title="AI-Driven Home Design Assistant", layout="centered")
st.title("🏠 AI-Driven Home Design Assistant")
st.markdown("Use AI to design your dream home layout and view a visual sample!")

style = st.selectbox("🏗️ Select Architectural Style:", ["Modern", "Traditional", "Minimalist", "Victorian", "Futuristic"])
size = st.text_input("📏 Enter Plot Size (e.g., 38x38 ft):")
bedrooms = st.number_input("🛏️ Number of Bedrooms:", min_value=1, max_value=10, value=3)
special_requirements = st.text_area("✨ Any Special Requirements?", placeholder="E.g., pooja room, open kitchen, east-facing, etc.")

if st.button("Generate Design Idea"):
    if not size.strip():
        st.error("Please enter a valid plot size.")
    else:
        with st.spinner("Generating layout and image..."):
            # Generate text
            layout_text = generate_design_idea(style, size, bedrooms, special_requirements)

            # Generate image
            image_prompt = f"{style} house plan, {size}, {bedrooms} bedrooms, {special_requirements}"
            image_url = generate_image_url(image_prompt)

        # Display result
        st.subheader("📝 Layout Plan")
        st.write(layout_text)

        if image_url:
            st.subheader("🖼️ Visual Sample")
            st.image(image_url, caption="AI-generated layout image", use_column_width=True)
        else:
            st.warning("Could not fetch image from Lexica.art. Please try again.")

        # Export Option
        st.download_button("📥 Download Layout Text", layout_text, file_name="layout_idea.txt")

