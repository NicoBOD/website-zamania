import os
import sys

path = '/opt/data/website-zamania/images/blog/img-automatisation-rapprochement-factures-fournisseurs.jpg'
try:
    size = os.path.getsize(path)
    with open(path, 'rb') as f:
        header = f.read(3)
    is_jpeg = header == b'\xff\xd8\xff'
    print(f'Size: {size} bytes')
    print(f'Is JPEG: {is_jpeg}')
    sys.exit(0 if (is_jpeg and size > 10000) else 1)
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
