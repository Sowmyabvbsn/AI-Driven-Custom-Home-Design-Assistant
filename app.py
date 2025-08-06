import streamlit as st
import asyncio
from datetime import datetime
import json
from typing import Dict, List, Optional

from ai_services import AIService
from components import render_header, render_preferences_form, render_layout_results
from utils import save_layout_to_session, get_session_layouts, export_layouts_to_json
from config import APP_CONFIG

# Configure Streamlit page
st.set_page_config(
    page_title="AI Home Layout Generator",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    .layout-result-card {
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease;
    }
    
    .layout-result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
    }
    
    .generate-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: bold;
        width: 100%;
    }
    
    .sidebar-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'generated_layouts' not in st.session_state:
        st.session_state.generated_layouts = []
    if 'ai_service' not in st.session_state:
        st.session_state.ai_service = None
    if 'generation_history' not in st.session_state:
        st.session_state.generation_history = []

async def generate_layout_ideas(preferences: Dict, ai_service: AIService) -> List[Dict]:
    """Generate layout ideas using AI service"""
    try:
        # Generate layout descriptions
        layout_descriptions = await ai_service.generate_layout_descriptions(preferences)
        
        results = []
        for i, description in enumerate(layout_descriptions):
            # Generate image for each layout
            image_url = await ai_service.generate_layout_image(description, preferences)
            
            result = {
                'id': f"layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}",
                'title': f"{preferences['style']} {preferences['room_type']} Layout #{i+1}",
                'description': description,
                'image_url': image_url,
                'preferences': preferences,
                'generated_at': datetime.now().isoformat(),
                'ai_provider': ai_service.current_provider
            }
            results.append(result)
        
        return results
    
    except Exception as e:
        st.error(f"Error generating layouts: {str(e)}")
        return []

def main():
    load_css()
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Sidebar for API configuration and settings
    with st.sidebar:
        st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
        st.subheader("🔧 AI Configuration")
        
        # API provider selection
        provider = st.selectbox(
            "Select AI Provider",
            options=["gemini", "openai"],
            index=0,
            help="Choose your preferred AI provider for generating layouts"
        )
        
        # API key input
        api_key = st.text_input(
            f"{provider.upper()} API Key",
            type="password",
            help=f"Enter your {provider.upper()} API key"
        )
        
        if api_key:
            st.session_state.ai_service = AIService(provider=provider, api_key=api_key)
            st.success(f"✅ {provider.upper()} configured successfully!")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Generation settings
        st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
        st.subheader("⚙️ Generation Settings")
        
        st.info("📋 Generating 1 layout per request for optimal quality")
        
        image_quality = st.selectbox(
            "Image Quality",
            options=["standard", "hd"],
            index=0,
            help="HD images take longer but look better"
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # History and export
        if st.session_state.generated_layouts:
            st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
            st.subheader("📋 Export Options")
            
            if st.button("📤 Export All Layouts"):
                export_data = export_layouts_to_json(st.session_state.generated_layouts)
                st.download_button(
                    label="Download JSON",
                    data=export_data,
                    file_name=f"home_layouts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            if st.button("🗑️ Clear History"):
                st.session_state.generated_layouts = []
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🏠 Layout Preferences")
        
        # Check if AI service is configured
        if not st.session_state.ai_service:
            st.warning("⚠️ Please configure your AI provider in the sidebar to get started.")
            st.stop()
        
        # Render preferences form
        preferences = render_preferences_form()
        
        # Generate button
        if st.button("✨ Generate Layout Ideas", type="primary", use_container_width=True):
            if not preferences:
                st.error("Please fill in all required preferences.")
                return
            
            with st.spinner("🎨 Generating your personalized home layouts..."):
                # Create progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Update progress
                    status_text.text("🧠 Generating layout descriptions...")
                    progress_bar.progress(25)
                    
                    # Update progress for image generation
                    progress_bar.progress(50)
                    status_text.text("🎨 Generating AI layout images...")
                    
                    # Generate layouts
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    results = loop.run_until_complete(
                        generate_layout_ideas(preferences, st.session_state.ai_service)
                    )
                    
                    progress_bar.progress(90)
                    status_text.text("🖼️ Finalizing layout presentation...")
                    
                    if results:
                        # Save to session state
                        st.session_state.generated_layouts.extend(results)
                        
                        progress_bar.progress(100)
                        status_text.text("✅ Layouts generated successfully!")
                        
                        st.success(f"🎉 Generated {len(results)} layout ideas!")
                        st.rerun()
                    else:
                        st.error("Failed to generate layouts. Please try again.")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                
                finally:
                    progress_bar.empty()
                    status_text.empty()
    
    with col2:
        st.subheader("🎨 Generated Layouts")
        
        if st.session_state.generated_layouts:
            render_layout_results(st.session_state.generated_layouts)
        else:
            st.info("👈 Configure your preferences and click 'Generate Layout Ideas' to see results here.")

if __name__ == "__main__":
    main()