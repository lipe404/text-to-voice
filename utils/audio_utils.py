import io
import base64
from gtts import gTTS
import streamlit as st
import time
import re
from config import VOICE_OPTIONS, VOICE_FILTERS, PITCH_OPTIONS


def text_to_speech(text, language='pt', slow=False, speed_option='normal',
                   voice_type='feminina', voice_filter='normal', pitch='normal'):
    """
    Converte texto em áudio usando gTTS com controle avançado de voz

    Args:
        text (str): Texto para converter
        language (str): Código do idioma
        slow (bool): Velocidade lenta (gTTS)
        speed_option (str): Opção de velocidade personalizada
        voice_type (str): Tipo de voz (feminina/masculina/infantil)
        voice_filter (str): Filtro de voz aplicado
        pitch (str): Tom da voz

    Returns:
        bytes: Dados do áudio em formato MP3
    """
    try:
        # Processar texto baseado na velocidade e filtros
        processed_text = process_text_for_voice(
            text, speed_option, voice_filter, pitch)

        # Obter configurações da voz
        voice_config = get_voice_config(language, voice_type)

        # Ajustar velocidade baseada no tipo de voz
        adjusted_slow = adjust_speed_for_voice(
            slow, voice_config, speed_option)

        # Criar objeto gTTS com configurações de voz
        tts = gTTS(
            text=processed_text,
            lang=language,
            slow=adjusted_slow,
            tld=voice_config.get('tld', 'com')
        )

        # Salvar em buffer de memória
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        return audio_buffer.getvalue()

    except Exception as e:
        st.error(f"Erro ao gerar áudio: {str(e)}")
        return None


def get_voice_config(language, voice_type):
    """
    Obtém configuração da voz baseada no idioma e tipo
    """
    if language in VOICE_OPTIONS and voice_type in VOICE_OPTIONS[language]:
        return VOICE_OPTIONS[language][voice_type]
    else:
        # Fallback para voz feminina padrão
        return {
            'label': 'Voz Padrão',
            'description': 'Voz padrão',
            'tld': 'com',
            'slow_adjustment': 1.0
        }


def adjust_speed_for_voice(slow, voice_config, speed_option):
    """
    Ajusta velocidade baseada no tipo de voz
    """
    adjustment = voice_config.get('slow_adjustment', 1.0)

    # Para voz masculina, usar velocidade ligeiramente mais lenta
    if adjustment < 1.0 and speed_option in ['normal', 'rapida']:
        return True  # Forçar slow para simular voz mais grave

    return slow


def process_text_for_voice(text, speed_option, voice_filter, pitch):
    """
    Processa o texto para simular diferentes vozes e filtros

    Args:
        text (str): Texto original
        speed_option (str): Opção de velocidade
        voice_filter (str): Filtro de voz
        pitch (str): Tom da voz

    Returns:
        str: Texto processado
    """
    processed_text = text

    # Aplicar processamento de velocidade
    processed_text = process_text_for_speed(processed_text, speed_option)

    # Aplicar filtros de voz
    processed_text = apply_voice_filter(processed_text, voice_filter)

    # Aplicar ajustes de pitch via texto
    processed_text = apply_pitch_adjustment(processed_text, pitch)

    return processed_text


def process_text_for_speed(text, speed_option):
    """
    Processa o texto para simular diferentes velocidades
    """
    if speed_option == 'muito_lenta':
        return re.sub(r'\s+', ' ... ', text)
    elif speed_option == 'lenta':
        return re.sub(r'\s+', ' .. ', text)
    elif speed_option == 'rapida':
        text = re.sub(r'\s*,\s*', ', ', text)
        text = re.sub(r'\s*\.\s*', '. ', text)
        return text
    else:  # normal
        return text


def apply_voice_filter(text, voice_filter):
    """
    Aplica filtros de voz através de processamento de texto
    """
    if voice_filter == 'robotico':
        # Adicionar pausas robóticas
        text = re.sub(r'\b(\w+)\b', r'\1.', text)
        text = re.sub(r'\.+', '.', text)
        return text

    elif voice_filter == 'eco':
        # Simular eco repetindo palavras importantes
        words = text.split()
        processed_words = []
        for i, word in enumerate(words):
            processed_words.append(word)
            # Adicionar eco em palavras longas
            if len(word) > 6 and i % 3 == 0:
                processed_words.append(f"...{word[-3:]}...")
        return ' '.join(processed_words)

    elif voice_filter == 'sussurro':
        # Simular sussurro com pausas suaves
        return re.sub(r'\s+', ' .. ', text)

    elif voice_filter == 'dramatico':
        # Adicionar ênfase dramática
        text = re.sub(r'[.!?]', r'...', text)
        text = re.sub(r'\b(muito|grande|importante|incrível|fantástico)\b',
                      r'... \1 ...', text, flags=re.IGNORECASE)
        return text

    elif voice_filter == 'animado':
        # Tom mais animado com exclamações
        text = re.sub(r'\.', '!', text)
        text = re.sub(r'\b(ótimo|excelente|maravilhoso|fantástico)\b',
                      r'... \1! ...', text, flags=re.IGNORECASE)
        return text

    else:  # normal
        return text


def apply_pitch_adjustment(text, pitch):
    """
    Simula ajuste de pitch através de modificações no texto
    """
    pitch_config = PITCH_OPTIONS.get(pitch, PITCH_OPTIONS['normal'])
    multiplier = pitch_config['multiplier']

    if multiplier < 0.9:  # Voz mais grave
        # Adicionar pausas para simular voz mais grave
        text = re.sub(r'\s+', ' . ', text)
    elif multiplier > 1.1:  # Voz mais aguda
        # Remover algumas pausas para simular voz mais aguda
        text = re.sub(r'\s*,\s*', ' ', text)
        text = re.sub(r'\s+', ' ', text)

    return text


def split_text(text, max_length=500):
    """
    Divide texto longo em chunks menores de forma inteligente
    """
    text = text.strip()
    if not text:
        return []

    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        if len(current_chunk + paragraph) <= max_length:
            current_chunk += paragraph + "\n\n"
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())

            if len(paragraph) > max_length:
                sentence_chunks = split_by_sentences(paragraph, max_length)
                chunks.extend(sentence_chunks)
                current_chunk = ""
            else:
                current_chunk = paragraph + "\n\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def split_by_sentences(text, max_length):
    """
    Divide texto por sentenças
    """
    sentences = re.split(r'[.!?]+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

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


def get_voice_preview_text(voice_type, voice_filter):
    """
    Retorna texto de preview para demonstrar a voz selecionada
    """
    base_text = "Olá! Esta é uma demonstração da voz selecionada."

    if voice_type == 'masculina':
        return "Olá! Esta é uma demonstração da voz masculina brasileira."
    elif voice_type == 'infantil':
        return "Oi! Esta é uma demonstração da voz infantil!"
    elif voice_filter == 'robotico':
        return "Olá. Esta. É. Uma. Demonstração. Da. Voz. Robótica."
    elif voice_filter == 'dramatico':
        return "Olá... Esta é uma demonstração... DRAMÁTICA... da voz selecionada!"
    else:
        return base_text
