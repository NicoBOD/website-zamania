import json
import urllib.request
import urllib.error
import os

with open('/opt/data/website-zamania/article_temp.json', 'r') as f:
    article_data = json.load(f)

slug = article_data['slug']
print(f"Generating image for {slug}")

url = 'https://api.openai.com/v1/images/generations'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {os.environ.get("OPENAI_API_KEY")}'
}
data = {
    "model": "dall-e-3",
    "prompt": "A professional, minimalist, high-quality, abstract 3D illustration representing business process automation, sales follow-ups, and AI. Wide 16:9 aspect ratio, corporate blue and white color palette, subtle glowing lines, modern technology concept, no text, clean composition.",
    "n": 1,
    "size": "1024x1024",
    "response_format": "url"
}

req = urllib.request.Request(url, json.dumps(data).encode('utf-8'), headers)
try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        image_url = result['data'][0]['url']
        print(f"Generated image URL: {image_url}")
        
        # Download image
        img_req = urllib.request.Request(image_url)
        with urllib.request.urlopen(img_req) as img_response:
            image_data = img_response.read()
            
            image_dir = '/opt/data/website-zamania/images/blog'
            os.makedirs(image_dir, exist_ok=True)
            image_path = os.path.join(image_dir, f'img-{slug}.jpg')
            
            with open(image_path, 'wb') as f:
                f.write(image_data)
            print(f"Image saved to {image_path}")
            
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
