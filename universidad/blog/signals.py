from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from .models import Cancion, Genero,Album

@receiver(m2m_changed, sender=Cancion.genero.through)
def actualizar_cantidad_canciones_m2m(sender, instance, action, **kwargs):
    if action in ['post_add', 'post_remove']:
        print(f"Se ha modificado la relación de géneros para la canción: {instance.titulo}")
        # Actualiza la cantidad de canciones para todos los géneros afectados
        for gen in Genero.objects.all():
            gen.cantidad_canciones = gen.canciones.count()
            gen.save()

@receiver(post_save, sender=Cancion)
def actualizar_cantidad_canciones(sender, instance, **kwargs):
    if kwargs.get('created', False):
        print(f"Se ha creado la canción: {instance.titulo}")
    else:
        print(f"Se ha actualizado la canción: {instance.titulo}")

    # Actualiza la cantidad de canciones para todos los géneros
    for gen in Genero.objects.all():
        gen.cantidad_canciones = gen.canciones.count()
        gen.save()


@receiver(post_delete, sender=Cancion)
def actualizar_cantidad_canciones_al_eliminar(sender, instance, **kwargs):
    print(f"Se ha eliminado la canción: {instance.titulo}")

    # Actualiza la cantidad de canciones para todos los géneros
    for gen in Genero.objects.all():
        gen.cantidad_canciones = gen.canciones.count()
        gen.save()



@receiver(post_save, sender=Cancion)
def actualizar_cantidad_canciones(sender, instance, **kwargs):
    # Asegúrate de que la instancia de Cancion tenga una relación con un álbum
    if instance.album:
        album = instance.album
        # Contar el número de canciones en el álbum
        cantidad = album.canciones.count()
        album.cantidad_canciones = cantidad
        album.save()
        print(f"Se ha guardado la canción '{instance.titulo}' en el álbum '{album.titulo}'. Total canciones: {cantidad}")

@receiver(post_delete, sender=Cancion)
def actualizar_cantidad_canciones_al_eliminar(sender, instance, **kwargs):
    # Asegúrate de que la instancia de Cancion tenga una relación con un álbum
    if instance.album:
        album = instance.album
        # Contar el número de canciones en el álbum después de la eliminación
        cantidad = album.canciones.count()
        album.cantidad_canciones = cantidad
        album.save()
        print(f"Se ha eliminado la canción '{instance.titulo}' del álbum '{album.titulo}'. Total canciones: {cantidad}")

