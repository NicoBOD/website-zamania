import os

path = '/opt/data/website-zamania/images/blog/img-ia-automatisation-reporting-syntheses-executives.jpg'
size = os.path.getsize(path)
with open(path, 'rb') as f:
    magic = f.read(3).hex().upper()

print(f"Size: {size} bytes")
print(f"Magic: {magic}")
