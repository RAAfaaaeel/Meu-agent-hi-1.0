# -*- coding: utf-8 -*-
import streamlit as st
import google.generativeai as genai
import time
import math

st.set_page_config(page_title="Histórias Longas para Voz IA", layout="centered")

st.markdown(
    "<style>div.block-container {padding-top: 1rem; padding-bottom: 1rem;} .stTextArea textarea {font-size:1rem;} .stDownloadButton, .stButton {width: 100%}</style>",
    unsafe_allow_html=True,
)

st.title("Gerador de Histórias para Voz IA (Mobile Ready)")

api_key = st.text_input("API Key Gemini/YouTube", type="password")
video_url = st.text_input("URL do vídeo (opcional)")
premissa = st.text_area("Premissa do roteiro (opcional)", height=60)

nichos = [
    "Reencontro de família", "Superação após perda", "Milionário transforma vida",
    "Mãe solo com filhos gêmeos", "Humilhação e redenção", "Órfãos encontram família",
    "Filho rejeitado se torna exemplo", "Adotados por acidente", "Sacrifício pela família",
    "Volta por cima após traição", "Perdão inesperado", "Segredos de infância revelados",
    "Pai distante reconquista filho"
]
nicho_principal = st.selectbox("Nicho principal", nichos)
nicho_secundario = st.selectbox("Nicho secundário", ["Nenhum"] + [n for n in nichos if n != nicho_principal])

idiomas = {
    "Português": "português",
    "Inglês": "inglês",
    "Espanhol do México": "espanhol mexicano"
}
idioma = st.selectbox("Idioma do roteiro", list(idiomas.keys()))
idioma_prompt = idiomas[idioma]

modelos = [
    "gemini-1.5-flash (recomendado)",
    "gemini-2.5-pro-preview-06-05",
    "gemini-2.5-pro-preview-05-06",
    "gemini-2.5-flash-preview-05-20",
    "gemini-2.5-flash-preview-04-17"
]
modelo = st.selectbox("Modelo de IA", modelos, index=0)

duracoes = [("15 minutos", 15), ("30 minutos", 30), ("45 minutos", 45),
            ("1 hora", 60), ("1h30min", 90), ("2 horas", 120)]
duracao_str, duracao_min = st.selectbox("Duração do roteiro", duracoes, format_func=lambda x: x[0], index=4)

estilos = [
    "Direto ao ponto", "Narrativo", "Motivacional", "Diálogo natural e espontâneo"
]
estilo = st.selectbox("Estilo", estilos)

perspectivas = ["Primeira pessoa", "Terceira pessoa"]
perspectiva = st.selectbox("Perspectiva", perspectivas)

intros = [
    "Curta (50-100 palavras)", "Média (150-250 palavras)", "Longa (250-500 palavras)"
]
tamanho_intro = st.selectbox("Tamanho da introdução", intros)

diretorio_saida = st.text_input("Diretório de saída sugerido (opcional)")

# ---- Lógica para cálculo automático de blocos ----
PALAVRAS_POR_MIN = 140
PALAVRAS_POR_BLOCO = 500
total_palavras = duracao_min * PALAVRAS_POR_MIN
total_blocos = math.ceil(total_palavras / PALAVRAS_POR_BLOCO)

st.info(
    f"Sua história terá cerca de {total_palavras} palavras "
    f"({total_blocos} blocos de {PALAVRAS_POR_BLOCO} palavras)."
)

# ---- Geração automática ----
if st.button("Gerar roteiro completo"):
    if not api_key:
        st.warning("Insira sua API Key Gemini!")
    else:
        st.info("Gerando, aguarde... (pode demorar vários minutos)")
        barra = st.progress(0)
        historia_final = ""
        ultimo_texto = ""
        genai.configure(api_key=api_key)
        model_name = modelo.split(" ")[0] if "(" in modelo else modelo
        model = genai.GenerativeModel(model_name)

        for bloco in range(total_blocos):
            # Prompt detalhado para cada bloco
            instrucao_dialogo = (
                "Gere um diálogo extremamente natural, fluido e suave, como em uma conversa real entre amigos próximos. "
                "Use frases de tamanhos variados, inclua pausas naturais com reticências e expressões cotidianas quando fizer sentido, "
                "mas evite exagero ou gírias forçadas. Evite linguagem formal, literária ou rebuscada. "
                "O texto deve soar espontâneo, acolhedor e humano, como uma lembrança ou desabafo contado de forma leve e íntima. "
                "O narrador pode demonstrar hesitação ou pensamento alto, tornando tudo mais autêntico."
                if estilo == 'Diálogo natural e espontâneo' else ""
            )
            if bloco == 0:
                prompt = (
                    f"Escreva o primeiro bloco de uma história original e emocionante, baseada na premissa abaixo, "
                    f"usando apenas texto narrativo contínuo, sem títulos, numeração, marcações ou comentários. "
                    f"O bloco deve ter cerca de {PALAVRAS_POR_BLOCO} palavras. "
                    f"Nicho principal: {nicho_principal}. "
                    f"Nicho secundário: {nicho_secundario if nicho_secundario != 'Nenhum' else ''}. "
                    f"Estilo: {estilo.lower()}. "
                    f"{instrucao_dialogo} "
                    f"Perspectiva: {perspectiva.lower()}. "
                    f"Tamanho da introdução: {tamanho_intro.lower()}. "
                    f"Idioma: {idioma_prompt}. "
                    f"Premissa base: {premissa if premissa.strip() else '(crie uma história do zero dentro dos nichos)'} "
                    f"Termine o bloco com um cliffhanger, de forma natural."
                )
            elif bloco == total_blocos - 1:
                prompt = (
                    f"Continue imediatamente a narrativa abaixo, escrevendo o último bloco de cerca de {PALAVRAS_POR_BLOCO} palavras. "
                    f"Mantenha o estilo {estilo.lower()}, nicho {nicho_principal}{(' / ' + nicho_secundario) if nicho_secundario != 'Nenhum' else ''}, "
                    f"perspectiva {perspectiva.lower()}, e idioma {idioma_prompt}. "
                    f"{instrucao_dialogo} "
                    f"Nunca use títulos ou quebras. "
                    f"Ao final, adicione uma chamada para ação humanizada, convidando o espectador a se inscrever no canal, comentar e compartilhar a história, sempre escrevendo tudo no idioma {idioma_prompt}."
                    f"Texto até agora: {ultimo_texto[-4000:]}"
                )
            else:
                prompt = (
                    f"Continue a narrativa abaixo, criando o próximo bloco de aproximadamente {PALAVRAS_POR_BLOCO} palavras. "
                    f"Não use títulos, numeração, marcações ou comentários, apenas narrativa pura. "
                    f"Mantenha o estilo {estilo.lower()}, nicho {nicho_principal}{(' / ' + nicho_secundario) if nicho_secundario != 'Nenhum' else ''}, "
                    f"perspectiva {perspectiva.lower()}, e idioma {idioma_prompt}. "
                    f"{instrucao_dialogo} "
                    f"Premissa base: {premissa if premissa.strip() else '(crie uma história do zero dentro dos nichos)'} "
                    f"Texto até agora: {ultimo_texto[-4000:]}. "
                    f"Finalize o bloco com um cliffhanger."
                )
            try:
                resposta = model.generate_content(prompt)
                bloco_gerado = resposta.text.strip().replace("\n\n", " ").replace("\n", " ")
                historia_final += " " + bloco_gerado
                ultimo_texto = historia_final
                barra.progress((bloco + 1) / total_blocos)
                time.sleep(1)
            except Exception as e:
                st.error(f"Erro ao gerar o bloco {bloco + 1}: {e}")
                break

        st.success("História completa gerada!")
        st.text_area("Prévia da história (início):", value=historia_final[:2000] + " ...", height=230)
        st.download_button(
            label="📥 Baixar História Completa (.txt)",
            data=historia_final.strip(),
            file_name="historia_completa.txt",
            mime="text/plain"
        )
        st.balloons()

st.markdown(
    "<div style='font-size: 0.85em; color: #666;'>Dica: para usar no celular, abra <b>http://IP_DO_PC:8501</b> no navegador do seu smartphone conectado à mesma Wi-Fi.</div>",
    unsafe_allow_html=True
)