# Configurações do aplicativo
import os

# Configurações de áudio
AUDIO_CONFIG = {
    'format': 'mp3',
    'quality': 'high',
    'speed': 'normal'
}

# Idiomas suportados com opções de voz
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

# Opções de voz para português brasileiro
VOICE_OPTIONS = {
    'pt': {
        'feminina': {
            'label': 'Voz Feminina',
            'description': 'Voz padrão feminina',
            'tld': 'com.br',  # Domínio brasileiro
            'slow_adjustment': 1.0
        },
        'masculina': {
            'label': 'Voz Masculina',
            'description': 'Voz simulada masculina',
            'tld': 'com',  # Domínio global (tom mais grave)
            'slow_adjustment': 0.9  # Ligeiramente mais lento para simular voz masculina
        },
        'infantil': {
            'label': 'Voz Infantil',
            'description': 'Voz simulada infantil',
            'tld': 'co.uk',  # Domínio UK (tom mais agudo)
            'slow_adjustment': 1.2  # Mais rápido para simular voz infantil
        }
    },
    'en': {
        'feminina': {
            'label': 'Female Voice',
            'description': 'Default female voice',
            'tld': 'com',
            'slow_adjustment': 1.0
        },
        'masculina': {
            'label': 'Male Voice',
            'description': 'Simulated male voice',
            'tld': 'co.uk',
            'slow_adjustment': 0.9
        }
    }
}

# Filtros de voz disponíveis
VOICE_FILTERS = {
    'normal': {
        'label': 'Normal',
        'description': 'Sem filtros aplicados',
        'text_processing': None
    },
    'robotico': {
        'label': 'Robótico',
        'description': 'Efeito de voz robótica',
        'text_processing': 'robot'
    },
    'eco': {
        'label': 'Eco',
        'description': 'Efeito de eco/reverb',
        'text_processing': 'echo'
    },
    'sussurro': {
        'label': 'Sussurro',
        'description': 'Efeito de sussurro',
        'text_processing': 'whisper'
    },
    'dramatico': {
        'label': 'Dramático',
        'description': 'Entonação dramática',
        'text_processing': 'dramatic'
    },
    'animado': {
        'label': 'Animado',
        'description': 'Tom mais animado',
        'text_processing': 'excited'
    }
}

# Opções de velocidade
SPEED_OPTIONS = {
    'muito_lenta': {'label': 'Muito Lenta', 'slow': True, 'description': 'Ideal para aprendizado'},
    'lenta': {'label': 'Lenta', 'slow': True, 'description': 'Boa para compreensão'},
    'normal': {'label': 'Normal', 'slow': False, 'description': 'Velocidade padrão'},
    'rapida': {'label': 'Rápida', 'slow': False, 'description': 'Para revisão rápida'}
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
    'baixa': {'label': 'Baixa', 'description': 'Arquivo menor'},
    'media': {'label': 'Média', 'description': 'Equilibrio'},
    'alta': {'label': 'Alta', 'description': 'Melhor qualidade'}
}

# Configurações de pitch/tom (simulado via processamento de texto)
PITCH_OPTIONS = {
    'muito_grave': {'label': 'Muito Grave', 'multiplier': 0.7},
    'grave': {'label': 'Grave', 'multiplier': 0.85},
    'normal': {'label': 'Normal', 'multiplier': 1.0},
    'agudo': {'label': 'Agudo', 'multiplier': 1.15},
    'muito_agudo': {'label': 'Muito Agudo', 'multiplier': 1.3}
}
