import streamlit as st
import numpy as np
import pickle
import re
import time
import pandas as pd
from difflib import get_close_matches

# ================================
# CONFIG
# ================================
st.set_page_config(
    page_title="Health Bot Clinic",
    page_icon="🏥",
    layout="wide"
)

# ================================
# LOAD DATA (AMAN TANPA TENSORFLOW)
# ================================
@st.cache_resource
def load_all():
    try:
        tokenizer = pickle.load(open("tokenizer.pkl", "rb"))
        label_encoder = pickle.load(open("label_encoder.pkl", "rb"))
        responses = pickle.load(open("responses.pkl", "rb"))

        df = pd.read_excel("DATASET_PHS.xlsx")
        df.columns = df.columns.str.strip().str.lower()
        qa_pairs = dict(zip(df["pertanyaan"], df["jawaban"]))

        return tokenizer, label_encoder, responses, qa_pairs

    except Exception as e:
        st.error(f"Error load data: {e}")
        return None, None, None, {
            "demam": "Istirahat yang cukup dan perbanyak minum air putih.",
            "batuk": "Minum air hangat dan hindari makanan berminyak.",
            "pusing": "Istirahat dan kurangi aktivitas berat."
        }

tokenizer, label_encoder, responses, qa_pairs = load_all()

# ================================
# SESSION
# ================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "patient" not in st.session_state:
    st.session_state.patient = {"nama": "", "umur": ""}

# ================================
# FUNCTION
# ================================
def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())

def get_response(user_input):
    text = clean_text(user_input)
    nama = st.session_state.patient["nama"] or "Pasien"

    # exact match
    if text in qa_pairs:
        return f"Halo **{nama}**, {qa_pairs[text]}"

    # fuzzy match
    match = get_close_matches(text, qa_pairs.keys(), n=1, cutoff=0.6)
    if match:
        return f"Halo **{nama}**, {qa_pairs[match[0]]}"

    return f"Maaf **{nama}**, saya belum menemukan jawaban yang sesuai."

# ================================
# HEADER
# ================================
st.markdown("""
<h1 style='text-align:center; color:#0083b0;'>🏥 Health Bot Clinic</h1>
<p style='text-align:center;'>Chatbot Edukasi Pola Hidup Sehat</p>
""", unsafe_allow_html=True)

# ================================
# SIDEBAR
# ================================
with st.sidebar:
    st.header("📋 Data Pasien")

    nama = st.text_input("Nama", st.session_state.patient["nama"])
    umur = st.text_input("Umur", st.session_state.patient["umur"])

    if st.button("Simpan"):
        if nama and umur.isdigit():
            st.session_state.patient["nama"] = nama
            st.session_state.patient["umur"] = umur
            st.success("Data tersimpan")
            st.rerun()
        else:
            st.error("Input tidak valid")

    if st.button("Hapus Chat"):
        st.session_state.messages = []
        st.rerun()

# ================================
# CHAT
# ================================
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])

if prompt := st.chat_input("Ketik pertanyaan..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Memproses..."):
        time.sleep(0.5)
        response = get_response(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
