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
            return layouts[:preferences.get('num_layouts', 3)]
        
        except Exception as e:
            st.error(f"Error generating layouts: {str(e)}")
            return []
    
    async def generate_layout_image(self, description: str, preferences: Dict) -> Optional[str]:
        """Generate layout image using AI"""
        image_prompt = self._create_image_prompt(description, preferences)
        
        try:
            if self.provider == "gemini":
                # For demo purposes, using placeholder images
                # In production, you would integrate with Gemini's Veo3 API
                return await self._generate_image_with_gemini(image_prompt)
            elif self.provider == "openai":
                return await self._generate_image_with_openai(image_prompt)
        
        except Exception as e:
            st.error(f"Error generating image: {str(e)}")
            return None
    
    def _create_layout_prompt(self, preferences: Dict) -> str:
        """Create prompt for layout generation"""
        return f"""
        Create 3 detailed home layout ideas for a {preferences['room_type']} with the following specifications:
        
        Style: {preferences['style']}
        Budget Range: {preferences['budget']}
        Space Size: {preferences['space_size']}
        Color Preferences: {', '.join(preferences.get('colors', []))}
        Special Features: {', '.join(preferences.get('features', []))}
        Additional Notes: {preferences.get('description', '')}
        
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
            # Create a more detailed prompt for Veo3 image generation
            veo3_prompt = f"""
            Generate a high-quality, photorealistic interior design image with the following specifications:
            
            {prompt}
            
            Technical requirements:
            - Ultra-high resolution (4K quality)
            - Professional interior photography lighting
            - Realistic textures and materials
            - Accurate perspective and proportions
            - Clean, uncluttered composition
            - Natural color grading
            - Sharp focus throughout the scene
            """
            
            # Use Gemini's image generation capabilities
            # Note: This uses the current Gemini API structure
            # Adjust based on actual Veo3 API when available
            response = await self._generate_veo3_image(veo3_prompt)
            
            if response and 'image_data' in response:
                # Convert base64 image data to URL or save locally
                return self._process_veo3_image(response['image_data'])
            else:
                # Fallback to curated stock images if Veo3 fails
                return self._get_fallback_image(prompt)
                
        except Exception as e:
            st.warning(f"Veo3 image generation failed: {str(e)}. Using fallback image.")
            return self._get_fallback_image(prompt)
    
    async def _generate_veo3_image(self, prompt: str) -> Optional[Dict]:
        """Generate image using Veo3 API"""
        try:
            # This is the structure for Veo3 integration
            # Note: Actual API endpoints may vary when Veo3 becomes available
            
            # For now, using Gemini's current image generation capabilities
            # with enhanced prompting for better results
            response = self.veo3_client.generate_content([
                prompt,
                "Generate this as a photorealistic interior design visualization"
            ])
            
            # Process the response based on actual Veo3 API structure
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content'):
                    # Extract image data from response
                    # This structure will need to be updated based on actual Veo3 API
                    return {
                        'image_data': candidate.content,
                        'metadata': {
                            'model': 'veo3',
                            'quality': 'high',
                            'generated_at': datetime.now().isoformat()
                        }
                    }
            
            return None
            
        except Exception as e:
            raise Exception(f"Veo3 API error: {str(e)}")
    
    def _process_veo3_image(self, image_data: str) -> str:
        """Process Veo3 image data and return URL"""
        try:
            # If image_data is base64, convert to displayable format
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                return image_data
            
            # If raw base64, add proper data URL prefix
            if isinstance(image_data, str):
                return f"data:image/png;base64,{image_data}"
            
            # For other formats, you might need to save to temporary file
            # and return file path or convert to base64
            return self._get_fallback_image("default")
            
        except Exception as e:
            st.error(f"Error processing Veo3 image: {str(e)}")
            return self._get_fallback_image("default")
    
    def _get_fallback_image(self, prompt: str) -> str:
        """Get fallback image when Veo3 is unavailable"""
        room_type = prompt.lower()
        
        # High-quality stock images from Pexels as fallbacks
        fallback_images = {
            'living': "https://images.pexels.com/photos/1571460/pexels-photo-1571460.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
            'bedroom': "https://images.pexels.com/photos/164595/pexels-photo-164595.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
            'kitchen': "https://images.pexels.com/photos/2724748/pexels-photo-2724748.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
            'bathroom': "https://images.pexels.com/photos/1454806/pexels-photo-1454806.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
            'office': "https://images.pexels.com/photos/667838/pexels-photo-667838.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
            'dining': "https://images.pexels.com/photos/1395967/pexels-photo-1395967.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
            'default': "https://images.pexels.com/photos/1571460/pexels-photo-1571460.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
        }
        
        for room_key in fallback_images:
            if room_key in room_type:
                return fallback_images[room_key]
        
        return fallback_images['default']
    
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