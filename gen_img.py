from PIL import Image, ImageDraw

img = Image.new('RGB', (1920, 1080), color=(15, 32, 39))
d = ImageDraw.Draw(img)
# Simple placeholder
img.save('/opt/data/website-zamania/images/blog/img-ia-triage-priorisation-demandes-clients.jpg')
