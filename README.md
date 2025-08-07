# 🏡 AI Home Layout Generator

A powerful Streamlit-based application that generates personalized home layout ideas using advanced AI technology. Create stunning interior designs with AI-generated descriptions and visualizations tailored to your preferences.

![Python](https://img.shields.io/badge/python-v3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 🎨 AI-Powered Design Generation
- **Multiple AI Providers**: Support for Google Gemini and OpenAI GPT-4
- **Intelligent Layout Descriptions**: Detailed room layouts with furniture placement, color schemes, and lighting suggestions
- **AI Image Generation**: Visual representations using Hugging Face, Pollinations AI, and curated high-quality images

### 🏠 Comprehensive Room Support
- Living Room, Bedroom, Kitchen, Bathroom
- Home Office, Dining Room, Children's Room
- Master Bedroom and more

### 🎭 Multiple Design Styles
- Modern, Contemporary, Traditional
- Minimalist, Scandinavian, Industrial
- Bohemian, Rustic, Mid-Century Modern
- Art Deco, Mediterranean, Farmhouse

### 💰 Budget-Conscious Planning
- Multiple budget ranges from under $1,000 to $30,000+
- Budget-specific recommendations and tips
- Cost-effective design solutions

### 🔧 Advanced Customization
- **Space Size Options**: Small to very large spaces
- **Color Preferences**: 20+ color options with multi-select
- **Special Features**: Built-in storage, reading nooks, smart home integration, and more
- **Additional Requirements**: Custom text input for specific needs

### 📊 Export & Management
- Export all layouts to JSON format
- Session-based layout history
- Clear and organized layout presentation

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- API keys for your chosen AI provider:
  - [Google Gemini API Key](https://makersuite.google.com/app/apikey) (Recommended)
  - [OpenAI API Key](https://platform.openai.com/api-keys) (Alternative)
  - [Hugging Face API Key](https://huggingface.co/settings/tokens) (Optional, for enhanced image generation)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-home-layout-generator.git
   cd ai-home-layout-generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:8501` to start using the application.

## 🔑 API Configuration

### Getting API Keys

#### Google Gemini (Recommended)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key for use in the application

#### OpenAI (Alternative)
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key for use in the application

#### Hugging Face (Optional)
1. Visit [Hugging Face Settings](https://huggingface.co/settings/tokens)
2. Create a new token with read permissions
3. This enables additional AI image generation capabilities

### Using the Application
1. **Configure AI Provider**: Enter your API key in the sidebar
2. **Set Preferences**: Choose room type, style, budget, and size
3. **Customize**: Select colors, features, and add specific requirements
4. **Generate**: Click "Generate Layout Ideas" to create your design
5. **Export**: Save your layouts as JSON for future reference

## 🏗️ Project Structure

```
ai-home-layout-generator/
├── app.py                 # Main Streamlit application
├── ai_services.py         # AI service integrations (Gemini, OpenAI)
├── components.py          # UI components and rendering
├── config.py             # Configuration settings and constants
├── utils.py              # Utility functions
├── requirements.txt      # Python dependencies
├── style.css            # Custom CSS styles
├── test_api.py          # API testing utilities
└── README.md            # Project documentation
```

## 🔧 Configuration

The application uses `config.py` for centralized configuration:

- **AI Models**: Gemini 1.5 Flash, GPT-4
- **Image Generation**: Multiple free services with fallbacks
- **UI Themes**: Customizable color schemes
- **Room Types**: Comprehensive list of supported rooms
- **Design Styles**: Wide variety of interior design styles

## 🎨 Image Generation

The application uses a multi-tier approach for image generation:

1. **Pollinations AI** (Free): Primary image generation service
2. **Hugging Face** (API Key Required): Enhanced AI image generation
3. **Curated Images**: High-quality fallback images from Pexels

## 📱 User Interface

### Sidebar Configuration
- AI provider selection (Gemini/OpenAI)
- API key input with secure password fields
- Generation settings and image quality options
- Export and history management tools

### Main Interface
- **Left Panel**: Preference form with comprehensive options
- **Right Panel**: Generated layout results with images
- **Progress Tracking**: Real-time generation status updates

## 🛠️ Development

### Running Tests
```bash
python test_api.py
```

### Adding New Features
1. **New Room Types**: Add to `config.py` room_types list
2. **New Styles**: Add to `config.py` design_styles list
3. **New AI Providers**: Extend `ai_services.py` AIService class
4. **UI Components**: Add to `components.py`

### Environment Variables
Create a `.env` file for development:
```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_API_KEY=your_hf_api_key_here
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini** for advanced AI text generation
- **OpenAI** for GPT-4 integration
- **Hugging Face** for AI image generation models
- **Pollinations AI** for free image generation services
- **Pexels** for high-quality curated images
- **Streamlit** for the amazing web framework

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/ai-home-layout-generator/issues) page
2. Create a new issue with detailed information
3. Include your Python version, OS, and error messages
