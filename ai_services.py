import google.generativeai as genai
import openai
from typing import List, Dict, Optional
import asyncio
import requests
from datetime import datetime
import streamlit as st
import base64
import io
import replicate
import os
import json

class AIService:
    def __init__(self, provider: str, api_key: str):
        self.provider = provider
        self.api_key = api_key
        self.hf_api_key = None 
        self.current_provider = provider
        self._setup_client()
    
    def _setup_client(self):
        """Initialize the AI client based on provider"""
        try:
            if self.provider == "gemini":
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel('gemini-1.5-flash')
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
            layouts = self._parse_layout_response(response)
            return layouts[:1]  
        
        except Exception as e:
            st.error(f"Error generating layouts: {str(e)}")
            return []
    
    async def generate_layout_image(self, description: str, preferences: Dict) -> Optional[str]:
        """Generate layout image using multiple free AI services"""
        try:
            print("🎨 Trying Pollinations AI...")
            image_url = await self._generate_with_pollinations(description, preferences)
            if image_url:
                return image_url
            print("🎨 Trying Hugging Face...")
            image_url = await self._generate_with_huggingface(description, preferences)
            if image_url:
                return image_url
        
            print("🎨 Using curated fallback image...")
            room_type = self._map_room_type(preferences['room_type'])
            style = self._map_style(preferences['style'])
            return self._get_curated_image(room_type, style)
        
        except Exception as e:
            st.error(f"Error generating image: {str(e)}")
            room_type = self._map_room_type(preferences['room_type'])
            style = self._map_style(preferences['style'])
            return self._get_curated_image(room_type, style)
    
    async def _generate_with_pollinations(self, description: str, preferences: Dict) -> Optional[str]:
        """Generate image using Pollinations AI (free service)"""
        try:
            prompt = self._create_detailed_image_prompt(description, preferences)
            print(f"🌸 Pollinations prompt: {prompt}")
            
            base_url = "https://image.pollinations.ai/prompt/"
            
            import urllib.parse
            encoded_prompt = urllib.parse.quote(prompt)
            params = "?width=512&height=512&model=flux&enhance=true&nologo=true"
            
            image_url = f"{base_url}{encoded_prompt}{params}"
            print(f"🌸 Pollinations URL: {image_url}")
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                print("✅ Pollinations image generated successfully!")
                return image_url
            else:
                print(f"❌ Pollinations failed with status: {response.status_code}")
            
        except Exception as e:
            print(f"❌ Pollinations generation failed: {str(e)}")
        
        return None
    
    async def _generate_with_huggingface(self, description: str, preferences: Dict) -> Optional[str]:
        """Generate image using Hugging Face Inference API with multiple model fallbacks"""
        try:
            if not hasattr(self, 'hf_api_key') or not self.hf_api_key:
                print("❌ No Hugging Face API key provided")
                return None
            prompt = self._create_detailed_image_prompt(description, preferences)
            print(f"🎨 Image prompt: {prompt}")
            models = [
                "stabilityai/stable-diffusion-xl-base-1.0",
                "CompVis/stable-diffusion-v1-4",
                "runwayml/stable-diffusion-v1-5"
            ]
            dimensions = self._get_image_dimensions_js_style(preferences.get('space_size', 'Medium'))
            print(f"📐 Image dimensions: {dimensions}")
            
            for model in models:
                try:
                    api_url = f"https://api-inference.huggingface.co/models/{model}"
                    print(f"🔄 Trying model: {model}")
                    
                    headers = {
                        "Authorization": f"Bearer {self.hf_api_key}",
                        "Content-Type": "application/json",
                    }
                    payload = {
                        "inputs": prompt,
                        "parameters": {}
                    }
                    
                    print(f"📤 Sending request to: {api_url}")
                    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
                    
                    response = requests.post(api_url, headers=headers, json=payload, timeout=30)
                    print(f"📥 Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        print(f"📄 Content type: {content_type}")
                        
                        if 'image' in content_type and len(response.content) > 1000:
                            image_data = response.content
                            encoded_image = base64.b64encode(image_data).decode()
                            print(f"✅ Successfully generated image with {model}")
                            return f"data:image/png;base64,{encoded_image}"
                        else:
                            try:
                                error_data = response.json()
                                print(f"❌ API returned JSON error: {error_data}")
                                continue
                            except json.JSONDecodeError:
                                print(f"❌ Invalid response format from {model}")
                                continue
                    
                    elif response.status_code in [503, 404]:
                        print(f"❌ Model {model} unavailable ({response.status_code}), trying next...")
                        continue
                    elif response.status_code == 429:
                        print(f"Rate limited for model {model}, trying next...")
                        continue
                    else:
                        print(f"❌ Model {model} failed ({response.status_code})")
                        continue
                        
                except Exception as model_error:
                    print(f"❌ Exception with model {model}: {str(model_error)}")
                    continue
            
            print("❌ All Hugging Face models failed")
            
        except Exception as e:
            print(f"Hugging Face generation failed: {str(e)}")
        
        return None
    
    def _get_image_dimensions_js_style(self, space_size: str) -> Dict[str, int]:
        """Get image dimensions matching JavaScript implementation"""
        base_size = 512
        aspect_ratio = "1/1"
        width_ratio, height_ratio = map(int, aspect_ratio.split("/"))
        
        scale_factor = base_size / (width_ratio * height_ratio) ** 0.5
        calculated_width = round(width_ratio * scale_factor)
        calculated_height = round(height_ratio * scale_factor)
     
        calculated_width = (calculated_width // 16) * 16
        calculated_height = (calculated_height // 16) * 16
        if calculated_width < 512:
            calculated_width = 512
        if calculated_height < 512:
            calculated_height = 512
            
        size_map = {
            'Small (< 100 sq ft)': {'width': calculated_width, 'height': calculated_height},
            'Medium (100-200 sq ft)': {'width': calculated_width, 'height': calculated_height},
            'Large (200-400 sq ft)': {'width': calculated_width, 'height': calculated_height},
            'Very Large (400+ sq ft)': {'width': calculated_width, 'height': calculated_height}
        }
        
        return size_map.get(space_size, {'width': calculated_width, 'height': calculated_height})
    
    def _create_detailed_image_prompt(self, description: str, preferences: Dict) -> str:
        """Create a detailed prompt optimized for image generation"""
        room_type = preferences['room_type']
        style = preferences['style']
        colors = ', '.join(preferences.get('colors', ['white', 'gray']))
        prompt = f"A beautiful {style.lower()} {room_type.lower()} interior design with {colors} color scheme, professional interior photography, high quality, well-lit, photorealistic"
        
        return prompt
    
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
    
    def _get_curated_image(self, room_type: str, style: str) -> str:
        """Get curated high-quality images based on room type and style"""
        curated_images = {
            'living': {
                'modern': [
                    "https://images.pexels.com/photos/1571460/pexels-photo-1571460.jpeg",
                    "https://images.pexels.com/photos/2062426/pexels-photo-2062426.jpeg",
                    "https://images.pexels.com/photos/1080721/pexels-photo-1080721.jpeg"
                ],
                'traditional': [
                    "https://images.pexels.com/photos/1648776/pexels-photo-1648776.jpeg",
                    "https://images.pexels.com/photos/1743229/pexels-photo-1743229.jpeg",
                    "https://images.pexels.com/photos/1395967/pexels-photo-1395967.jpeg"
                ],
                'scandinavian': [
                    "https://images.pexels.com/photos/1571453/pexels-photo-1571453.jpeg",
                    "https://images.pexels.com/photos/1454806/pexels-photo-1454806.jpeg",
                    "https://images.pexels.com/photos/2062426/pexels-photo-2062426.jpeg"
                ],
                'industrial': [
                    "https://images.pexels.com/photos/1080721/pexels-photo-1080721.jpeg",
                    "https://images.pexels.com/photos/1329711/pexels-photo-1329711.jpeg",
                    "https://images.pexels.com/photos/2089698/pexels-photo-2089698.jpeg"
                ],
                'bohemian': [
                    "https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg",
                    "https://images.pexels.com/photos/1080696/pexels-photo-1080696.jpeg",
                    "https://images.pexels.com/photos/1743229/pexels-photo-1743229.jpeg"
                ]
            },
            'bedroom': {
                'modern': [
                    "https://images.pexels.com/photos/164595/pexels-photo-164595.jpeg",
                    "https://images.pexels.com/photos/1454806/pexels-photo-1454806.jpeg",
                    "https://images.pexels.com/photos/1080696/pexels-photo-1080696.jpeg"
                ],
                'traditional': [
                    "https://images.pexels.com/photos/1743229/pexels-photo-1743229.jpeg",
                    "https://images.pexels.com/photos/1648776/pexels-photo-1648776.jpeg",
                    "https://images.pexels.com/photos/164595/pexels-photo-164595.jpeg"
                ],
                'scandinavian': [
                    "https://images.pexels.com/photos/1454806/pexels-photo-1454806.jpeg",
                    "https://images.pexels.com/photos/1080696/pexels-photo-1080696.jpeg",
                    "https://images.pexels.com/photos/164595/pexels-photo-164595.jpeg"
                ],
                'industrial': [
                    "https://images.pexels.com/photos/1329711/pexels-photo-1329711.jpeg",
                    "https://images.pexels.com/photos/1080696/pexels-photo-1080696.jpeg",
                    "https://images.pexels.com/photos/164595/pexels-photo-164595.jpeg"
                ],
                'bohemian': [
                    "https://images.pexels.com/photos/1080696/pexels-photo-1080696.jpeg",
                    "https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg",
                    "https://images.pexels.com/photos/1743229/pexels-photo-1743229.jpeg"
                ]
            },
            'kitchen': {
                'modern': [
                    "https://images.pexels.com/photos/2724748/pexels-photo-2724748.jpeg",
                    "https://images.pexels.com/photos/2062426/pexels-photo-2062426.jpeg",
                    "https://images.pexels.com/photos/2089698/pexels-photo-2089698.jpeg"
                ],
                'traditional': [
                    "https://images.pexels.com/photos/1599791/pexels-photo-1599791.jpeg",
                    "https://images.pexels.com/photos/2724748/pexels-photo-2724748.jpeg",
                    "https://images.pexels.com/photos/1648776/pexels-photo-1648776.jpeg"
                ],
                'scandinavian': [
                    "https://images.pexels.com/photos/2062426/pexels-photo-2062426.jpeg",
                    "https://images.pexels.com/photos/2724748/pexels-photo-2724748.jpeg",
                    "https://images.pexels.com/photos/1599791/pexels-photo-1599791.jpeg"
                ],
                'industrial': [
                    "https://images.pexels.com/photos/2089698/pexels-photo-2089698.jpeg",
                    "https://images.pexels.com/photos/2724748/pexels-photo-2724748.jpeg",
                    "https://images.pexels.com/photos/1599791/pexels-photo-1599791.jpeg"
                ],
                'bohemian': [
                    "https://images.pexels.com/photos/1599791/pexels-photo-1599791.jpeg",
                    "https://images.pexels.com/photos/2724748/pexels-photo-2724748.jpeg",
                    "https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg"
                ]
            },
            'bathroom': {
                'modern': [
                    "https://images.pexels.com/photos/1358912/pexels-photo-1358912.jpeg",
                    "https://images.pexels.com/photos/2062426/pexels-photo-2062426.jpeg",
                    "https://images.pexels.com/photos/1080721/pexels-photo-1080721.jpeg"
                ],
                'traditional': [
                    "https://images.pexels.com/photos/1454806/pexels-photo-1454806.jpeg",
                    "https://images.pexels.com/photos/1358912/pexels-photo-1358912.jpeg",
                    "https://images.pexels.com/photos/1648776/pexels-photo-1648776.jpeg"
                ],
                'scandinavian': [
                    "https://images.pexels.com/photos/1080696/pexels-photo-1080696.jpeg",
                    "https://images.pexels.com/photos/1358912/pexels-photo-1358912.jpeg",
                    "https://images.pexels.com/photos/2062426/pexels-photo-2062426.jpeg"
                ],
                'industrial': [
                    "https://images.pexels.com/photos/1329711/pexels-photo-1329711.jpeg",
                    "https://images.pexels.com/photos/1358912/pexels-photo-1358912.jpeg",
                    "https://images.pexels.com/photos/1080721/pexels-photo-1080721.jpeg"
                ],
                'bohemian': [
                    "https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg",
                    "https://images.pexels.com/photos/1358912/pexels-photo-1358912.jpeg",
                    "https://images.pexels.com/photos/1080696/pexels-photo-1080696.jpeg"
                ]
            },
            'office': {
                'modern': [
                    "https://images.pexels.com/photos/667838/pexels-photo-667838.jpeg",
                    "https://images.pexels.com/photos/1181406/pexels-photo-1181406.jpeg",
                    "https://images.pexels.com/photos/1080721/pexels-photo-1080721.jpeg"
                ],
                'traditional': [
                    "https://images.pexels.com/photos/1181406/pexels-photo-1181406.jpeg",
                    "https://images.pexels.com/photos/667838/pexels-photo-667838.jpeg",
                    "https://images.pexels.com/photos/1648776/pexels-photo-1648776.jpeg"
                ],
                'scandinavian': [
                    "https://images.pexels.com/photos/1080696/pexels-photo-1080696.jpeg",
                    "https://images.pexels.com/photos/667838/pexels-photo-667838.jpeg",
                    "https://images.pexels.com/photos/1181406/pexels-photo-1181406.jpeg"
                ],
                'industrial': [
                    "https://images.pexels.com/photos/1329711/pexels-photo-1329711.jpeg",
                    "https://images.pexels.com/photos/667838/pexels-photo-667838.jpeg",
                    "https://images.pexels.com/photos/1080721/pexels-photo-1080721.jpeg"
                ],
                'bohemian': [
                    "https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg",
                    "https://images.pexels.com/photos/667838/pexels-photo-667838.jpeg",
                    "https://images.pexels.com/photos/1181406/pexels-photo-1181406.jpeg"
                ]
            },
            'dining': {
                'modern': [
                    "https://images.pexels.com/photos/1395967/pexels-photo-1395967.jpeg",
                    "https://images.pexels.com/photos/2062426/pexels-photo-2062426.jpeg",
                    "https://images.pexels.com/photos/1080721/pexels-photo-1080721.jpeg"
                ],
                'traditional': [
                    "https://images.pexels.com/photos/1648776/pexels-photo-1648776.jpeg",
                    "https://images.pexels.com/photos/1395967/pexels-photo-1395967.jpeg",
                    "https://images.pexels.com/photos/1743229/pexels-photo-1743229.jpeg"
                ],
                'scandinavian': [
                    "https://images.pexels.com/photos/1571453/pexels-photo-1571453.jpeg",
                    "https://images.pexels.com/photos/1395967/pexels-photo-1395967.jpeg",
                    "https://images.pexels.com/photos/2062426/pexels-photo-2062426.jpeg"
                ],
                'industrial': [
                    "https://images.pexels.com/photos/1080721/pexels-photo-1080721.jpeg",
                    "https://images.pexels.com/photos/1395967/pexels-photo-1395967.jpeg",
                    "https://images.pexels.com/photos/1329711/pexels-photo-1329711.jpeg"
                ],
                'bohemian': [
                    "https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg",
                    "https://images.pexels.com/photos/1395967/pexels-photo-1395967.jpeg",
                    "https://images.pexels.com/photos/1743229/pexels-photo-1743229.jpeg"
                ]
            }
        }
        
        if room_type in curated_images and style in curated_images[room_type]:
            images = curated_images[room_type][style]
            import time
            index = int(time.time()) % len(images)
            return images[index]
        elif room_type in curated_images:
            fallback_images = curated_images[room_type].get('modern', list(curated_images[room_type].values())[0])
            index = int(time.time()) % len(fallback_images)
            return fallback_images[index]
        else:
            return "https://images.pexels.com/photos/1571460/pexels-photo-1571460.jpeg"
    
    def _parse_layout_response(self, response: str) -> List[str]:
        """Parse AI response into individual layout descriptions"""
        layouts = []
        parts = response.split("LAYOUT")
        
        for part in parts[1:]: 
            layout_text = part.strip()
            if layout_text:
                layout_desc = layout_text.split(":", 1)[-1].strip()
                if layout_desc:
                    layouts.append(layout_desc)
        if not layouts and response.strip():
            layouts = [response.strip()]
        
        return layouts