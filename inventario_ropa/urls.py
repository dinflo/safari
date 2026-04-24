from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from tienda.admin import dashboard_view

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Dashboard del admin
    path('admin/dashboard/', admin.site.admin_view(dashboard_view), name='admin_dashboard'),
    # Admin normal
    path('admin/', admin.site.urls),
    path("", include("tienda.urls")),

    # URLs de autenticación
    path('accounts/login/', auth_views.LoginView.as_view(template_name='tienda/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='inicio'), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)