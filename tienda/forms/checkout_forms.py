from django import forms
from ..models import Orden

class OrdenForm(forms.ModelForm):
    class Meta:
        model = Orden
        fields = ['nombre_completo', 'email', 'telefono', 'direccion', 'ciudad']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre Completo'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'correo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '999 999 999'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Dirección completa',
                'rows': 3
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ciudad'
            }),
        }
