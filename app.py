import streamlit as st
import io
import time
from datetime import datetime
from config import LANGUAGES, UI_CONFIG, LIMITS
from utils.audio_utils import text_to_speech, split_text, process_long_text, get_download_link, get_multiple_download_links

# Configuração da página
st.set_page_config(
    page_title=UI_CONFIG['page_title'],
    page_icon=UI_CONFIG['page_icon'],
    layout=UI_CONFIG['layout'],
    initial_sidebar_state=UI_CONFIG['initial_sidebar_state']
)


def main():
    # Header
    st.title("Text to Voice Converter")
    st.markdown("---")

    # Descrição
    st.markdown("""
    ### Como usar:
    1. **Digite ou cole** seu texto na área abaixo
    2. **Escolha o idioma** desejado
    3. **Configure as opções** de áudio
    4. **Clique em gerar** e baixe seu áudio!

    *Suporte para textos longos com geração de múltiplos arquivos*
    """)

    # Sidebar com configurações
    with st.sidebar:
        st.header("Configurações")

        # Seleção de idioma
        selected_lang = st.selectbox(
            "Idioma:",
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            index=0
        )

        # Velocidade
        slow_speech = st.checkbox("Velocidade lenta", value=False)

        # Opção para textos longos
        st.markdown("---")
        st.markdown("### Textos Longos")
        merge_option = st.radio(
            "Como processar textos longos:",
            ["Arquivos separados", "Arquivo único (experimental)"],
            help="Arquivos separados são mais confiáveis para textos muito longos"
        )

        # Informações
        st.markdown("---")
        st.markdown("### Informações")
        st.info(f"**Limite por chunk:** {LIMITS['chunk_size']} caracteres")
        st.info("**Formatos suportados:** MP3")

        # Estatísticas da sessão
        if 'conversions_count' not in st.session_state:
            st.session_state.conversions_count = 0

        st.markdown("---")
        st.markdown("### Estatísticas")
        st.metric("Conversões nesta sessão",
                  st.session_state.conversions_count)

    # Área principal
    col1, col2 = st.columns([2, 1])

    with col1:
        # Área de texto
        st.subheader("Texto para Conversão")
        text_input = st.text_area(
            "Digite ou cole seu texto aqui:",
            height=300,
            placeholder="Cole aqui o texto que você deseja converter em áudio...\n\nNão há limite de caracteres! O sistema dividirá automaticamente textos longos em partes menores.",
            help="Textos longos serão automaticamente divididos em chunks para melhor processamento"
        )

        # Contador de caracteres
        char_count = len(text_input)
        st.caption(f"Caracteres: {char_count:,}")

        if char_count > LIMITS['chunk_size']:
            chunks_needed = len(split_text(text_input, LIMITS['chunk_size']))
            st.info(
                f"ℹTexto longo detectado! Será dividido em {chunks_needed} partes.")

    with col2:
        # Preview e controles
        st.subheader("Controles")

        # Botão de gerar
        generate_button = st.button(
            "Gerar Áudio",
            type="primary",
            disabled=not text_input.strip(),
            use_container_width=True
        )

        # Preview do texto
        if text_input.strip():
            st.markdown("**Preview:**")
            preview_text = text_input[:200] + \
                "..." if len(text_input) > 200 else text_input
            st.text_area("", value=preview_text, height=100, disabled=True)

    # Processamento
    if generate_button and text_input.strip():
        process_text_to_speech(text_input, selected_lang,
                               slow_speech, merge_option)


def process_text_to_speech(text, language, slow, merge_option):
    """Processa a conversão de texto para áudio"""

    with st.spinner("Gerando áudio..."):
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Verificar se precisa dividir o texto
            if len(text) <= LIMITS['chunk_size']:
                # Texto curto - processamento direto
                status_text.text("Convertendo texto em áudio...")
                progress_bar.progress(50)

                audio_data = text_to_speech(text, language, slow)
                progress_bar.progress(100)

                if audio_data:
                    display_single_audio_result(audio_data, text)
                    st.session_state.conversions_count += 1

            else:
                # Texto longo
                chunks = split_text(text, LIMITS['chunk_size'])
                total_chunks = len(chunks)

                status_text.text(
                    f"Dividindo texto em {total_chunks} partes...")
                time.sleep(0.5)

                audio_chunks = []

                for i, chunk in enumerate(chunks):
                    status_text.text(
                        f"Processando parte {i+1}/{total_chunks}...")
                    progress = int((i / total_chunks) * 100)
                    progress_bar.progress(progress)

                    chunk_audio = text_to_speech(chunk, language, slow)
                    if chunk_audio:
                        audio_chunks.append(chunk_audio)
                    else:
                        st.error(f"Erro ao processar parte {i+1}")
                        return

                    # Pequena pausa para evitar rate limiting
                    time.sleep(0.3)

                progress_bar.progress(100)

                if audio_chunks:
                    if merge_option == "Arquivo único (experimental)":
                        display_merged_audio_result(
                            audio_chunks, text, total_chunks)
                    else:
                        display_multiple_audio_result(
                            audio_chunks, text, total_chunks)
                    st.session_state.conversions_count += 1

        except Exception as e:
            st.error(f"Erro durante o processamento: {str(e)}")

        finally:
            progress_bar.empty()
            status_text.empty()


def display_single_audio_result(audio_data, original_text):
    """Exibe o resultado de um único áudio"""

    st.success("Áudio gerado com sucesso!")

    # Informações do áudio
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Caracteres", f"{len(original_text):,}")

    with col2:
        st.metric("Arquivos", "1")

    with col3:
        audio_size = len(audio_data) / 1024  # KB
        st.metric("Tamanho", f"{audio_size:.1f} KB")

    # Player de áudio
    st.subheader("Player de Áudio")
    st.audio(audio_data, format='audio/mp3')

    # Download
    st.subheader("Download")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"texto_para_audio_{timestamp}.mp3"

    download_link = get_download_link(audio_data, filename)
    st.markdown(download_link, unsafe_allow_html=True)


def display_multiple_audio_result(audio_chunks, original_text, chunks_count):
    """Exibe o resultado de múltiplos áudios"""

    st.success("Áudios gerados com sucesso!")

    # Informações do áudio
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Caracteres", f"{len(original_text):,}")

    with col2:
        st.metric("Arquivos", chunks_count)

    with col3:
        total_size = sum(len(chunk) for chunk in audio_chunks) / 1024  # KB
        st.metric("Tamanho Total", f"{total_size:.1f} KB")

    # Players de áudio
    st.subheader("Players de Áudio")

    for i, audio_data in enumerate(audio_chunks):
        with st.expander(f"Parte {i+1}/{chunks_count}"):
            st.audio(audio_data, format='audio/mp3')

    # Downloads
    st.subheader("Downloads")
    st.markdown("**Baixar arquivos individuais:**")
    download_links = get_multiple_download_links(audio_chunks)
    st.markdown(download_links, unsafe_allow_html=True)


def display_merged_audio_result(audio_chunks, original_text, chunks_count):
    """Exibe resultado experimental de áudio mesclado (concatenação simples)"""

    st.warning(
        "Modo experimental: Os áudios serão concatenados de forma simples")

    # Concatenar os bytes dos áudios (método simples)
    merged_audio = b''.join(audio_chunks)

    st.success("Áudios concatenados!")

    # Informações do áudio
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Caracteres", f"{len(original_text):,}")

    with col2:
        st.metric("Partes processadas", chunks_count)

    with col3:
        audio_size = len(merged_audio) / 1024  # KB
        st.metric("Tamanho", f"{audio_size:.1f} KB")

    # Player de áudio
    st.subheader("Player de Áudio Concatenado")
    st.audio(merged_audio, format='audio/mp3')

    # Download
    st.subheader("Download")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"texto_completo_{timestamp}.mp3"

    download_link = get_download_link(merged_audio, filename)
    st.markdown(download_link, unsafe_allow_html=True)

# Footer


def show_footer():
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p><strong>Text to Voice Converter</strong> | Desenvolvido com Streamlit e gTTS</p>
            <p><em>Converta textos longos em áudio de alta qualidade</em></p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
    show_footer()
