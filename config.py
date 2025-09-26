# Configurações do aplicativo
import os

# Configurações de áudio
AUDIO_CONFIG = {
    'format': 'mp3',
    'quality': 'high',
    'speed': 'normal'
}

# Idiomas suportados
LANGUAGES = {
    'pt': 'Português (Brasil)',
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'it': 'Italiano',
    'de': 'Deutsch',
    'ja': '日本語',
    'ko': '한국어',
    'zh': '中文'
}

# Configurações da interface
UI_CONFIG = {
    'page_title': 'Text to Voice Converter',
    'page_icon': '🎵',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Limites
LIMITS = {
    'max_chars': 5000,  # Limite do gTTS
    'chunk_size': 500   # Tamanho do chunk para textos longos
}
