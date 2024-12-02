from django.contrib import admin
from .models import Cancion, Categoria, Imagen, Video, Album, Genero ,Publicacion,MensajeContacto,IntentoInicioSesion
from .models import Artista
from .models import MensajeContacto
@admin.register(Artista)
class ArtistaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'imagen_thumbnail')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('nombre',)

    def imagen_thumbnail(self, obj):
        if obj.imagen:
            return '<img src="%s" width="100" height="100" />' % obj.imagen.url
        return 'No image'
    
    imagen_thumbnail.allow_tags = True
    imagen_thumbnail.short_description = 'Imagen'

@admin.register(Cancion)
class CancionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'artista', 'album', 'fecha_lanzamiento', 'link_spotify')
    search_fields = ('titulo', 'artista__nombre', 'album__titulo')
    filter_horizontal = ('categorias', 'genero')



@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')

@admin.register(Imagen)
class ImagenAdmin(admin.ModelAdmin):
    list_display = ('cancion', 'descripcion', 'mas_informacion', 'link')
    search_fields = ('cancion__titulo', 'descripcion', 'link')
    list_filter = ('cancion',)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('cancion', 'enlace_video')
    search_fields = ('cancion__titulo', 'enlace_video')
    list_filter = ('cancion',)
    
    
@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'imagen')  # Agrega el nombre y la imagen a la lista
    search_fields = ('nombre',)  # Coloca los campos de búsqueda en una tupla
    list_filter = ('nombre',)
    
    # Especificar los campos que serán editables
    fields = ('nombre', 'imagen')

#  Álbum
@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'artista', 'fecha_lanzamiento', 'genero','imagen')
    search_fields = ('titulo', 'artista__nombre', 'genero__nombre')
    list_filter = ('artista', 'genero')
    fields = ('titulo', 'artista', 'fecha_lanzamiento', 'genero','imagen')

@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_creacion', 'usuario', 'imagen_thumbnail')
    search_fields = ('titulo', 'descripcion', 'usuario__username')
    list_filter = ('fecha_creacion', 'usuario')

    def imagen_thumbnail(self, obj):
        if obj.imagen:
            return '<img src="%s" width="100" height="100" />' % obj.imagen.url
        return 'No image'
    
    imagen_thumbnail.allow_tags = True
    imagen_thumbnail.short_description = 'Imagen'
    


@admin.register(MensajeContacto)
class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ('correo_electronico', 'asunto', 'fecha_creacion')
    search_fields = ('correo_electronico', 'asunto', 'mensaje')


@admin.register(IntentoInicioSesion)
class IntentoInicioSesionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'exitoso', 'fecha_intento')  # Campos que se mostrarán en la lista
    search_fields = ('usuario__username', 'exitoso')  # Campos que se pueden buscar
    list_filter = ('exitoso', 'fecha_intento')  # Filtros disponibles en el panel de administración    