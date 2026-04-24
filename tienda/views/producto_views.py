from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test

from tienda.models import Producto
from tienda.forms.producto_forms import ProductoForm


#  Solo administradores
def es_admin(user):
    return user.is_staff


@login_required
@user_passes_test(es_admin)
def producto_listar(request):
    productos = Producto.objects.all().order_by('-id')
    return render(request, 'panel/productos/listar.html', {
        'productos': productos
    })


@login_required
@user_passes_test(es_admin)
def producto_crear(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('producto_listar')
    else:
        form = ProductoForm()

    return render(request, 'panel/productos/crear.html', {
        'form': form
    })


@login_required
@user_passes_test(es_admin)
def producto_editar(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('producto_listar')
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'panel/productos/editar.html', {
        'form': form,
        'producto': producto
    })


# from django import forms
# from .models import Proveedor 

# class ProveedorForm(forms.ModelForm):
#     class Meta:
#         model = Proveedor
#         fields = ["nombre", "telefono", "email", "direccion"]

