import streamlit as st
from auth.login import login_interface
from pages import admin_datos, visualizaciones, info_nacional

# Iniciar sesión
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    login_interface()
else:
    st.set_page_config(page_title="Producción Huevos", layout="wide")
    rol = st.session_state.get("rol", "Invitado")

    st.sidebar.title("Menú")

    if rol == "Administrador":
        menu = ["Panel Principal", "Admin de Datos", "Visualización", "Info Nacional", "Cerrar Sesión"]
    elif rol == "Usuario":
        menu = ["Panel Principal", "Visualización", "Info Nacional", "Cerrar Sesión"]
    else:
        menu = ["Panel Principal", "Info Nacional", "Cerrar Sesión"]

    opcion = st.sidebar.radio("Opciones", menu)

    if opcion == "Panel Principal":
        st.title("🛠️ Panel Principal")
        st.success(f"Bienvenido {st.session_state['usuario']} ({rol})")

    elif opcion == "Admin de Datos":
        admin_datos.app()

    elif opcion == "Visualización":
        visualizaciones.app()

    elif opcion == "Info Nacional":
        info_nacional.app()

    elif opcion == "Cerrar Sesión":
        st.session_state.autenticado = False
        st.session_state.usuario = ""
        st.session_state.rol = ""
        st.rerun()

