import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventario_ropa.settings')
django.setup()

from tienda.models import Producto
from django.utils.text import slugify

def fix_slugs():
    # Fix products with slug being None or literally 'None' or empty
    productos = Producto.objects.all()
    count = 0
    for p in productos:
        if not p.slug or p.slug.lower() == 'none' or p.slug.lower() == 'ninguno':
            old_slug = p.slug
            p.slug = slugify(p.nombre)
            # Ensure uniqueness if needed - though currently the model says unique=False
            p.save()
            print(f"Fixed: '{p.nombre}' ( {old_slug} -> {p.slug} )")
            count += 1
    
    print(f"\nTotal fixed: {count}")

if __name__ == "__main__":
    fix_slugs()
