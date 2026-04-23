import streamlit as st
import pandas as pd
import pickle
import re
import time
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
# LOAD DATA (AMAN)
# ================================
@st.cache_resource
def load_all():
    qa_pairs = {}

    # Load dataset Excel
    try:
        df = pd.read_excel("DATASET_PHS.xlsx")
        df.columns = df.columns.str.strip().str.lower()

        if "pertanyaan" in df.columns and "jawaban" in df.columns:
            qa_pairs = dict(zip(df["pertanyaan"], df["jawaban"]))

    except Exception as e:
        st.warning(f"Gagal load dataset Excel: {e}")

    # Fallback jika kosong
    if not qa_pairs:
        qa_pairs = {
            "demam": "Istirahat yang cukup dan perbanyak minum air putih.",
            "batuk": "Minum air hangat dan hindari makanan berminyak.",
            "pusing": "Istirahat dan kurangi aktivitas berat.",
            "flu": "Perbanyak istirahat dan konsumsi vitamin C."
        }

    return qa_pairs

qa_pairs = load_all()

# ================================
# SESSION STATE
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

    # Exact match
    if text in qa_pairs:
        return f"Halo **{nama}**, {qa_pairs[text]}"

    # Fuzzy match
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

    st.markdown("---")

    if st.button("🗑️ Hapus Chat"):
        st.session_state.messages = []
        st.rerun()

# ================================
# CHAT DISPLAY
# ================================
if not st.session_state.messages:
    st.info("💬 Silakan mulai bertanya tentang kesehatan...")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ================================
# INPUT CHAT
# ================================
if prompt := st.chat_input("Ketik pertanyaan..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Memproses..."):
        time.sleep(0.5)
        response = get_response(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
