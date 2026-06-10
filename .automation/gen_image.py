import os
from PIL import Image, ImageDraw, ImageFont

def generate_image(path, title):
    # Create a 16:9 image (1920x1080)
    width, height = 1920, 1080
    image = Image.new('RGB', (width, height), color=(26, 35, 50))
    draw = ImageDraw.Draw(image)
    
    # Draw a gradient or some shapes for a professional tech look
    for i in range(height):
        r = int(26 + (201 - 26) * i / height * 0.3)
        g = int(35 + (160 - 35) * i / height * 0.3)
        b = int(50 + (95 - 50) * i / height * 0.3)
        draw.line([(0, i), (width, i)], fill=(r, g, b))
        
    # Draw some abstract circles
    draw.ellipse([(1200, -200), (2200, 800)], outline=(201, 160, 95), width=10)
    draw.ellipse([(-300, 600), (500, 1400)], outline=(201, 160, 95), width=5)
    
    try:
        # Try to use a default font or system font
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 80)
    except:
        font = ImageFont.load_default(size=80)
        
    # Add text
    text = "ZamanIA - " + title
    
    # Simple text wrapping (rough)
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        if len(" ".join(current_line)) > 30:
            lines.append(" ".join(current_line[:-1]))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
        
    y_text = 400
    for line in lines:
        try:
            bbox = draw.textbbox((0,0), line, font=font)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]
        except AttributeError:
            line_width = len(line) * 45 # rough estimate
            line_height = 80
        draw.text(((width - line_width) / 2, y_text), line, font=font, fill=(255, 255, 255))
        y_text += line_height + 20
        
    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    image.save(path)

# Generate the image
img_path = "/opt/data/website-zamania/images/blog/img-accelerez-signatures-propositions-commerciales.jpg"
generate_image(img_path, "Propositions commerciales IA")
print("Image generated at:", img_path)
