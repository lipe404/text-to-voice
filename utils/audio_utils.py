import io
import base64
from gtts import gTTS
import streamlit as st
import time


def text_to_speech(text, language='pt', slow=False):
    """
    Converte texto em áudio usando gTTS

    Args:
        text (str): Texto para converter
        language (str): Código do idioma
        slow (bool): Velocidade lenta

    Returns:
        bytes: Dados do áudio em formato MP3
    """
    try:
        # Criar objeto gTTS
        tts = gTTS(text=text, lang=language, slow=slow)

        # Salvar em buffer de memória
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        return audio_buffer.getvalue()

    except Exception as e:
        st.error(f"Erro ao gerar áudio: {str(e)}")
        return None


def split_text(text, max_length=500):
    """
    Divide texto longo em chunks menores

    Args:
        text (str): Texto para dividir
        max_length (int): Tamanho máximo de cada chunk

    Returns:
        list: Lista de chunks de texto
    """
    # Dividir por sentenças primeiro
    sentences = text.replace('!', '.').replace('?', '.').split('.')
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # Se adicionar a sentença não exceder o limite
        if len(current_chunk + sentence) <= max_length:
            current_chunk += sentence + ". "
        else:
            # Salvar chunk atual e começar novo
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "

    # Adicionar último chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def process_long_text(text, language='pt', slow=False, max_length=500):
    """
    Processa texto longo dividindo em chunks e gerando áudios separados

    Args:
        text (str): Texto completo
        language (str): Código do idioma
        slow (bool): Velocidade lenta
        max_length (int): Tamanho máximo de cada chunk

    Returns:
        list: Lista de dados de áudio em bytes
    """
    chunks = split_text(text, max_length)
    audio_chunks = []

    for i, chunk in enumerate(chunks):
        # Pequena pausa para evitar rate limiting do gTTS
        if i > 0:
            time.sleep(0.5)

        audio_data = text_to_speech(chunk, language, slow)
        if audio_data:
            audio_chunks.append(audio_data)
        else:
            st.error(f"Erro ao processar chunk {i+1}")
            return None

    return audio_chunks


def get_download_link(audio_data, filename="audio.mp3"):
    """
    Gera link de download para o áudio

    Args:
        audio_data (bytes): Dados do áudio
        filename (str): Nome do arquivo

    Returns:
        str: HTML do link de download
    """
    b64 = base64.b64encode(audio_data).decode()
    href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}" style="text-decoration: none; background-color: #4CAF50; color: white; padding: 10px 20px; border-radius: 5px; display: inline-block; margin: 5px;">Baixar Áudio MP3</a>'
    return href


def get_multiple_download_links(audio_chunks):
    """
    Gera links de download para múltiplos chunks de áudio

    Args:
        audio_chunks (list): Lista de dados de áudio em bytes

    Returns:
        str: HTML com múltiplos links de download
    """
    links_html = ""
    for i, audio_data in enumerate(audio_chunks):
        filename = f"audio_parte_{i+1:02d}.mp3"
        b64 = base64.b64encode(audio_data).decode()
        link = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}" style="text-decoration: none; background-color: #2196F3; color: white; padding: 8px 16px; border-radius: 5px; display: inline-block; margin: 3px;">📥 Parte {i+1}</a>'
        links_html += link + " "

    return links_html
