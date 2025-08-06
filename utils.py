import json
from typing import Dict, List
from datetime import datetime
import streamlit as st

def save_layout_to_session(layout: Dict):
    """Save a layout to session state"""
    if 'saved_layouts' not in st.session_state:
        st.session_state.saved_layouts = []
    
    # Add timestamp if not present
    if 'saved_at' not in layout:
        layout['saved_at'] = datetime.now().isoformat()
    
    st.session_state.saved_layouts.append(layout)

def get_session_layouts() -> List[Dict]:
    """Get all layouts from session state"""
    return st.session_state.get('generated_layouts', [])

def export_layouts_to_json(layouts: List[Dict]) -> str:
    """Export layouts to JSON format"""
    export_data = {
        'export_timestamp': datetime.now().isoformat(),
        'total_layouts': len(layouts),
        'layouts': layouts
    }
    
    return json.dumps(export_data, indent=2, ensure_ascii=False)

def validate_preferences(preferences: Dict) -> List[str]:
    """Validate user preferences and return list of errors"""
    errors = []
    
    required_fields = ['room_type', 'style', 'budget', 'space_size']
    
    for field in required_fields:
        if not preferences.get(field):
            errors.append(f"{field.replace('_', ' ').title()} is required")
    
    return errors

def format_layout_for_export(layout: Dict) -> Dict:
    """Format layout data for export"""
    return {
        'id': layout.get('id'),
        'title': layout.get('title'),
        'description': layout.get('description'),
        'preferences': layout.get('preferences', {}),
        'ai_provider': layout.get('ai_provider'),
        'generated_at': layout.get('generated_at'),
        'image_url': layout.get('image_url')
    }

def create_layout_summary(layouts: List[Dict]) -> Dict:
    """Create a summary of generated layouts"""
    if not layouts:
        return {'total': 0, 'styles': [], 'room_types': []}
    
    styles = set()
    room_types = set()
    
    for layout in layouts:
        if 'preferences' in layout:
            prefs = layout['preferences']
            styles.add(prefs.get('style', 'Unknown'))
            room_types.add(prefs.get('room_type', 'Unknown'))
    
    return {
        'total': len(layouts),
        'styles': list(styles),
        'room_types': list(room_types),
        'latest_generation': max([layout.get('generated_at', '') for layout in layouts]) if layouts else None
    }

def filter_layouts_by_criteria(layouts: List[Dict], criteria: Dict) -> List[Dict]:
    """Filter layouts based on specified criteria"""
    filtered = []
    
    for layout in layouts:
        matches = True
        prefs = layout.get('preferences', {})
        
        if criteria.get('room_type') and prefs.get('room_type') != criteria['room_type']:
            matches = False
        
        if criteria.get('style') and prefs.get('style') != criteria['style']:
            matches = False
        
        if criteria.get('budget') and prefs.get('budget') != criteria['budget']:
            matches = False
        
        if matches:
            filtered.append(layout)
    
    return filtered