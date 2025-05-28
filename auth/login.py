import streamlit as st
import pandas as pd

def cargar_usuarios():
    return pd.read_csv("auth/usuarios.csv")

def login_interface():
    st.set_page_config(page_title="Login", layout="centered")
    st.title("🔐 Ingreso al Sistema")

    usuarios = cargar_usuarios()

    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        contraseña = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar"):
            user_row = usuarios[usuarios["usuario"] == usuario]
            if not user_row.empty and user_row.iloc[0]["password"] == contraseña:
                st.session_state.autenticado = True
                st.session_state.usuario = usuario
                st.session_state.rol = user_row.iloc[0]["rol"]
                st.success("✅ Acceso concedido")
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos.")
