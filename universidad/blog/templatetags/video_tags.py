# myapp/templatetags/video_tags.py
from django import template

register = template.Library()

@register.simple_tag
def embed_video(url):
    # Aquí puedes incluir la lógica para generar el HTML del video embebido
    return f'<iframe src="{url}" frameborder="0" allowfullscreen></iframe>'
