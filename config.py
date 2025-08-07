"""Configuration settings for the Home Layout Generator app"""

APP_CONFIG = {
    'app_name': 'AI Home Layout Generator',
    'version': '1.0.0',
    'description': 'Generate personalized home layout ideas using AI',
    
    # AI Configuration
    'supported_providers': ['gemini', 'openai'],
    'default_provider': 'gemini',
    
    # Generation Settings
    'max_layouts_per_request': 5,
    'default_num_layouts': 3,
    'max_description_length': 500,
    
    # Image Settings
    'image_sizes': ['512x512', '1024x1024', '1792x1024'],
    'default_image_size': '1024x1024',
    'image_qualities': ['standard', 'hd'],
    'default_image_quality': 'standard',

    # Free AI Image Generation Services
    'image_services': {
        'pollinations': {
            'base_url': 'https://image.pollinations.ai/prompt/',
            'params': '?width=1024&height=1024&model=flux&enhance=true'
        },
        'huggingface': {
            'api_url': 'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0',
            'model': 'stabilityai/stable-diffusion-xl-base-1.0'
        }
    },
    
    # UI Settings
    'theme_colors': {
        'primary': '#667eea',
        'secondary': '#764ba2',
        'accent': '#f093fb',
        'background': '#f8f9fa',
        'text': '#2c3e50'
    },
    
    # Room Types
    'room_types': [
        'Living Room',
        'Bedroom', 
        'Kitchen',
        'Bathroom',
        'Home Office',
        'Dining Room',
        'Children\'s Room',
        'Master Bedroom',
        'Guest Room',
        'Study Room'
    ],
    
    # Design Styles
    'design_styles': [
        'Modern',
        'Contemporary', 
        'Traditional',
        'Minimalist',
        'Scandinavian',
        'Industrial',
        'Bohemian',
        'Rustic',
        'Mid-Century Modern',
        'Art Deco',
        'Mediterranean',
        'Farmhouse'
    ],
    
    # Budget Ranges
    'budget_ranges': [
        'Under $1,000',
        '$1,000 - $5,000', 
        '$5,000 - $15,000',
        '$15,000 - $30,000',
        '$30,000+'
    ],
    
    # Space Sizes
    'space_sizes': [
        'Small (< 100 sq ft)',
        'Medium (100-200 sq ft)',
        'Large (200-400 sq ft)', 
        'Very Large (400+ sq ft)'
    ],
    
    # Color Options
    'color_options': [
        'White', 'Black', 'Gray', 'Beige', 'Brown',
        'Blue', 'Green', 'Red', 'Yellow', 'Purple',
        'Pink', 'Orange', 'Cream', 'Navy', 'Teal',
        'Burgundy', 'Gold', 'Silver', 'Coral', 'Sage'
    ],
    
    # Feature Options
    'feature_options': [
        'Built-in Storage',
        'Reading Nook',
        'Work Area', 
        'Entertainment Center',
        'Walk-in Closet',
        'En-suite Bathroom',
        'Balcony Access',
        'Fireplace',
        'Bay Window',
        'High Ceilings',
        'Natural Light Focus',
        'Smart Home Integration',
        'Custom Lighting',
        'Statement Wall',
        'Multi-functional Furniture'
    ]
}

# API Configuration Templates
GEMINI_CONFIG = {
    'model': 'gemini-1.5-flash',
    'temperature': 0.7,
    'max_tokens': 1500,
    'image_generation': {
        'quality': 'high',
        'resolution': '1024x1024',
        'style': 'photorealistic'
    }
}

OPENAI_CONFIG = {
    'text_model': 'gpt-4',
    'image_model': 'dall-e-3', 
    'temperature': 0.7,
    'max_tokens': 1500
}

HUGGINGFACE_CONFIG = {
    'models': [
        'stabilityai/stable-diffusion-xl-base-1.0',
        'runwayml/stable-diffusion-v1-5', 
        'stabilityai/stable-diffusion-2-1',
        'CompVis/stable-diffusion-v1-4'
    ],
    'default_params': {
        'num_inference_steps': 25,
        'guidance_scale': 7.5
    }
}

# Prompt Templates
LAYOUT_PROMPT_TEMPLATE = """
Create {num_layouts} detailed home layout ideas for a {room_type} with the following specifications:

Style: {style}
Budget Range: {budget}
Space Size: {space_size}
Color Preferences: {colors}
Special Features: {features}
Additional Notes: {description}

For each layout, provide:
1. A descriptive title
2. Detailed layout description (150-200 words)
3. Key features and furniture placement
4. Color scheme and materials
5. Lighting suggestions
6. Budget-conscious tips

Format each layout as:
LAYOUT [number]:
[Detailed description]

Make each layout unique and practical while staying within the specified parameters.
"""

IMAGE_PROMPT_TEMPLATE = """
Create a photorealistic interior design image of a {room_type} with {style} style.

Layout description: {description}

Image requirements:
- Ultra-high quality, photorealistic rendering using Veo3
- {style} interior design style
- {space_size} space
- Color scheme incorporating {colors}
- Professional interior photography lighting
- Clean, modern composition
- Show furniture placement and room layout clearly
- 4K resolution with sharp details
- Realistic textures and materials
- Natural lighting and shadows
- Accurate architectural proportions
- Interior design magazine quality
"""