from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import login, login_blocked
urlpatterns = [
    # Authentication
   
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('login/', login, name='login'),
    path('login-blocked/', login_blocked, name='login_blocked'),
    path('contacto/', views.vista_contacto, name='contacto'), 
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
  
    
    # Main application views
    path('', views.inicio, name='inicio'),
    path('register/', views.registrar_usuario, name='register'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
   
    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('agregar-cancion/', views.agregar_cancion, name='agregar_cancion'),
    path('cancion/<int:id>/<str:track_id>/', views.detalle_cancion, name='detalle_cancion'),
    path('cancion/<int:cancion_id>/agregar_comentario/', views.agregar_comentario, name='agregar_comentario'),
    path('favoritos/', views.lista_favoritos, name='lista_favoritos'),
    path('cancion/<int:cancion_id>/favoritos/agregar/', views.agregar_a_favoritos, name='agregar_a_favoritos'),
    path('cancion/<int:cancion_id>/favoritos/eliminar/', views.eliminar_de_favoritos, name='eliminar_de_favoritos'),
    path('artista/<int:id>/', views.detalle_artista, name='detalle_artista'),

    path('publicaciones/', views.lista_publicaciones, name='lista_publicaciones'),
    path('publicaciones/crear/', views.crear_publicacion, name='crear_publicacion'),
    path('editar_publicacion/<int:id>/', views.editar_publicacion, name='editar_publicacion'),
    path('guardar-publicacion/<int:pk>/', views.guardar_publicacion, name='guardar_publicacion'),
    path('publicaciones-guardadas/', views.publicaciones_guardadas, name='publicaciones_guardadas'),
    path('publicacion/eliminar/<int:id>/', views.eliminar_publicacion, name='eliminar_publicacion'),
   
    
    path('genero/<int:genero_id>/', views.canciones_por_genero, name='canciones_por_genero'),
    path('album/<int:album_id>/', views.album_detail, name='album_detail'),
    path('artista/', views.lista_artistas, name='lista_artistas'),
    path('comentario/<int:comentario_id>/editar/', views.editar_comentario, name='editar_comentario'),
    path('comentario/<int:comentario_id>/eliminar/', views.eliminar_comentario, name='eliminar_comentario'),
    path('acceso-denegado/', views.acceso_denegado, name='acceso_denegado')
]



