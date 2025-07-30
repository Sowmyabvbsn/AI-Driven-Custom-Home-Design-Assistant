import os
import streamlit as st
from dotenv import load_dotenv
from utils.gemini_generator import generate_layout_with_gemini
from utils.openai_generator import generate_layout_with_openai
from utils.lexica_image import fetch_lexica_image

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(page_title="AI Home Design Assistant", layout="wide")
st.title("🏡 AI-Driven Custom Home Design Assistant")

# Sidebar settings
st.sidebar.header("Enter Home Design Preferences")
style = st.sidebar.selectbox("🏷️ Style", ["Modern", "Traditional", "Minimalist", "Industrial"])
size = st.sidebar.text_input("📐 Plot Size (e.g., 38x38 ft)")
bedrooms = st.sidebar.slider("🛏️ Number of Bedrooms", min_value=1, max_value=10, value=3)
special = st.sidebar.text_area("✨ Special Requirements", placeholder="Pooja Room, Home Office, etc.")

# API model preference
model_choice = st.sidebar.radio("🔌 Use which AI Model?", ("Gemini", "OpenAI"))

# Submit button
if st.sidebar.button("Generate Design"):
    if not size:
        st.warning("Please enter the plot size.")
        st.stop()

    with st.spinner("Generating design layout..."):
        # Create the prompt
        prompt = f"Generate a {style.lower()} style home design layout for a plot of size {size} with {bedrooms} bedrooms."
        if special:
            prompt += f" Include special features like {special}."

        # Call Gemini or OpenAI
        try:
            if model_choice == "Gemini":
                layout_text = generate_layout_with_gemini(prompt)
            else:
                layout_text = generate_layout_with_openai(prompt)
        except Exception as e:
            st.error(f"Error during AI generation: {e}")
            st.stop()

    # Display layout
    st.subheader("📝 Generated Layout Plan")
    st.write(layout_text)

    # Fetch and display image
    st.subheader("🖼️ Visual Inspiration from Lexica.art")
    image_prompt = f"{style} house design with {bedrooms} bedrooms, {special}, {size}"
    try:
        image_url = fetch_lexica_image(image_prompt)
        if image_url:
            st.image(image_url, caption="Image generated using Lexica.art")
        else:
            st.warning("No image found from Lexica.")
    except Exception as e:
        st.warning(f"Image generation failed: {e}")

    # Export option
    st.download_button("📥 Download Layout Text", layout_text, file_name="home_design.txt")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit, Gemini & OpenAI")
