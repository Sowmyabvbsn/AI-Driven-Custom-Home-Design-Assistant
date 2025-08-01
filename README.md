# 🏠 AI-Driven Custom Home Design Assistant

This Streamlit-based app helps users generate personalized home layout ideas using generative AI (Gemini & OpenAI) and visualizes them with AI-generated images from Lexica.art.

---

## 🚀 Features

- ✨ Style-based layout generation (modern, traditional, etc.)
- 📏 Custom sizes and number of bedrooms
- 🙏 Optional Vastu or special requirements
- 🧠 Uses Gemini 1.5 or OpenAI GPT-4 (fallback)
- 🎨 Image generation with Lexica.art API
- 📦 Downloadable layout idea text

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI Models**: Gemini 1.5 Pro, OpenAI GPT-4
- **Image Generation**: Lexica.art API
- **Language**: Python 3.10+

---

## ⚙️ Setup Instructions

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/Custom_Home_Design_Assistant.git
    cd Custom_Home_Design_Assistant
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file:
    ```env
    GEMINI_API_KEY=your_gemini_api_key
    OPENAI_API_KEY=your_openai_api_key
    ```

4. Run the app:
    ```bash
    streamlit run app.py
    ```

---

## 🔗 Demo Link

[Click here to try the app (Streamlit Cloud)](https://share.streamlit.io/your-demo-link-here)

> Replace this with the actual demo link once deployed!

---

## 📂 Project Structure

Custom_Home_Design_Assistant/
├── app.py
├── .env # NOT pushed to GitHub
├── requirements.txt
├── utils/
│ ├── gemini_generator.py
│ ├── openai_generator.py
│ └── lexica_image.py
└── README.md