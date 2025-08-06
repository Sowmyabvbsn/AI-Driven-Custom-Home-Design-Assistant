import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime

def render_header():
    """Render the main application header"""
    st.markdown("""
    <div class='main-header'>
        <h1>🏡 AI Home Layout Generator</h1>
        <p>Create personalized home layouts using advanced AI technology</p>
    </div>
    """, unsafe_allow_html=True)

def render_preferences_form() -> Optional[Dict]:
    """Render the layout preferences form"""
    st.markdown("<div class='feature-card'>", unsafe_allow_html=True)
    
    # Room Type Selection
    room_type = st.selectbox(
        "🏠 Room Type",
        options=[
            "Living Room",
            "Bedroom",
            "Kitchen",
            "Bathroom",
            "Home Office",
            "Dining Room",
            "Children's Room",
            "Master Bedroom"
        ],
        help="Select the type of room you want to design"
    )
    
    # Style Preferences
    style = st.selectbox(
        "🎨 Design Style",
        options=[
            "Modern",
            "Contemporary",
            "Traditional",
            "Minimalist",
            "Scandinavian",
            "Industrial",
            "Bohemian",
            "Rustic",
            "Mid-Century Modern",
            "Art Deco"
        ],
        help="Choose your preferred interior design style"
    )
    
    # Budget Range
    budget = st.selectbox(
        "💰 Budget Range",
        options=[
            "Under $1,000",
            "$1,000 - $5,000",
            "$5,000 - $15,000",
            "$15,000 - $30,000",
            "$30,000+"
        ],
        help="Select your budget range for the room design"
    )
    
    # Space Size
    space_size = st.selectbox(
        "📏 Space Size",
        options=[
            "Small (< 100 sq ft)",
            "Medium (100-200 sq ft)",
            "Large (200-400 sq ft)",
            "Very Large (400+ sq ft)"
        ],
        help="Approximate size of the space"
    )
    
    # Color Preferences
    st.subheader("🎨 Color Preferences")
    colors = st.multiselect(
        "Select preferred colors",
        options=[
            "White", "Black", "Gray", "Beige", "Brown",
            "Blue", "Green", "Red", "Yellow", "Purple",
            "Pink", "Orange", "Cream", "Navy", "Teal"
        ],
        default=["White", "Gray"],
        help="Choose colors you'd like to incorporate"
    )
    
    # Special Features
    st.subheader("✨ Special Features")
    features = st.multiselect(
        "Select desired features",
        options=[
            "Built-in Storage",
            "Reading Nook",
            "Work Area",
            "Entertainment Center",
            "Walk-in Closet",
            "En-suite Bathroom",
            "Balcony Access",
            "Fireplace",
            "Bay Window",
            "High Ceilings",
            "Natural Light Focus",
            "Smart Home Integration"
        ],
        help="Choose special features you'd like to include"
    )
    
    # Additional Description
    description = st.text_area(
        "📝 Additional Requirements",
        placeholder="Describe any specific needs, preferences, or constraints...",
        help="Provide any additional details about your vision"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Validate required fields
    if room_type and style and budget and space_size:
        return {
            'room_type': room_type,
            'style': style,
            'budget': budget,
            'space_size': space_size,
            'colors': colors,
            'features': features,
            'description': description
        }
    
    return None

def render_layout_results(layouts: List[Dict]):
    """Render the generated layout results"""
    if not layouts:
        st.info("No layouts generated yet.")
        return
    
    st.write(f"📊 **{len(layouts)}** layouts generated")
    
    for i, layout in enumerate(reversed(layouts)):  # Show newest first
        with st.container():
            st.markdown("<div class='layout-result-card'>", unsafe_allow_html=True)
            
            # Layout header
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.subheader(f"🎨 {layout['title']}")
                st.caption(f"Generated: {_format_timestamp(layout['generated_at'])}")
            
            with col2:
                st.metric("Provider", layout['ai_provider'].upper())
            
            with col3:
                if st.button("💾", key=f"save_{layout['id']}", help="Save layout"):
                    st.success("Layout saved!")
            
            # Layout content
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Layout description
                st.markdown("**📋 Layout Description:**")
                st.write(layout['description'])
                
                # Preferences used
                if 'preferences' in layout:
                    with st.expander("🔧 Generation Settings"):
                        prefs = layout['preferences']
                        st.write(f"**Room:** {prefs['room_type']}")
                        st.write(f"**Style:** {prefs['style']}")
                        st.write(f"**Budget:** {prefs['budget']}")
                        st.write(f"**Size:** {prefs['space_size']}")
                        if prefs.get('colors'):
                            st.write(f"**Colors:** {', '.join(prefs['colors'])}")
                        if prefs.get('features'):
                            st.write(f"**Features:** {', '.join(prefs['features'])}")
            
            with col2:
                # Layout image
                if layout.get('image_url'):
                    st.markdown("**🎨 AI Generated Visualization (Veo3):**")
                    st.image(
                        layout['image_url'],
                        caption="Generated with Gemini Veo3 - Photorealistic Interior Design",
                        use_column_width=True
                    )
                else:
                    st.info("🎬 Veo3 image generation in progress...")
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("---")

def render_layout_card(layout: Dict, index: int):
    """Render individual layout card"""
    st.markdown(f"""
    <div class='layout-result-card'>
        <h3>{layout['title']}</h3>
        <div style='margin: 1rem 0;'>
            <strong>Description:</strong>
            <p>{layout['description'][:200]}...</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def _format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return timestamp