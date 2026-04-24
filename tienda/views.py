from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce



from django.contrib import messages
from .models import Proveedor, Producto, Categoria, PerfilCliente, Carrito, CarritoItem, Inventario, Orden, OrdenItem, Movimiento
from .forms import ProveedorForm, OrdenForm, PerfilForm, RegistroForm


def inicio(request):
    return render(request, "tienda/inicio.html")

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'¡Cuenta creada para {user.username}! Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'tienda/registro.html', {'form': form})



# LISTAR proveedores
@login_required
def proveedor_listar(request):
    proveedores = Proveedor.objects.all()
    return render(request, "tienda/proveedores/listar.html", {
        "proveedores": proveedores
    })


# CREAR proveedor
@login_required
def proveedor_crear(request):
    form = ProveedorForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("proveedor_listar")

    return render(request, "tienda/proveedores/form.html", {
        "form": form,
        "titulo": "Registrar Proveedor"
    })


# EDITAR proveedor
@login_required
def proveedor_editar(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    form = ProveedorForm(request.POST or None, instance=proveedor)

    if form.is_valid():
        form.save()
        return redirect("proveedor_listar")

    return render(request, "tienda/proveedores/form.html", {
        "form": form,
        "titulo": "Editar Proveedor"
    })


# ELIMINAR proveedor
@login_required
def proveedor_eliminar(request, id): 
    proveedor = get_object_or_404(Proveedor, id=id)

    if request.method == "POST":
        proveedor.delete()
        return redirect("proveedor_listar")

    return render(request, "tienda/proveedores/eliminar.html", {
        "proveedor": proveedor
    })

# PAGINA DE ABOUT 
def about(request):
    return render(request, "tienda/about.html")

def catalogo_publico(request):
    # Obtén productos activos con prefetch para optimizar
    productos = Producto.objects.filter(activo=True).prefetch_related('inventarios')
    
    # Filtro por categoría
    categoria = request.GET.get('categoria')
    if categoria:
        productos = productos.filter(categoria__id=categoria)
    
    # Búsqueda
    query = request.GET.get('q', '').strip()
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__nombre__icontains=query)
        )
    
    # Filtro por precio
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    
    if precio_min:
        try:
            productos = productos.filter(precio__gte=float(precio_min))
        except ValueError:
            pass
    
    if precio_max:
        try:
            productos = productos.filter(precio__lte=float(precio_max))
        except ValueError:
            pass
    
    # Filtro por stock (aplicar después de obtener todos)
    solo_con_stock = request.GET.get('con_stock')
    if solo_con_stock:
        # Filtra productos con stock > 0
        productos_con_stock_ids = [
            p.id for p in productos 
            if p.stock > 0  # Usa la propiedad que acabamos de crear
        ]
        productos = productos.filter(id__in=productos_con_stock_ids)
    
    # Ordenamiento
    ordenar = request.GET.get('ordenar', 'nombre-asc')
    orden_map = {
        'nombre-asc': 'nombre',
        'nombre-desc': '-nombre',
        'precio-asc': 'precio',
        'precio-desc': '-precio',
        'reciente': '-id',
    }
    
    # Para ordenar por stock, necesitamos ordenar manualmente
    if ordenar in ['stock-asc', 'stock-desc']:
        # Convertir a lista para ordenar
        productos_lista = list(productos)
        
        if ordenar == 'stock-asc':
            productos_lista.sort(key=lambda x: x.stock)
        else:  # stock-desc
            productos_lista.sort(key=lambda x: x.stock, reverse=True)
        
        productos = productos_lista  # Ahora es una lista
    else:
        productos = productos.order_by(orden_map.get(ordenar, 'nombre'))
    
    # Categorías coherentes
    categorias = Categoria.objects.filter(
        productos__in=productos
    ).distinct()
    
    # Pre-calcular selección para evitar errores de sintaxis en plantillas
    sort_selected = {
        'nombre_asc': 'selected' if ordenar == 'nombre-asc' else '',
        'nombre_desc': 'selected' if ordenar == 'nombre-desc' else '',
        'precio_asc': 'selected' if ordenar == 'precio-asc' else '',
        'precio_desc': 'selected' if ordenar == 'precio-desc' else '',
        'reciente': 'selected' if ordenar == 'reciente' else '',
    }
    
    return render(request, 'tienda/catalogo.html', {
        'productos': productos,
        'categorias': categorias,
        'con_stock': solo_con_stock,
        'sort_selected': sort_selected
    })

def proveedores_publico(request):
    """Vista PÚBLICA de proveedores (para clientes)"""
    proveedores = Proveedor.objects.filter(activo=True).order_by('nombre')
    
    return render(request, "tienda/proveedores/publico.html", {
        'proveedores': proveedores,
        'titulo': 'Nuestros Proveedores'
    })

def producto_detalle(request, slug):
    producto = get_object_or_404(Producto, slug=slug, activo=True)
    variantes = producto.inventarios.filter(stock__gt=0)
    return render(request, 'tienda/producto_detalle.html', {
        'producto': producto,
        'variantes': variantes
    })

def producto_detalle_por_id(request, id):
    producto = get_object_or_404(Producto, id=id, activo=True)
    if producto.slug:
        return redirect('producto_detalle', slug=producto.slug)
    variantes = producto.inventarios.filter(stock__gt=0)
    return render(request, 'tienda/producto_detalle.html', {
        'producto': producto,
        'variantes': variantes
    })

# --- CARRITO VIEWS ---

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Carrito.objects.get_or_create(usuario=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Carrito.objects.get_or_create(session_key=request.session.session_key)
    return cart

def carrito_ver(request):
    carrito = get_or_create_cart(request)
    return render(request, 'tienda/carrito.html', {
        'carrito': carrito
    })

def carrito_agregar(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = get_or_create_cart(request)
    
    variante_id = request.POST.get('variante')
    variante = None
    if variante_id:
        variante = get_object_or_404(Inventario, id=variante_id)
    
    cantidad = int(request.POST.get('cantidad', 1))
    
    item, created = CarritoItem.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        variante=variante,
        defaults={'cantidad': cantidad}
    )
    
    if not created:
        item.cantidad += cantidad
        item.save()
    
    # Redirigir a la página anterior o al catálogo
    return redirect(request.META.get('HTTP_REFERER', 'catalogo'))

def carrito_actualizar(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(CarritoItem, id=item_id)
        accion = request.POST.get('accion')
        
        if accion == 'incrementar':
            item.cantidad += 1
            item.save()
        elif accion == 'decrementar':
            if item.cantidad > 1:
                item.cantidad -= 1
                item.save()
            else:
                item.delete()
        elif accion == 'eliminar':
            item.delete()
            
    return redirect('carrito_ver')

def carrito_eliminar(request, item_id):
    item = get_object_or_404(CarritoItem, id=item_id)
    item.delete()
    return redirect('carrito_ver')

# --- CHECKOUT & PAYMENT VIEWS ---

@login_required
def checkout_view(request):
    carrito = get_or_create_cart(request)
    if not carrito.items.exists():
        return redirect('catalogo')
    
    form = OrdenForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        orden = form.save(commit=False)
        orden.usuario = request.user
        orden.total = carrito.total
        orden.save()
        
        # Transferir items del carrito a la orden
        for item in carrito.items.all():
            OrdenItem.objects.create(
                orden=orden,
                producto=item.producto,
                variante=item.variante,
                precio=item.producto.precio_final,
                cantidad=item.cantidad
            )
        
        return redirect('pago_simulado', orden_id=orden.id)
    
    return render(request, 'tienda/checkout.html', {
        'carrito': carrito,
        'form': form
    })

@login_required
def pago_simulado(request, orden_id):
    # Asegurar que la orden pertenece al usuario autenticado
    orden = get_object_or_404(Orden, id=orden_id, usuario=request.user)
    
    if request.method == 'POST':
        # Simulación de pago exitoso
        orden.pagado = True
        orden.estado = 'PAGADO'
        orden.save()
        
        # ACTUALIZACIÓN DE INVENTARIO EN TIEMPO REAL
        for item in orden.items.all():
            if item.variante:
                # Crear movimiento de salida para la variante específica
                Movimiento.objects.create(
                    inventario=item.variante,
                    tipo='SALIDA',
                    cantidad=item.cantidad,
                    observacion=f"Venta Online - Orden #{orden.id}"
                )
        
        # Vaciar el carrito tras el pago
        carrito = get_or_create_cart(request)
        carrito.items.all().delete()
        
        return redirect('pedido_confirmado', orden_id=orden.id)
        
    return render(request, 'tienda/pago_simulado.html', {
        'orden': orden
    })

@login_required
def pedido_confirmado(request, orden_id):
    # Asegurar que la orden pertenece al usuario autenticado
    orden = get_object_or_404(Orden, id=orden_id, usuario=request.user)
    return render(request, 'tienda/pedido_confirmado.html', {
        'orden': orden
    })

@login_required
def perfil_view(request):
    # Obtener o crear perfil si no existe
    perfil, created = PerfilCliente.objects.get_or_create(usuario=request.user)
    
    # Manejar actualización de perfil
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado con éxito!')
            return redirect('perfil')
    else:
        form = PerfilForm(instance=perfil)
        
    # Obtener historial de órdenes
    ordenes = Orden.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    
    return render(request, 'tienda/perfil.html', {
        'perfil': perfil,
        'ordenes': ordenes,
        'form': form
    })
