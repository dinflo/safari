from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Carrito, CarritoItem

@receiver(user_logged_in)
def fusionar_carrito_al_iniciar_sesion(sender, request, user, **kwargs):
    # Intentar obtener el carrito de la sesión actual
    session_key = request.session.session_key
    if not session_key:
        return

    try:
        carrito_anonimo = Carrito.objects.get(session_key=session_key, usuario__isnull=True)
    except Carrito.DoesNotExist:
        # No hay carrito anónimo para esta sesión
        return

    # Obtener o crear el carrito del usuario
    carrito_usuario, created = Carrito.objects.get_or_create(usuario=user)

    # Mover items del carrito anónimo al carrito del usuario
    items_anonimos = CarritoItem.objects.filter(carrito=carrito_anonimo)
    
    for item_anonimo in items_anonimos:
        # Buscar si el producto (y variante) ya existe en el carrito del usuario
        item_existente, item_created = CarritoItem.objects.get_or_create(
            carrito=carrito_usuario,
            producto=item_anonimo.producto,
            variante=item_anonimo.variante,
            defaults={'cantidad': item_anonimo.cantidad}
        )
        
        if not item_created:
            # Si ya existía, sumar la cantidad
            item_existente.cantidad += item_anonimo.cantidad
            item_existente.save()
            
    # Eliminar el carrito anónimo una vez fusionado
    carrito_anonimo.delete()
