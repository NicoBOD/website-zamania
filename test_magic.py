import os
f='/opt/data/website-zamania/images/blog/img-accelerer-traitement-appels-offres-ia.jpg'
print('Size:', os.path.getsize(f))
with open(f, 'rb') as file:
    print('Magic:', file.read(3).hex().upper())
