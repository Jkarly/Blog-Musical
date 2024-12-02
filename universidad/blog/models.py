from django.db import models
from django.contrib.auth.models import User  # Import Django's user model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import datetime
from django.utils.translation import gettext_lazy as _


   

# Signal to create or update user profile automatically
@receiver(post_save, sender=User)
def crear_o_actualizar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(user=instance, fecha_nacimiento=datetime.now())
    else:
        perfil, _ = PerfilUsuario.objects.get_or_create(user=instance)
        if perfil.fecha_nacimiento is None:
            perfil.fecha_nacimiento = datetime.now()
            perfil.save()

# Usuario Perfil
class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fecha_nacimiento = models.DateField(default=datetime.now)
    telefono = models.CharField(max_length=15, blank=True, null=True) 
    foto_perfil = models.ImageField(upload_to='images/', null=True)
    
    def __str__(self):
        return f'{self.user.username} ({self.user.email})'

# Category
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.nombre




class Artista(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='images/')
    descripcion = models.TextField()
    link_tiktok = models.URLField(blank=True, null=True)
    link_facebook = models.URLField(blank=True, null=True)
    link_twitter = models.URLField(blank=True, null=True)
    link_instagram = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nombre



class Genero(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    imagen = models.ImageField(upload_to='images/', null=True, blank=True)
    cantidad_canciones = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nombre

# Álbum
class Album(models.Model):
    titulo = models.CharField(max_length=200)
    artista = models.ForeignKey('Artista', on_delete=models.CASCADE, related_name='albumes')
    fecha_lanzamiento = models.DateField()
    genero = models.ForeignKey('Genero', on_delete=models.SET_NULL, null=True, related_name='albumes')
    imagen = models.ImageField(upload_to='images/', blank=True, null=True)
    cantidad_canciones = models.PositiveIntegerField(default=0, editable=False)

    def __str__(self):
        return f"{self.titulo} - {self.artista.nombre}"
class Cancion(models.Model):
    titulo = models.CharField(max_length=200)
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE, related_name='canciones')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='canciones', blank=True, null=True)
    fecha_lanzamiento = models.DateField()
    genero = models.ManyToManyField(Genero, related_name='canciones', blank=True)
    letras = models.TextField(_('lyrics'))
    imagen = models.ImageField(upload_to='images/', blank=True, null=True)
    link_spotify = models.CharField(max_length=50, blank=True, null=True)
    categorias = models.ManyToManyField(Categoria, related_name='canciones', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo

    

#Comentarios
class Comentario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cancion = models.ForeignKey(Cancion, on_delete=models.CASCADE, related_name='comentarios')
    comentario = models.TextField()
    fecha_comentario = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario.username} - {self.cancion.titulo}: {self.comentario}'

# Imagen
class Imagen(models.Model):
    cancion = models.ForeignKey(Cancion, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='imagenes/')
    descripcion = models.CharField(max_length=255)
    mas_informacion = models.TextField(blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)  # Campo link agregado

    def __str__(self):
        return f"Imagen de {self.cancion.titulo} - {self.descripcion}"

    class Meta:
        verbose_name = 'Imagen'
        verbose_name_plural = 'Imagenes'


from embed_video.fields import EmbedVideoField

class Video(models.Model):
    cancion = models.ForeignKey(Cancion, on_delete=models.CASCADE, related_name='videos')
    enlace_video = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Video de {self.cancion.titulo}"

    class Meta:
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'


class Favorito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cancion = models.ForeignKey(Cancion, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usuario', 'cancion')
    
# Publicación
class Publicacion(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(null=False, default=' ')
    imagen = models.ImageField(upload_to='publicaciones/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='publicaciones')

    def __str__(self):
        return self.titulo
    
class PublicacionGuardada(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE)
    fecha_guardado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'publicacion')   
        

class IntentoInicioSesion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    exitoso = models.BooleanField()
    fecha_intento = models.DateTimeField(auto_now_add=True)

class MensajeContacto(models.Model):
    correo_electronico = models.EmailField(verbose_name='Correo Electrónico')
    asunto = models.CharField(max_length=255, verbose_name='Asunto')
    mensaje = models.TextField(verbose_name='Mensaje')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
           