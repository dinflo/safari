from .views import get_or_create_cart

def cart_processor(request):
    """
    Context processor to add the cart object to all templates.
    """
    # Evitar acceder a la sesión si no es necesario (opcional)
    # pero para el carrito dinámico es mejor tenerlo siempre
    try:
        carrito = get_or_create_cart(request)
        return {'carrito_global': carrito}
    except Exception:
        return {'carrito_global': None}
