from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from ..models import PerfilCliente

class RegistroForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label='Nombre')
    last_name = forms.CharField(max_length=30, label='Apellido')
    email = forms.EmailField(label='Email')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class PerfilForm(forms.ModelForm):

    class Meta:
        model = PerfilCliente
        fields = ['telefono', 'direccion', 'ciudad']
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +51 999 999 999'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu dirección completa'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Lima'}),
        }
