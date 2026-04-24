# tienda/admin_dashboard.py
from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import reverse
from .models import *

class DashboardAdmin(admin.ModelAdmin):
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
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
            **self.admin_site.each_context(request),
        }
        
        return TemplateResponse(request, "admin/dashboard.html", context)

# En tu admin.py principal, solo importa y registra
# from .admin_dashboard import DashboardAdmin
# admin.site.register(DashboardAdmin)