from django.contrib import admin
from django.db.models import Count, Sum
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.html import format_html
from django.urls import reverse
import json
from .models import *

# ModelAdmins (mantén los que ya tienes)
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    # Configuración básica para listar
    list_display = ['id', 'nombre', 'telefono', 'email', 'activo', 'logo_preview', 'productos_count']
    list_display_links = ['id', 'nombre']
    list_filter = ['activo']
    search_fields = ['nombre', 'email', 'telefono', 'direccion']
    list_per_page = 20
    ordering = ['nombre']
    
    # Campos editables directamente en la lista
    list_editable = ['activo']
    
    # Vista previa del logo
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 5px;" />',
                obj.logo.url
            )
        return format_html(
            '<div style="width: 40px; height: 40px; background: #f0f0f0; border-radius: 5px; display: flex; align-items: center; justify-content: center; font-size: 10px;">Sin logo</div>'
        )
    logo_preview.short_description = 'Logo'
    
    # Contador de productos
    def productos_count(self, obj):
        count = obj.productos.count()
        url = reverse('admin:tienda_producto_changelist') + f'?proveedor__id__exact={obj.id}'
        return format_html(
            '<a href="{}" style="background: #4CAF50; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px;">{} productos</a>',
            url, count
        )
    productos_count.short_description = 'Productos'
    
    # Configuración del formulario de edición/creación
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'telefono', 'email', 'direccion')
        }),
        ('Información Pública', {
            'fields': ('logo', 'descripcion', 'sitio_web'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('activo',),
            'classes': ('wide',)
        }),
    )
    
    # Acciones personalizadas
    actions = ['activar_proveedores', 'desactivar_proveedores']
    
    def activar_proveedores(self, request, queryset):
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} proveedor(es) activado(s).')
    activar_proveedores.short_description = '✅ Activar seleccionados'
    
    def desactivar_proveedores(self, request, queryset):
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} proveedor(es) desactivado(s).')
    desactivar_proveedores.short_description = '❌ Desactivar seleccionados'



@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'producto_count_display']
    list_display_links = ['id', 'nombre']
    search_fields = ['nombre']
    list_per_page = 20
    ordering = ['nombre']
    
    def producto_count_display(self, obj):
        count = obj.productos.count()
        url = reverse('admin:tienda_producto_changelist') + f'?categoria__id__exact={obj.id}'
        color = "#4CAF50" if count > 0 else "#9E9E9E"
        return format_html(
            '<a href="{}" style="color: {}; font-weight: bold;">{} productos</a>',
            url, color, count
        )
    producto_count_display.short_description = 'Total Productos'
    
    # Acciones personalizadas
    actions = ['duplicar_categorias']
    
    def duplicar_categorias(self, request, queryset):
        for categoria in queryset:
            Categoria.objects.create(
                nombre=f"{categoria.nombre} (copia)"
            )
        self.message_user(request, f'{queryset.count()} categoría(s) duplicada(s).')
    duplicar_categorias.short_description = 'Duplicar categorías'

@admin.register(Talla)
class TallaAdmin(admin.ModelAdmin):
    list_display = ['nombre']

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'muestra_color', 'inventarios_count', 'productos_count']
    list_display_links = ['id', 'nombre']
    search_fields = ['nombre']
    list_per_page = 20
    ordering = ['nombre']
    
    def muestra_color(self, obj):
        colores_map = {
            'rojo': '#FF0000', 'azul': '#0000FF', 'verde': '#00FF00',
            'amarillo': '#FFFF00', 'negro': '#000000', 'blanco': '#FFFFFF',
            'gris': '#808080', 'naranja': '#FFA500', 'rosa': '#FFC0CB',
            'morado': '#800080', 'marrón': '#A52A2A', 'beige': '#F5F5DC',
            'celeste': '#87CEEB', 'verde oscuro': '#006400', 'rojo oscuro': '#8B0000',
        }
        color_hex = colores_map.get(obj.nombre.lower(), '#CCCCCC')
        return format_html(
            '<div style="width: 30px; height: 30px; background-color: {}; border: 1px solid #ddd; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" title="{}"></div>',
            color_hex, obj.nombre
        )
    muestra_color.short_description = 'Muestra'
    
    def inventarios_count(self, obj):
        count = Inventario.objects.filter(color=obj).count()
        url = reverse('admin:tienda_inventario_changelist') + f'?color__id__exact={obj.id}'
        return format_html(
            '<a href="{}" style="background: #9C27B0; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px;">{} inventarios</a>',
            url, count
        )
    inventarios_count.short_description = 'Inventarios'
    
    def productos_count(self, obj):
        count = Producto.objects.filter(inventarios__color=obj).distinct().count()
        url = reverse('admin:tienda_producto_changelist') + f'?inventarios__color__id__exact={obj.id}'
        return format_html(
            '<a href="{}" style="background: #FF5722; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px;">{} productos</a>',
            url, count
        )
    productos_count.short_description = 'Productos'
    
    actions = ['crear_colores_comunes']
    
    def crear_colores_comunes(self, request, queryset):
        colores_comunes = ['Rojo', 'Azul', 'Verde', 'Negro', 'Blanco', 'Gris', 'Amarillo', 'Naranja', 'Rosa']
        creados = 0
        for color in colores_comunes:
            if not Color.objects.filter(nombre__iexact=color).exists():
                Color.objects.create(nombre=color)
                creados += 1
        self.message_user(request, f'{creados} colores comunes creados.')
    crear_colores_comunes.short_description = '🎨 Crear colores comunes'



@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'categoria', 'proveedor', 'estado_stock_display', 'imagen_preview']
    list_filter = ['categoria', 'proveedor', 'activo']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['imagen_preview']
    
    def estado_stock_display(self, obj):
        estado = obj.estado_stock
        if estado == "out":
            return format_html('<span style="color: red; font-weight: bold;">{}</span>', 'Agotado')
        elif estado == "last":
            return format_html('<span style="color: orange; font-weight: bold;">{}</span>', 'Stock Bajo')
        else:
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', 'Disponible')
    
    def imagen_preview(self, obj):
        try:
            if obj.imagen and obj.imagen.url:
                return format_html(
                    '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                    obj.imagen.url
                )
        except (ValueError, AttributeError):
            pass
        return "Sin imagen"
    
    imagen_preview.short_description = 'Vista Previa'

@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ['producto', 'talla', 'color', 'stock']
    list_filter = ['producto__categoria', 'talla', 'color']
    search_fields = ['producto__nombre']

@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ['inventario', 'tipo', 'cantidad', 'fecha', 'observacion']
    list_filter = ['tipo', 'fecha']
    readonly_fields = ['fecha']
    date_hierarchy = 'fecha'

# FUNCIÓN PARA EL DASHBOARD
def dashboard_view(request):
    # Estadísticas generales
    total_productos = Producto.objects.count()
    total_proveedores = Proveedor.objects.count()
    
    # Productos con stock bajo
    productos_bajo_stock = []
    for producto in Producto.objects.all():
        stock_total = sum(inv.stock for inv in producto.inventarios.all())
        if 0 < stock_total <= 5:
            productos_bajo_stock.append({
                'nombre': producto.nombre,
                'stock': stock_total,
                'url': reverse('admin:tienda_producto_change', args=[producto.id])
            })
    
    # Productos agotados
    productos_agotados = []
    for producto in Producto.objects.all():
        stock_total = sum(inv.stock for inv in producto.inventarios.all())
        if stock_total == 0:
            productos_agotados.append({
                'nombre': producto.nombre,
                'url': reverse('admin:tienda_producto_change', args=[producto.id])
            })
    
    # Últimos movimientos
    movimientos_recientes = Movimiento.objects.select_related(
        'inventario__producto'
    ).order_by('-fecha')[:10]
    
    # Productos por categoría
    productos_por_categoria = {}
    for categoria in Categoria.objects.all():
        productos_por_categoria[categoria.nombre] = categoria.productos.count()
    
    # Stock total por categoría
    stock_por_categoria = {}
    for categoria in Categoria.objects.all():
        total_stock = 0
        for producto in categoria.productos.all():
            for inventario in producto.inventarios.all():
                total_stock += inventario.stock
        stock_por_categoria[categoria.nombre] = total_stock
    
    context = {
        'total_productos': total_productos,
        'total_proveedores': total_proveedores,
        'stock_bajo': len(productos_bajo_stock),
        'productos_bajo_stock': productos_bajo_stock[:5],
        'productos_agotados': productos_agotados[:5],
        'movimientos_recientes': movimientos_recientes,
        'productos_por_categoria': productos_por_categoria,
        'stock_por_categoria': stock_por_categoria,
        'title': 'Dashboard de Inventario',
        **admin.site.each_context(request),  # Esto es importante para el contexto del admin
    }
    
    return TemplateResponse(request, "admin/dashboard.html", context)

# SOLUCIÓN ALTERNATIVA MÁS SIMPLE: Usar un AdminSite personalizado
# O simplemente agregar la URL manualmente