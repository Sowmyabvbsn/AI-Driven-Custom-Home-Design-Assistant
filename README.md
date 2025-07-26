# 🏠 AI-Driven Custom Home Design Assistant

This Streamlit web app helps users design custom home layouts using Generative AI (Gemini API by Google or OpenAI fallback) and image generation via Lexica.art.

---

## 📌 Features

- 🎯 Takes user input: Style, Size, Bedrooms, and Special Requirements
- 🤖 Uses **Gemini Pro** (Google Generative AI) to generate text-based layout
- 🔄 Fallback to **OpenAI GPT** if Gemini fails
- 🖼️ Fetches visual design from **Lexica.art** based on layout
- ✅ Validates input fields before generating results
- 💾 Option to export layout to `.txt` file
- ⚡ Built with **Streamlit** and integrated APIs

---

## 🧰 Technologies Used

- `Streamlit`
- `Google Generative AI API (Gemini Pro)`
- `OpenAI GPT (Fallback)`
- `Lexica.art` (Image generation)
- `.env` for secure API keys

---

## 🛠️ Installation Instructions

1. **Clone the repository**

```bash
git clone https://github.com/bhavana111017/Custom_Home_Design_Assistant.git
cd Custom_Home_Design_Assistant
