import requests

# Function to fetch image from Lexica.art using search prompt
def fetch_lexica_image(prompt):
    try:
        url = f"https://lexica.art/api/v1/search?q={prompt}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data.get("images") and len(data["images"]) > 0:
                return data["images"][0]["src"]
        return None
    except Exception as e:
        return None
