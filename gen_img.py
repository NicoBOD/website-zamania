from PIL import Image, ImageDraw
import os
img = Image.new("RGB", (1920, 1080), color=(30, 30, 40))
d = ImageDraw.Draw(img)
for i in range(0, 1920, 20):
    for j in range(0, 1080, 20):
        d.rectangle([i, j, i+10, j+10], fill=(i%255, j%255, (i+j)%255))
img.save("/opt/data/website-zamania/images/blog/img-agent-ia-qualification-leads-entrants.jpg", "JPEG", quality=95)
