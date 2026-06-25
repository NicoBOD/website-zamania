from PIL import Image, ImageDraw, ImageFont
import random

width, height = 1920, 1080
image = Image.new("RGB", (width, height), (240, 245, 250))
draw = ImageDraw.Draw(image)

# Draw a professional gradient/shapes
for i in range(100):
    x1 = random.randint(0, width)
    y1 = random.randint(0, height)
    x2 = x1 + random.randint(100, 500)
    y2 = y1 + random.randint(100, 500)
    color = (random.randint(200, 255), random.randint(220, 255), random.randint(240, 255))
    draw.rectangle([x1, y1, x2, y2], fill=color)

# Draw a main rect
draw.rectangle([400, 300, 1520, 780], fill=(255, 255, 255), outline=(0, 100, 200), width=5)

image.save("/opt/data/website-zamania/images/blog/img-fluidifiez-integration-onboarding-rh-agent-virtuel.jpg", "JPEG", quality=95)
