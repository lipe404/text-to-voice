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

# Opções de velocidade
SPEED_OPTIONS = {
    'muito_lenta': {'label': '🐌 Muito Lenta', 'slow': True, 'description': 'Ideal para aprendizado'},
    'lenta': {'label': '🚶 Lenta', 'slow': True, 'description': 'Boa para compreensão'},
    'normal': {'label': '🚀 Normal', 'slow': False, 'description': 'Velocidade padrão'},
    'rapida': {'label': '⚡ Rápida', 'slow': False, 'description': 'Para revisão rápida'}
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

# Configurações de qualidade
QUALITY_OPTIONS = {
    'baixa': {'label': '📱 Baixa', 'description': 'Arquivo menor'},
    'media': {'label': '💻 Média', 'description': 'Equilibrio'},
    'alta': {'label': '🎧 Alta', 'description': 'Melhor qualidade'}
}
