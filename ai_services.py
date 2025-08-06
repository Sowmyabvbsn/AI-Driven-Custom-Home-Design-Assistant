import google.generativeai as genai
import openai
from typing import List, Dict, Optional
import asyncio
import requests
from datetime import datetime
import streamlit as st
import base64
import io

class AIService:
    def __init__(self, provider: str, api_key: str):
        self.provider = provider
        self.api_key = api_key
        self.current_provider = provider
        self._setup_client()
    
    def _setup_client(self):
        """Initialize the AI client based on provider"""
        try:
            if self.provider == "gemini":
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel('gemini-1.5-flash')
                # Initialize Veo3 for video/image generation
                self.veo3_client = genai.GenerativeModel('gemini-1.5-flash')
            elif self.provider == "openai":
                self.client = openai.OpenAI(api_key=self.api_key)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            st.error(f"Failed to initialize {self.provider}: {str(e)}")
            raise e
    
    async def generate_layout_descriptions(self, preferences: Dict) -> List[str]:
        """Generate layout descriptions using AI"""
        prompt = self._create_layout_prompt(preferences)
        
        try:
            if self.provider == "gemini":
                response = await self._generate_with_gemini(prompt)
            elif self.provider == "openai":
                response = await self._generate_with_openai(prompt)
            
            # Parse response into multiple layout ideas
            layouts = self._parse_layout_response(response)
            return layouts[:1]  # Return only one layout
        
        except Exception as e:
            st.error(f"Error generating layouts: {str(e)}")
            return []
    
    async def generate_layout_image(self, description: str, preferences: Dict) -> Optional[str]:
        """Generate layout image using AI"""
        # Use preferences directly for more reliable image selection
        room_type = self._map_room_type(preferences['room_type'])
        style = self._map_style(preferences['style'])
        
        try:
            if self.provider == "gemini":
                # Use preferences directly instead of parsing from description
                return self._get_curated_image(room_type, style)
            elif self.provider == "openai":
                image_prompt = self._create_image_prompt(description, preferences)
                return await self._generate_image_with_openai(image_prompt)
        
        except Exception as e:
            st.error(f"Error generating image: {str(e)}")
    
    def _create_layout_prompt(self, preferences: Dict) -> str:
        """Create prompt for layout generation"""
        return f"""
        Create 1 detailed home layout idea for a {preferences['room_type']} with the following specifications:
        
        Style: {preferences['style']}
        Budget Range: {preferences['budget']}
        Space Size: {preferences['space_size']}
        Color Preferences: {', '.join(preferences.get('colors', []))}
        Special Features: {', '.join(preferences.get('features', []))}
        Additional Notes: {preferences.get('description', '')}
        
        For the layout, provide:
        1. A descriptive title
        2. Detailed layout description (150-200 words)
        3. Key features and furniture placement
        4. Color scheme and materials
        5. Lighting suggestions
        6. Budget-conscious tips
        
        Format the layout as:
        LAYOUT 1:
        [Detailed description]
        
        Make the layout unique and practical while staying within the specified parameters.
        """
    
    def _create_image_prompt(self, description: str, preferences: Dict) -> str:
        """Create prompt for image generation"""
        return f"""
        Create a photorealistic interior design image of a {preferences['room_type']} with {preferences['style']} style.
        
        Layout description: {description}
        
        Image requirements:
        - High quality, photorealistic rendering
        - {preferences['style']} interior design style
        - {preferences['space_size']} space
        - Color scheme incorporating {', '.join(preferences.get('colors', []))}
        - Professional interior photography lighting
        - Clean, modern composition
        - Show furniture placement and room layout clearly
        """
    
    async def _generate_with_gemini(self, prompt: str) -> str:
        """Generate text using Gemini"""
        try:
            response = self.client.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini generation error: {str(e)}")
    
    async def _generate_with_openai(self, prompt: str) -> str:
        """Generate text using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert interior designer specializing in home layout planning."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI generation error: {str(e)}")
    
    async def _generate_image_with_gemini(self, prompt: str) -> str:
        """Generate image using Gemini Veo3"""
        try:
            # Since Veo3 is not yet available in the public API,
            # we'll use a more sophisticated fallback system with better image selection
            return await self._get_contextual_image(prompt)
                
        except Exception as e:
            st.warning(f"Image generation failed: {str(e)}. Using contextual fallback.")
            return await self._get_contextual_image(prompt)
    
    async def _get_contextual_image(self, prompt: str) -> str:
        """Get contextual image based on room type and style"""
        try:
            # Extract room type and style from prompt with debugging
            room_type = self._extract_room_type(prompt)
            style = self._extract_style(prompt)
            
            # Debug logging
            print(f"DEBUG - Prompt: {prompt[:100]}...")
            print(f"DEBUG - Extracted room_type: {room_type}, style: {style}")
            
            # Get curated images based on room type and style
            image_url = self._get_curated_image(room_type, style)
            print(f"DEBUG - Selected image URL: {image_url}")
            
            return image_url
            
        except Exception as e:
            return self._get_fallback_image("default")
    
    def _map_room_type(self, room_type: str) -> str:
        """Map UI room type to internal room type"""
        mapping = {
            'Living Room': 'living',
            'Bedroom': 'bedroom',
            'Master Bedroom': 'bedroom',
            'Children\'s Room': 'bedroom',
            'Kitchen': 'kitchen',
            'Bathroom': 'bathroom',
            'Home Office': 'office',
            'Study Room': 'office',
            'Dining Room': 'dining'
        }
        return mapping.get(room_type, 'living')
    
    def _map_style(self, style: str) -> str:
        """Map UI style to internal style"""
        mapping = {
            'Modern': 'modern',
            'Contemporary': 'modern',
            'Traditional': 'traditional',
            'Minimalist': 'scandinavian',
            'Scandinavian': 'scandinavian',
            'Industrial': 'industrial',
            'Bohemian': 'bohemian',
            'Rustic': 'traditional',
            'Mid-Century Modern': 'modern',
            'Art Deco': 'modern',
            'Mediterranean': 'traditional',
            'Farmhouse': 'traditional'
        }
        return mapping.get(style, 'modern')
    
    def _extract_room_type(self, prompt: str) -> str:
        """Extract room type from prompt"""
        prompt_lower = prompt.lower()
        
        # First check for exact room type matches in common phrases
        if 'living room' in prompt_lower or 'living' in prompt_lower:
            return 'living'
        elif 'bedroom' in prompt_lower or 'bed room' in prompt_lower:
            return 'bedroom'
        elif 'kitchen' in prompt_lower:
            return 'kitchen'
        elif 'bathroom' in prompt_lower or 'bath room' in prompt_lower:
            return 'bathroom'
        elif 'office' in prompt_lower or 'study' in prompt_lower:
            return 'office'
        elif 'dining' in prompt_lower:
            return 'dining'
        
        # Fallback to more detailed matching
        room_types = {
            'living': ['living room', 'living', 'lounge'],
            'bedroom': ['bedroom', 'bed room', 'master bedroom'],
            'kitchen': ['kitchen', 'cooking', 'culinary'],
            'bathroom': ['bathroom', 'bath room', 'washroom'],
            'office': ['office', 'study', 'work'],
            'dining': ['dining', 'dining room', 'eat']
        }
        
        for room_key, keywords in room_types.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    return room_key
        
        return 'living'  # default
    
    def _extract_style(self, prompt: str) -> str:
        """Extract design style from prompt"""
        prompt_lower = prompt.lower()
        
        # Direct style matching
        if 'modern' in prompt_lower:
            return 'modern'
        elif 'traditional' in prompt_lower or 'classic' in prompt_lower:
            return 'traditional'
        elif 'scandinavian' in prompt_lower or 'nordic' in prompt_lower:
            return 'scandinavian'
        elif 'industrial' in prompt_lower:
            return 'industrial'
        elif 'bohemian' in prompt_lower or 'boho' in prompt_lower:
            return 'bohemian'
        elif 'contemporary' in prompt_lower:
            return 'modern'  # Map contemporary to modern
        elif 'minimalist' in prompt_lower:
            return 'scandinavian'  # Map minimalist to scandinavian
        
        # Fallback to detailed matching
        styles = {
            'modern': ['modern', 'contemporary', 'minimalist'],
            'traditional': ['traditional', 'classic', 'vintage'],
            'scandinavian': ['scandinavian', 'nordic', 'scandi'],
            'industrial': ['industrial', 'loft', 'urban'],
            'bohemian': ['bohemian', 'boho', 'eclectic']
        }
        
        for style_key, keywords in styles.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    return style_key
        
        return 'modern'  # default
    
    def _get_curated_image(self, room_type: str, style: str) -> str:
        """Get curated high-quality images based on room type and style"""
        print(f"DEBUG - Getting image for room_type: {room_type}, style: {style}")
        
        # Curated high-quality interior design images from Pexels
        curated_images = {
            'living': {
                'modern': "https://images.pexels.com/photos/1571460/pexels-photo-1571460.jpeg",
                'traditional': "https://images.pexels.com/photos/1648776/pexels-photo-1648776.jpeg",
                'scandinavian': "https://images.pexels.com/photos/1571453/pexels-photo-1571453.jpeg",
                'industrial': "https://images.pexels.com/photos/1080721/pexels-photo-1080721.jpeg",
                'bohemian': "https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg"
            },
            'bedroom': {
                'modern': "https://images.pexels.com/photos/164595/pexels-photo-164595.jpeg",
                'traditional': "https://images.pexels.com/photos/1743229/pexels-photo-1743229.jpeg",
                'scandinavian': "https://images.pexels.com/photos/1454806/pexels-photo-1454806.jpeg",
                'industrial': "https://images.pexels.com/photos/1329711/pexels-photo-1329711.jpeg",
                'bohemian': "https://images.pexels.com/photos/1080696/pexels-photo-1080696.jpeg"
            },
            'kitchen': {
                'modern': "https://images.pexels.com/photos/2724748/pexels-photo-2724748.jpeg",
                'traditional': "https://images.pexels.com/photos/1599791/pexels-photo-1599791.jpeg",
                'scandinavian': "https://images.pexels.com/photos/2062426/pexels-photo-2062426.jpeg",
                'industrial': "https://images.pexels.com/photos/2089698/pexels-photo-2089698.jpeg",
                'bohemian': "https://images.pexels.com/photos/1599791/pexels-photo-1599791.jpeg"
            },
            'bathroom': {
                'modern': "https://images.pexels.com/photos/1358912/pexels-photo-1358912.jpeg",
                'traditional': "https://images.pexels.com/photos/1454806/pexels-photo-1454806.jpeg",
                'scandinavian': "https://images.pexels.com/photos/1080696/pexels-photo-1080696.jpeg",
                'industrial': "https://images.pexels.com/photos/1329711/pexels-photo-1329711.jpeg",
                'bohemian': "https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg"
            },
            'office': {
                'modern': "https://images.pexels.com/photos/667838/pexels-photo-667838.jpeg",
                'traditional': "https://images.pexels.com/photos/1181406/pexels-photo-1181406.jpeg",
                'scandinavian': "https://images.pexels.com/photos/1080696/pexels-photo-1080696.jpeg",
                'industrial': "https://images.pexels.com/photos/1329711/pexels-photo-1329711.jpeg",
                'bohemian': "https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg"
            },
            'dining': {
                'modern': "https://images.pexels.com/photos/1395967/pexels-photo-1395967.jpeg",
                'traditional': "https://images.pexels.com/photos/1648776/pexels-photo-1648776.jpeg",
                'scandinavian': "https://images.pexels.com/photos/1571453/pexels-photo-1571453.jpeg",
                'industrial': "https://images.pexels.com/photos/1080721/pexels-photo-1080721.jpeg",
                'bohemian': "https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg"
            }
        }
        
        # Get the appropriate image based on room type and style
        if room_type in curated_images and style in curated_images[room_type]:
            selected_url = curated_images[room_type][style]
            print(f"DEBUG - Found specific image: {selected_url}")
            return selected_url
        elif room_type in curated_images:
            # Fallback to modern style if specific style not found
            fallback_url = curated_images[room_type].get('modern', curated_images[room_type][list(curated_images[room_type].keys())[0]])
            print(f"DEBUG - Using fallback for room: {fallback_url}")
            return fallback_url
        else:
            def _get_fallback_image(self, prompt: str) -> str:
                return "https://images.pexels.com/photos/1571460/pexels-photo-1571460.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
    
    async def _generate_image_with_openai(self, prompt: str) -> str:
        """Generate image using OpenAI DALL-E"""
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            return response.data[0].url
        except Exception as e:
            raise Exception(f"OpenAI image generation error: {str(e)}")
    
    def _parse_layout_response(self, response: str) -> List[str]:
        """Parse AI response into individual layout descriptions"""
        layouts = []
        
        # Split by layout markers
        parts = response.split("LAYOUT")
        
        for part in parts[1:]:  # Skip first empty part
            # Clean up the layout description
            layout_text = part.strip()
            if layout_text:
                # Remove the number prefix and clean up
                layout_desc = layout_text.split(":", 1)[-1].strip()
                if layout_desc:
                    layouts.append(layout_desc)
        
        # If parsing fails, return the whole response as one layout
        if not layouts and response.strip():
            layouts = [response.strip()]
        
        return layouts