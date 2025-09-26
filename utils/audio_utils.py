import io
import base64
from gtts import gTTS
import streamlit as st
import time
import re


def text_to_speech(text, language='pt', slow=False, speed_option='normal'):
    """
    Converte texto em áudio usando gTTS com controle de velocidade

    Args:
        text (str): Texto para converter
        language (str): Código do idioma
        slow (bool): Velocidade lenta (gTTS)
        speed_option (str): Opção de velocidade personalizada

    Returns:
        bytes: Dados do áudio em formato MP3
    """
    try:
        # Ajustar texto baseado na velocidade
        processed_text = process_text_for_speed(text, speed_option)

        # Criar objeto gTTS
        tts = gTTS(text=processed_text, lang=language, slow=slow)

        # Salvar em buffer de memória
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        return audio_buffer.getvalue()

    except Exception as e:
        st.error(f"Erro ao gerar áudio: {str(e)}")
        return None


def process_text_for_speed(text, speed_option):
    """
    Processa o texto para simular diferentes velocidades

    Args:
        text (str): Texto original
        speed_option (str): Opção de velocidade

    Returns:
        str: Texto processado
    """
    if speed_option == 'muito_lenta':
        # Adiciona pausas extras entre palavras
        return re.sub(r'\s+', ' ... ', text)
    elif speed_option == 'lenta':
        # Adiciona pausas menores
        return re.sub(r'\s+', ' .. ', text)
    elif speed_option == 'rapida':
        # Remove pausas desnecessárias e vírgulas extras
        text = re.sub(r'\s*,\s*', ', ', text)
        text = re.sub(r'\s*\.\s*', '. ', text)
        return text
    else:  # normal
        return text


def split_text(text, max_length=500):
    """
    Divide texto longo em chunks menores de forma inteligente

    Args:
        text (str): Texto para dividir
        max_length (int): Tamanho máximo de cada chunk

    Returns:
        list: Lista de chunks de texto
    """
    # Limpar e normalizar o texto
    text = text.strip()
    if not text:
        return []

    # Dividir por parágrafos primeiro
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        # Se o parágrafo inteiro cabe no chunk atual
        if len(current_chunk + paragraph) <= max_length:
            current_chunk += paragraph + "\n\n"
        else:
            # Salvar chunk atual se não estiver vazio
            if current_chunk.strip():
                chunks.append(current_chunk.strip())

            # Se o parágrafo é muito longo, dividir por sentenças
            if len(paragraph) > max_length:
                sentence_chunks = split_by_sentences(paragraph, max_length)
                chunks.extend(sentence_chunks)
                current_chunk = ""
            else:
                current_chunk = paragraph + "\n\n"

    # Adicionar último chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def split_by_sentences(text, max_length):
    """
    Divide texto por sentenças
    """
    # Dividir por sentenças
    sentences = re.split(r'[.!?]+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # Adicionar pontuação de volta
        sentence += "."

        if len(current_chunk + sentence) <= max_length:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def get_download_link(audio_data, filename="audio.mp3"):
    """
    Gera link de download estilizado para o áudio
    """
    b64 = base64.b64encode(audio_data).decode()
    href = f'''
    <a href="data:audio/mp3;base64,{b64}" download="{filename}"
       style="text-decoration: none; background: linear-gradient(45deg, #4CAF50, #45a049);
              color: white; padding: 12px 24px; border-radius: 8px;
              display: inline-block; margin: 5px; font-weight: bold;
              box-shadow: 0 4px 8px rgba(0,0,0,0.2); transition: all 0.3s;">
        Baixar Áudio MP3
    </a>
    '''
    return href


def get_multiple_download_links(audio_chunks):
    """
    Gera links de download para múltiplos chunks com design melhorado
    """
    links_html = "<div style='display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0;'>"

    for i, audio_data in enumerate(audio_chunks):
        filename = f"audio_parte_{i+1:02d}.mp3"
        b64 = base64.b64encode(audio_data).decode()
        link = f'''
        <a href="data:audio/mp3;base64,{b64}" download="{filename}"
           style="text-decoration: none; background: linear-gradient(45deg, #2196F3, #1976D2);
                  color: white; padding: 8px 16px; border-radius: 6px;
                  display: inline-block; font-size: 14px; font-weight: 500;
                  box-shadow: 0 2px 4px rgba(0,0,0,0.2); transition: all 0.3s;">
            Parte {i+1}
        </a>
        '''
        links_html += link

    links_html += "</div>"
    return links_html


def get_audio_info(audio_data):
    """
    Retorna informações sobre o áudio
    """
    size_kb = len(audio_data) / 1024
    size_mb = size_kb / 1024

    if size_mb >= 1:
        size_str = f"{size_mb:.2f} MB"
    else:
        size_str = f"{size_kb:.1f} KB"

    return {
        'size': size_str,
        'size_bytes': len(audio_data),
        'format': 'MP3'
    }


def estimate_duration(text, speed_option='normal'):
    """
    Estima a duração do áudio baseado no texto e velocidade
    """
    # Média de palavras por minuto para diferentes velocidades
    wpm_rates = {
        'muito_lenta': 80,
        'lenta': 120,
        'normal': 160,
        'rapida': 200
    }

    word_count = len(text.split())
    wpm = wpm_rates.get(speed_option, 160)
    duration_minutes = word_count / wpm

    if duration_minutes < 1:
        return f"{int(duration_minutes * 60)}s"
    else:
        minutes = int(duration_minutes)
        seconds = int((duration_minutes - minutes) * 60)
        return f"{minutes}m {seconds}s"
