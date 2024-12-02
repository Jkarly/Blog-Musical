from django import forms
from django.contrib.auth.models import User
from .models import PerfilUsuario, Cancion, Comentario,Publicacion
from django.core.exceptions import ValidationError
import re
from datetime import datetime
class LoginForm(forms.Form):
    usuario = forms.CharField()  # Este campo es personalizado
    contraseña = forms.CharField(widget=forms.PasswordInput)

class UserRegistrationForm(forms.ModelForm):
    contrasena = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    confirmar_contrasena = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('El nombre de usuario ya está en uso. Por favor, elige otro.')
        return username
    def clean_contrasena(self):
        contrasena = self.cleaned_data.get('contrasena')
        
        # Validaciones
        if len(contrasena) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        if not any(char.isdigit() for char in contrasena):
            raise ValidationError('La contraseña debe contener al menos un número.')
        if not any(char.isalpha() for char in contrasena):
            raise ValidationError('La contraseña debe contener al menos una letra.')

        return contrasena

    def clean(self):
        cleaned_data = super().clean()
        contrasena = cleaned_data.get('contrasena')
        confirmar_contrasena = cleaned_data.get('confirmar_contrasena')

        if contrasena and confirmar_contrasena:
            if contrasena != confirmar_contrasena:
                raise ValidationError('Las contraseñas no coinciden.')

        return cleaned_data

class EditarPerfilForm(forms.ModelForm):
   
    telefono = forms.CharField(label="Número de Teléfono")

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')

        # Verifica que el número de teléfono solo contenga números
        if not re.match(r'^\d+$', telefono):
            raise ValidationError('El número de teléfono solo debe contener números.')

        # Retorna el número completo con un espacio entre el código de país y el número de teléfono
        return f' {telefono}'

    class Meta:
        model = PerfilUsuario
        fields = [ 'telefono', 'fecha_nacimiento', 'foto_perfil']


class CancionForm(forms.ModelForm):
    class Meta:
        model = Cancion
        fields = ['titulo', 'artista', 'album', 'fecha_lanzamiento', 'genero', 'letras', 'imagen', 'categorias']



class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['comentario']  


class PublicacionForm(forms.ModelForm):
    class Meta:
        model = Publicacion
        fields = ['titulo', 'descripcion', 'imagen']

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        # Verifica si hay al menos una letra en la descripción
        if not re.search(r'[A-Za-z]', descripcion):
            raise ValidationError('La descripción debe contener al menos una letra.')
        return descripcion


class BuscadorCancionesForm(forms.Form):
    query = forms.CharField(
        label='Buscar canciones',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Buscar...'})
    )
    
    


class CancionForm(forms.ModelForm):
    class Meta:
        model = Cancion
        fields = ['titulo', 'artista', 'album', 'fecha_lanzamiento', 'genero', 'letras', 'imagen', 'link_spotify', 'categorias']
        widgets = {
            'fecha_lanzamiento': forms.SelectDateWidget(years=range(1900, datetime.now().year + 1)),
            'genero': forms.CheckboxSelectMultiple(),
            'categorias': forms.CheckboxSelectMultiple(),
        }    