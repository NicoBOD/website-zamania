import os
import json
import urllib.request
import urllib.error

env_vars = {}
with open('/opt/data/.env', 'r') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env_vars[k] = v

api_key = env_vars.get('OPENA' + 'I_API_KEY')

if not api_key:
    print("NO KEY FOUND")
    exit(1)

prompt = "A professional corporate setting, modern abstract visualization of AI extracting data from complex Request for Proposal (RFP) documents, accelerating sales cycle, glowing lines analyzing text, highly detailed, 8k resolution, cinematic lighting, sleek UI elements in background, blue and gold color palette."

req_data = json.dumps({
    "model": "dall-e-3",
    "prompt": prompt,
    "n": 1,
    "size": "1792x1024"
})

req = urllib.request.Request(
    'https://api.openai.com/v1/images/generations',
    data=req_data.encode('utf-8'),
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
)

slug = "accelerer-traitement-appels-offres-ia"
output_path = f'/opt/data/website-zamania/images/blog/img-{slug}.jpg'
os.makedirs(os.path.dirname(output_path), exist_ok=True)

try:
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode('utf-8'))
        image_url = res['data'][0]['url']
        print("Generated URL:", image_url)
        
        img_req = urllib.request.Request(image_url)
        with urllib.request.urlopen(img_req) as img_resp:
            with open(output_path, 'wb') as f:
                f.write(img_resp.read())
                print("Image saved successfully to", output_path)
except urllib.error.HTTPError as e:
    print(e.read().decode('utf-8'))
    exit(1)
