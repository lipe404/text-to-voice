import streamlit as st
import io
import time
from datetime import datetime
from config import LANGUAGES, UI_CONFIG, LIMITS, SPEED_OPTIONS, QUALITY_OPTIONS
from utils.audio_utils import (
    text_to_speech, split_text, get_download_link,
    get_multiple_download_links, get_audio_info, estimate_duration
)

# Configuração da página
st.set_page_config(
    page_title=UI_CONFIG['page_title'],
    page_icon=UI_CONFIG['page_icon'],
    layout=UI_CONFIG['layout'],
    initial_sidebar_state=UI_CONFIG['initial_sidebar_state']
)


def main():
    # Header com estilo
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 30px;'>
        <h1 style='color: white; margin: 0;'>🎵 Text to Voice Converter</h1>
        <p style='color: white; margin: 5px 0 0 0; opacity: 0.9;'>Converta textos em áudio de alta qualidade</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar com configurações avançadas
    with st.sidebar:
        st.header("⚙️ Configurações")

        # Seleção de idioma
        selected_lang = st.selectbox(
            "🌍 Idioma:",
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            index=0
        )

        # Controle de velocidade avançado
        st.markdown("---")
        st.markdown("### Controle de Velocidade")

        speed_option = st.selectbox(
            "Velocidade de fala:",
            options=list(SPEED_OPTIONS.keys()),
            format_func=lambda x: SPEED_OPTIONS[x]['label'],
            index=2,  # Normal por padrão
            help="Escolha a velocidade ideal para sua necessidade"
        )

        # Mostrar descrição da velocidade selecionada
        st.caption(f"ℹ️ {SPEED_OPTIONS[speed_option]['description']}")

        # Opções avançadas
        st.markdown("---")
        st.markdown("### 🔧 Opções Avançadas")

        # Qualidade (visual apenas, gTTS não suporta)
        quality_option = st.selectbox(
            "Qualidade do áudio:",
            options=list(QUALITY_OPTIONS.keys()),
            format_func=lambda x: QUALITY_OPTIONS[x]['label'],
            index=1,  # Média por padrão
            help="Configuração visual - gTTS usa qualidade padrão"
        )

        # Opção para textos longos
        merge_option = st.radio(
            "Textos longos:",
            ["Arquivos separados", "Arquivo único"],
            help="Arquivos separados são mais confiáveis"
        )

        # Informações do sistema
        st.markdown("---")
        st.markdown("### Informações")
        st.info(f"**Limite por chunk:** {LIMITS['chunk_size']} caracteres")
        st.info("**Formato:** MP3 (gTTS)")

        # Estatísticas da sessão
        if 'conversions_count' not in st.session_state:
            st.session_state.conversions_count = 0
        if 'total_chars' not in st.session_state:
            st.session_state.total_chars = 0

        st.markdown("---")
        st.markdown("### Estatísticas da Sessão")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Conversões", st.session_state.conversions_count)
        with col2:
            st.metric("Caracteres", f"{st.session_state.total_chars:,}")

    # Área principal
    col1, col2 = st.columns([2, 1])

    with col1:
        # Área de texto melhorada
        st.markdown("### Texto para Conversão")
        text_input = st.text_area(
            "",
            height=350,
            placeholder="Digite ou cole seu texto aqui...\n\n Dicas:\n• Não há limite de caracteres\n• Use pontuação para melhor resultado\n• Textos longos serão divididos automaticamente\n• Experimente diferentes velocidades!",
            help="O sistema divide automaticamente textos longos para melhor processamento"
        )

        # Informações do texto em tempo real
        if text_input:
            char_count = len(text_input)
            word_count = len(text_input.split())
            estimated_duration = estimate_duration(text_input, speed_option)

            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric("Caracteres", f"{char_count:,}")
            with col_info2:
                st.metric("Palavras", f"{word_count:,}")
            with col_info3:
                st.metric("Duração estimada", estimated_duration)

            if char_count > LIMITS['chunk_size']:
                chunks_needed = len(split_text(
                    text_input, LIMITS['chunk_size']))
                st.info(
                    f"Texto longo detectado! Será dividido em **{chunks_needed} partes**.")

    with col2:
        # Painel de controle
        st.markdown("### Painel de Controle")

        # Preview da configuração
        with st.container():
            st.markdown("**Configuração Atual:**")
            config_info = f"""
            - **Idioma:** {LANGUAGES[selected_lang]}
            - **Velocidade:** {SPEED_OPTIONS[speed_option]['label']}
            - **Qualidade:** {QUALITY_OPTIONS[quality_option]['label']}
            - **Modo:** {merge_option}
            """
            st.markdown(config_info)

        # Botão de gerar com estilo
        generate_button = st.button(
            "🎵 Gerar Áudio",
            type="primary",
            disabled=not text_input.strip(),
            use_container_width=True,
            help="Clique para converter o texto em áudio"
        )

        # Preview do texto
        if text_input.strip():
            with st.expander("Preview do Texto", expanded=False):
                preview_text = text_input[:300] + \
                    "..." if len(text_input) > 300 else text_input
                st.text_area("", value=preview_text, height=150,
                             disabled=True, key="preview")

    # Processamento
    if generate_button and text_input.strip():
        process_text_to_speech(text_input, selected_lang,
                               speed_option, merge_option)


def process_text_to_speech(text, language, speed_option, merge_option):
    """Processa a conversão de texto para áudio com velocidade personalizada"""

    with st.spinner("Gerando áudio..."):
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Determinar se usar slow do gTTS
            use_slow = SPEED_OPTIONS[speed_option]['slow']

            # Verificar se precisa dividir o texto
            if len(text) <= LIMITS['chunk_size']:
                # Texto curto - processamento direto
                status_text.text("Convertendo texto em áudio...")
                progress_bar.progress(50)

                audio_data = text_to_speech(
                    text, language, use_slow, speed_option)
                progress_bar.progress(100)

                if audio_data:
                    display_single_audio_result(audio_data, text, speed_option)
                    st.session_state.conversions_count += 1
                    st.session_state.total_chars += len(text)

            else:
                # Texto longo
                chunks = split_text(text, LIMITS['chunk_size'])
                total_chunks = len(chunks)

                status_text.text(
                    f"Dividindo texto em {total_chunks} partes...")
                progress_bar.progress(10)
                time.sleep(0.5)

                audio_chunks = []

                for i, chunk in enumerate(chunks):
                    status_text.text(
                        f"Processando parte {i+1}/{total_chunks}...")
                    progress = int(10 + (i / total_chunks) * 80)
                    progress_bar.progress(progress)

                    chunk_audio = text_to_speech(
                        chunk, language, use_slow, speed_option)
                    if chunk_audio:
                        audio_chunks.append(chunk_audio)
                    else:
                        st.error(f"Erro ao processar parte {i+1}")
                        return

                    # Pausa para evitar rate limiting
                    time.sleep(0.4)

                status_text.text("Finalizando processamento...")
                progress_bar.progress(100)

                if audio_chunks:
                    if merge_option == "Arquivo único":
                        display_merged_audio_result(
                            audio_chunks, text, total_chunks, speed_option)
                    else:
                        display_multiple_audio_result(
                            audio_chunks, text, total_chunks, speed_option)
                    st.session_state.conversions_count += 1
                    st.session_state.total_chars += len(text)

        except Exception as e:
            st.error(f"Erro durante o processamento: {str(e)}")

        finally:
            progress_bar.empty()
            status_text.empty()


def display_single_audio_result(audio_data, original_text, speed_option):
    """Exibe resultado de áudio único com informações detalhadas"""

    st.success("Áudio gerado com sucesso!")

    # Informações detalhadas
    audio_info = get_audio_info(audio_data)
    estimated_duration = estimate_duration(original_text, speed_option)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Caracteres", f"{len(original_text):,}")
    with col2:
        st.metric("Arquivos", "1")
    with col3:
        st.metric("Tamanho", audio_info['size'])
    with col4:
        st.metric("⏱Duração", estimated_duration)

    # Player de áudio
    st.markdown("### Player de Áudio")
    st.audio(audio_data, format='audio/mp3')

    # Download
    st.markdown("### Download")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    speed_suffix = speed_option if speed_option != 'normal' else ''
    filename = f"audio_{speed_suffix}_{timestamp}.mp3"

    download_link = get_download_link(audio_data, filename)
    st.markdown(download_link, unsafe_allow_html=True)


def display_multiple_audio_result(audio_chunks, original_text, chunks_count, speed_option):
    """Exibe resultado de múltiplos áudios"""

    st.success("Áudios gerados com sucesso!")

    # Informações detalhadas
    total_size = sum(len(chunk) for chunk in audio_chunks)
    audio_info = get_audio_info(b''.join(audio_chunks))
    estimated_duration = estimate_duration(original_text, speed_option)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Caracteres", f"{len(original_text):,}")
    with col2:
        st.metric("Arquivos", chunks_count)
    with col3:
        st.metric("Tamanho Total", audio_info['size'])
    with col4:
        st.metric("Duração", estimated_duration)

    # Players de áudio organizados
    st.markdown("### Players de Áudio")

    # Mostrar apenas os primeiros 3 por padrão
    show_all = st.checkbox("Mostrar todos os players", value=False)
    display_count = len(audio_chunks) if show_all else min(
        3, len(audio_chunks))

    for i in range(display_count):
        audio_data = audio_chunks[i]
        chunk_info = get_audio_info(audio_data)

        with st.expander(f"Parte {i+1}/{chunks_count} ({chunk_info['size']})", expanded=i == 0):
            st.audio(audio_data, format='audio/mp3')

    if not show_all and len(audio_chunks) > 3:
        st.info(f"➕ {len(audio_chunks) - 3} players adicionais disponíveis")

    # Downloads
    st.markdown("### Downloads")
    st.markdown("**Baixar arquivos individuais:**")
    download_links = get_multiple_download_links(audio_chunks)
    st.markdown(download_links, unsafe_allow_html=True)


def display_merged_audio_result(audio_chunks, original_text, chunks_count, speed_option):
    """Exibe resultado de áudio mesclado"""

    st.warning("Modo experimental: Concatenação simples de áudios")

    # Concatenar áudios
    merged_audio = b''.join(audio_chunks)

    st.success("Áudios concatenados!")

    # Informações
    audio_info = get_audio_info(merged_audio)
    estimated_duration = estimate_duration(original_text, speed_option)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Caracteres", f"{len(original_text):,}")
    with col2:
        st.metric("Partes", chunks_count)
    with col3:
        st.metric("Tamanho", audio_info['size'])
    with col4:
        st.metric("Duração", estimated_duration)

    # Player
    st.markdown("### Player de Áudio Completo")
    st.audio(merged_audio, format='audio/mp3')

    # Download
    st.markdown("### Download")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    speed_suffix = speed_option if speed_option != 'normal' else ''
    filename = f"audio_completo_{speed_suffix}_{timestamp}.mp3"

    download_link = get_download_link(merged_audio, filename)
    st.markdown(download_link, unsafe_allow_html=True)


def show_footer():
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 30px; background: #f8f9fa; border-radius: 10px; margin-top: 40px;'>
        <h4 style='margin: 0 0 10px 0; color: #333;'>Text to Voice Converter</h4>
        <p style='margin: 0; font-size: 14px;'>Desenvolvido com ❤️ usando Streamlit e Google Text-to-Speech</p>
        <p style='margin: 5px 0 0 0; font-size: 12px; opacity: 0.7;'>Converta textos em áudio de alta qualidade com controle total de velocidade</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
    show_footer()
