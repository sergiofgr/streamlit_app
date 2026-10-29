import os
from datetime import datetime

import pandas as pd
import streamlit as st

# Em produção (Streamlit Cloud) o disco é efêmero: o CSV local é só um complemento.
# Use o botão "Baixar CSV" para exportar os dados da sessão.
ARQUIVO_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pacientes.csv")
COLUNAS = ["timestamp", "nome", "idade", "convenio", "prioridade", "motivo"]
CONVENIOS = ["Particular", "Unimed", "Bradesco Saúde", "SulAmérica", "Outro"]

st.set_page_config(page_title="Cadastro de Pacientes", layout="centered")
st.title("Cadastro de Pacientes")

if "pacientes" not in st.session_state:
    st.session_state.pacientes = pd.DataFrame(columns=COLUNAS)

with st.form("cadastro", clear_on_submit=True):
    nome = st.text_input("Nome do paciente")
    idade = st.number_input("Idade", min_value=0, max_value=120, step=1)
    convenio = st.selectbox("Convênio", CONVENIOS)
    prioridade = st.slider("Prioridade do atendimento (5 = urgente)", 1, 5)
    motivo = st.text_area("Motivo da consulta / observações")
    enviado = st.form_submit_button("Cadastrar")

if enviado:
    if not nome.strip():
        st.warning("⚠️ Informe o nome do paciente.")
    else:
        nova_linha = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nome": nome.strip(),
            "idade": int(idade),
            "convenio": convenio,
            "prioridade": int(prioridade),
            "motivo": motivo.strip(),
        }
        st.session_state.pacientes = pd.concat(
            [st.session_state.pacientes, pd.DataFrame([nova_linha])],
            ignore_index=True,
        )
        try:
            existe = os.path.exists(ARQUIVO_CSV)
            pd.DataFrame([nova_linha], columns=COLUNAS).to_csv(
                ARQUIVO_CSV,
                mode="a" if existe else "w",
                header=not existe,
                index=False,
                encoding="utf-8",
            )
        except OSError:
            pass  # disco somente leitura/efêmero: os dados seguem na sessão
        st.success("✅ Paciente cadastrado!")

st.subheader("Últimos pacientes cadastrados")
st.dataframe(st.session_state.pacientes.tail(5))

csv = st.session_state.pacientes.to_csv(index=False).encode("utf-8")
st.download_button("Baixar CSV", csv, "pacientes.csv", "text/csv")

