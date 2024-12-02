from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import PerfilUsuario
from .forms import LoginForm
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q 
from .models import Cancion, Video, Imagen, Comentario, Favorito, Artista, Publicacion, PublicacionGuardada,Genero,Album, MensajeContacto
from .forms import ComentarioForm, CancionForm, UserRegistrationForm, EditarPerfilForm,PublicacionForm, BuscadorCancionesForm

from django.contrib import messages
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings
from django.http import HttpResponseForbidden
from urllib.parse import urlparse, parse_qs
from .utils import extraer_id_youtube
from django.utils.translation import gettext as _
from django.utils.translation import get_language
from googletrans import Translator
import re

from django.contrib.auth.models import User
from django.contrib import messages
from .decorators import group_required
from datetime import timedelta
from .models import IntentoInicioSesion  
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group
from django.utils import timezone


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['usuario']
            password = form.cleaned_data['contraseña']
            user = authenticate(request, username=username, password=password)

            if user:
                if not user.is_active:
                    messages.error(request, 'Cuenta bloqueada por intentos fallidos. Contacte con el soporte para desbloquearla.')
                    return redirect('login_blocked')  # Redirige a una página de cuenta bloqueada

                # Elimina los intentos fallidos del usuario si la cuenta está activa
                IntentoInicioSesion.objects.filter(usuario=user, exitoso=False).delete()
                
                auth_login(request, user)
                IntentoInicioSesion.objects.create(usuario=user, exitoso=True)
                return redirect('inicio')  
            else:
                usuario = User.objects.filter(username=username).first()
                if usuario:
                    IntentoInicioSesion.objects.create(usuario=usuario, exitoso=False)
                    # Calcula el número de intentos fallidos Dentro de la última hora
                    intentos_fallidos = IntentoInicioSesion.objects.filter(
                        usuario=usuario,
                        exitoso=False,
                        fecha_intento__gte=timezone.now() - timedelta(hours=1)  
                    ).count()

                    if intentos_fallidos >= 3:
                        usuario.is_active = False
                        usuario.save()
                        messages.error(request, 'Cuenta bloqueada por intentos fallidos. Contacte con el soporte para desbloquearla.')
                        return redirect('login_blocked') 
                
                messages.error(request, 'La información no es correcta.')
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})





from django.shortcuts import render

def login_blocked(request):
    return render(request, 'registration/login_blocked.html')


def inicio(request):
    form = BuscadorCancionesForm(request.GET or None)
    artistas = Artista.objects.all()
    canciones = Cancion.objects.all().select_related('artista')
    generos = Genero.objects.all()
    albums = Album.objects.all()
    favoritos = set(request.user.favorito_set.values_list('cancion_id', flat=True)) if request.user.is_authenticated else set()
    
    if form.is_valid():
        query = form.cleaned_data['query']
        if query:
            canciones = canciones.filter(
                Q(titulo__icontains=query) | 
                Q(artista__nombre__icontains=query)  
            )
            # Filtrar artistas por el término de búsqueda
            artistas = artistas.filter(
                Q(nombre__icontains=query)
            )
            albums = albums.filter(
                Q(titulo__icontains=query) | 
                Q(artista__nombre__icontains=query)  
            )
    
    # Agrupar artistas en grupos de 5
    artistas_grupos = [artistas[i:i + 5] for i in range(0, len(artistas), 5)]
    # Agrupar canciones en grupos de 4
    canciones_list = list(canciones) 
    canciones_grupos = [canciones_list[i:i + 4] for i in range(0, len(canciones_list), 4)]
    
    return render(request, 'iniciosesion/inicio.html', {
        'canciones_grupos': canciones_grupos,
        'artistas_grupos': artistas_grupos,
        'generos': generos,
        'albums': albums,
        'favoritos': favoritos,
        'form': form,
    })



def registrar_usuario(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['contrasena'])
            new_user.save()
            
            # Crear perfil de usuario
            if not PerfilUsuario.objects.filter(user=new_user).exists():
                PerfilUsuario.objects.create(user=new_user)
            # Asignar el usuario al grupo de 'regular_users'
            try:
                grupo = Group.objects.get(name='regular_users')
            except Group.DoesNotExist:
                grupo = Group.objects.create(name='regular_users')  
            
            new_user.groups.add(grupo)
            
            messages.success(request, '¡Usuario registrado exitosamente!')
            return redirect('login')  
    else:
        user_form = UserRegistrationForm()

    return render(request, 'iniciosesion/register.html', {'user_form': user_form})




@login_required
def perfil_view(request):
    perfil, created = PerfilUsuario.objects.get_or_create(user=request.user)
    
    if created:
        
        return redirect('editar_perfil') 
    
    return render(request, 'perfil/perfil.html', {'perfil': perfil})

@login_required
def editar_perfil(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('perfil')  
    else:
        form = EditarPerfilForm(instance=perfil)
    return render(request, 'perfil/editar_perfil.html', {'form': form})

def obtener_id_youtube(url):
    """ Extrae el ID de YouTube de una URL. """
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if 'v' in parse_qs(parsed_url.query):
            return parse_qs(parsed_url.query)['v'][0]
    return None







def es_id_spotify_valido(id):
    return len(id) == 22 and all(c in '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' for c in id)


@login_required
def detalle_cancion(request, id, track_id=None):
    cancion = get_object_or_404(Cancion, id=id)
    comentarios = cancion.comentarios.all()
    videos = Video.objects.filter(cancion=cancion)
    imagenes = Imagen.objects.filter(cancion=cancion)
    idioma_actual = get_language()
  
    # Agrupar imágenes de dos en dos
    imagenes_grupos = [imagenes[i:i + 2] for i in range(0, len(imagenes), 2)]

    # Traducción dinámica usando el idioma actual
    letras_traducidas = cancion.letras
    if idioma_actual == 'es':
        translator = Translator()
        try:
            letras_traducidas = translator.translate(cancion.letras, dest='es').text
        except Exception as e:
            print(f'Error en la traducción: {e}')
    
    # Procesar los ID de YouTube
    for video in videos:
        video.enlace_video = extraer_id_youtube(video.enlace_video)
        print(video.enlace_video)  # Verifica el ID del video

    if not track_id or not es_id_spotify_valido(track_id):
        messages.error(request, 'Track ID no disponible o inválido.')
        return redirect('inicio')  

    # Inicializar la instancia de Spotify
    sp = Spotify(auth_manager=SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope="user-library-read"
    ))

    # Obtenemos información de la pista
    try:
        track = sp.track(track_id)
    except Exception as e:
        messages.error(request, f'Error al obtener información del track: {e}')
        return redirect('inicio')

    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.usuario = request.user
            comentario.cancion = cancion
            comentario.save()
            return redirect('detalle_cancion', id=cancion.id, track_id=track_id)
    else:
        form = ComentarioForm()

    return render(request, 'canciones/detalle_cancion.html', {
        'cancion': cancion,
        'comentarios': comentarios,
        'videos': videos,
        'imagenes_grupos': imagenes_grupos,
        'letras_traducidas': letras_traducidas,
        'track': track,
        'track_id': track_id,
        'form': form,
    })



@login_required
def agregar_comentario(request, cancion_id):
    cancion = get_object_or_404(Cancion, id=cancion_id)
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            nuevo_comentario = form.save(commit=False)
            nuevo_comentario.usuario = request.user
            nuevo_comentario.cancion = cancion
            nuevo_comentario.save()
            messages.success(request, 'Comentario añadido con éxito.')
            return redirect('detalle_cancion', id=cancion.id)
        else:
            messages.error(request, 'Error al agregar el comentario.')
    else:
        form = ComentarioForm()
    
    return render(request, 'canciones/detalle_cancion.html', {'form': form, 'cancion': cancion})




@login_required
def agregar_a_favoritos(request, cancion_id):
    cancion = get_object_or_404(Cancion, id=cancion_id)
    favorito, created = Favorito.objects.get_or_create(usuario=request.user, cancion=cancion)
    
    if created:
        messages.success(request, f'{cancion.titulo} ha sido añadido a tus favoritos.')
    else:
        messages.info(request, f'{cancion.titulo} ya está en tus favoritos.')
    
    return redirect('inicio')  

@login_required
def eliminar_de_favoritos(request, cancion_id):
    cancion = get_object_or_404(Cancion, id=cancion_id)
    favorito = Favorito.objects.filter(usuario=request.user, cancion=cancion)
    
    if favorito.exists():
        favorito.delete()
        messages.success(request, f'{cancion.titulo} ha sido eliminado de tus favoritos.')
    else:
        messages.info(request, f'{cancion.titulo} no está en tus favoritos.')
    
    return redirect('inicio')  


@login_required
def lista_favoritos(request):
    favoritos = Favorito.objects.filter(usuario=request.user)
    return render(request, 'favoritos/lista_favoritos.html', {'favoritos': favoritos})


def lista_artistas(request):
    artistas = Artista.objects.all()
    return render(request, 'artista/lista_artistas.html', {'artistas': artistas})

def detalle_artista(request, id):
    artista = get_object_or_404(Artista, id=id)
    return render(request, 'artista/detalle_artista.html', {'artista': artista})


@login_required
def album_detail(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    canciones = album.canciones.all()  
    
    track_ids = canciones.values_list('link_spotify', flat=True) if canciones.exists() else []
    return render(request, 'album/album_detail.html', {
        'album': album,
        'canciones': canciones, 
        'track_ids': track_ids 
    })



@login_required
def canciones_por_genero(request, genero_id):
    genero = get_object_or_404(Genero, id=genero_id)
    canciones = Cancion.objects.filter(genero=genero)
    
    track_ids = canciones.values_list('link_spotify', flat=True) if canciones.exists() else []
    
    return render(request, 'canciones/canciones_genero.html', {
        'genero': genero,
        'canciones': canciones,
        'track_ids': track_ids  
    })

@login_required
def crear_publicacion(request):
    if request.method == 'POST':
        form = PublicacionForm(request.POST, request.FILES)
        if form.is_valid():
            publicacion = form.save(commit=False)
            publicacion.usuario = request.user
            publicacion.save()
            messages.success(request, '¡Publicación creada con éxito!')
            return redirect('lista_publicaciones')
        else:
            messages.error(request, 'Error al crear la publicación. Verifica los datos ingresados.')
    else:
        form = PublicacionForm()

    return render(request, 'publicaciones/crear_publicacion.html', {'form': form})



@login_required
def lista_publicaciones(request):
    publicaciones = Publicacion.objects.all()  
    usuario_guardadas = PublicacionGuardada.objects.filter(usuario=request.user).values_list('publicacion', flat=True)
    return render(request, 'publicaciones/lista_publicaciones.html', {
        'publicaciones': publicaciones,
        'usuario_guardadas': usuario_guardadas
    })


@login_required
def guardar_publicacion(request, pk):
    publicacion = get_object_or_404(Publicacion, id=pk)
    
    usuario_guardada = PublicacionGuardada.objects.filter(usuario=request.user, publicacion=publicacion).first()

    if usuario_guardada:
        usuario_guardada.delete()
        messages.success(request, "La publicación ha sido desguardada.")
    else:
        PublicacionGuardada.objects.create(usuario=request.user, publicacion=publicacion)
        messages.success(request, "La publicación ha sido guardada.")

    return redirect('lista_publicaciones')


@permission_required('blog.change_publicacion', raise_exception=True)
def editar_publicacion(request, id):
    publicacion = get_object_or_404(Publicacion, id=id)
    
    # Verifica si el usuario tiene permiso para cambiar la publicación
    if not request.user.has_perm('blog.change_publicacion'):
        return HttpResponseForbidden("No tienes permiso para editar esta publicación.")

    if request.method == 'POST':
        form = PublicacionForm(request.POST, request.FILES, instance=publicacion)
        if form.is_valid():
            form.save()
            return redirect('lista_publicaciones')
    else:
        form = PublicacionForm(instance=publicacion)
    
    return render(request, 'publicaciones/editar_publicacion.html', {'form': form, 'publicacion': publicacion})




@login_required
def publicaciones_guardadas(request):
    publicaciones = PublicacionGuardada.objects.filter(usuario=request.user)
    return render(request, 'publicaciones/publicaciones_guardadas.html', {'publicaciones': publicaciones})

@login_required
def editar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id)

    if comentario.usuario != request.user and not request.user.is_staff:
        messages.error(request, 'No tienes permiso para editar este comentario.')
        return redirect('detalle_cancion', id=comentario.cancion.id, track_id=comentario.cancion.link_spotify)

    if request.method == 'POST':
        form = ComentarioForm(request.POST, instance=comentario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comentario actualizado con éxito.')
            return redirect('detalle_cancion', id=comentario.cancion.id, track_id=comentario.cancion.link_spotify)
    else:
        form = ComentarioForm(instance=comentario)

    return render(request, 'comentario/editar_comentario.html', {'form': form, 'comentario': comentario})



@login_required
def eliminar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id)

    if comentario.usuario != request.user and not request.user.is_staff:
        messages.error(request, 'No tienes permiso para eliminar este comentario.')
        return redirect('detalle_cancion', id=comentario.cancion.id, track_id=comentario.cancion.link_spotify)

    if request.method == 'POST':
        cancion_id = comentario.cancion.id
        track_id = comentario.cancion.link_spotify  
        comentario.delete()
        messages.success(request, 'Comentario eliminado con éxito.')
        return redirect('detalle_cancion', id=cancion_id, track_id=track_id)

    return render(request, 'comentario/eliminar_comentario.html', {'comentario': comentario})



@login_required
def eliminar_publicacion(request, id):
    publicacion = get_object_or_404(Publicacion, id=id)
    
    if publicacion.usuario == request.user:
        publicacion.delete()
        messages.success(request, 'Publicación eliminada con éxito.')
    else:
        messages.error(request, 'No tienes permiso para eliminar esta publicación.')
    
    return redirect('lista_publicaciones')





def vista_contacto(request):
    if request.method == 'POST':
        correo_electronico = request.POST.get('correo_electronico')
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')

        # Validacion
        if correo_electronico and asunto and mensaje:
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(email_regex, correo_electronico):
                # Guardar el mensaje en la base de datos
                MensajeContacto.objects.create(
                    correo_electronico=correo_electronico,
                    asunto=asunto,
                    mensaje=mensaje
                )
                messages.success(request, 'Su mensaje ha sido recibido.')
                return redirect('login_blocked')  
            else:
                messages.error(request, 'El formato del correo electrónico no es válido.')
        else:
            messages.error(request, 'Todos los campos son obligatorios.')

    return render(request, 'contacto/contacto.html')




@group_required('blog_collaborators')
def agregar_cancion(request):
    if request.method == 'POST':
        form = CancionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('inicio')  
    else:
        form = CancionForm()
    return render(request, 'canciones/agregar_cancion.html', {'form': form})


def acceso_denegado(request):
    return render(request, 'canciones/acceso_denegado.html')
