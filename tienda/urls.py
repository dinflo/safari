from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("about/", views.about, name="about"),
    path("proveedores/nuevo/", views.proveedor_crear, name="proveedor_crear"),
    path("proveedores/editar/<int:id>/", views.proveedor_editar, name="proveedor_editar"),
    path("proveedores/eliminar/<int:id>/", views.proveedor_eliminar, name="proveedor_eliminar"),
    path('catalogo/', views.catalogo_publico, name='catalogo'),
    path('producto/<slug:slug>/', views.producto_detalle, name='producto_detalle'),
    path('producto/id/<int:id>/', views.producto_detalle_por_id, name='producto_detalle_por_id'),

    # Carrito
    path('carrito/', views.carrito_ver, name='carrito_ver'),
    path('carrito/agregar/<int:producto_id>/', views.carrito_agregar, name='carrito_agregar'),
    path('carrito/actualizar/<int:item_id>/', views.carrito_actualizar, name='carrito_actualizar'),
    path('carrito/eliminar/<int:item_id>/', views.carrito_eliminar, name='carrito_eliminar'),

    # PROVEEDORES - VISTA PÚBLICA (para clientes)
    path('proveedores/', views.proveedores_publico, name='proveedores_publico'),
    # Autenticación
    path('accounts/login/', auth_views.LoginView.as_view(template_name='tienda/login.html'), name='login'),
    path('accounts/registro/', views.registro, name='registro'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='inicio'), name='logout'),
    # Checkout y Pago
    path('checkout/', views.checkout_view, name='checkout'),
    path('pago/simulado/<int:orden_id>/', views.pago_simulado, name='pago_simulado'),
    path('pedido/confirmado/<int:orden_id>/', views.pedido_confirmado, name='pedido_confirmado'),
    path('perfil/', views.perfil_view, name='perfil'),
]
