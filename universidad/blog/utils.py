# myapp/utils.py

import re

from googletrans import Translator  #
def extraer_id_youtube(url):
    # Buscar el ID del video en ambos formatos
    match = re.search(r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:embed\/|v\/|watch\?v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})', url)
    return match.group(1) if match else None


def traducir_texto(texto, idioma='es'):
    translator = Translator()
    try:
        traduccion = translator.translate(texto, dest=idioma)
        return traduccion.text
    except Exception as e:
        print(f'Error en la traducción: {e}')
        return texto
