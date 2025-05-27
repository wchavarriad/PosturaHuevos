import streamlit as st

# Base de datos simulada de usuarios
USUARIOS = {
    "admin": {"password": "1234", "rol": "Administrador"},
    "usuario1": {"password": "abcd", "rol": "Usuario"},
    "invitado": {"password": "0000", "rol": "Invitado"},
}

# Función para validar credenciales
def validar_usuario(usuario, contraseña):
    return usuario in USUARIOS and USUARIOS[usuario]["password"] == contraseña

# Inicializar sesión
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""
if "rol" not in st.session_state:
    st.session_state.rol = ""

# Página de login
if not st.session_state.autenticado:
    st.set_page_config(page_title="Control de Accesos", layout="centered")
    st.title("🔐 Sistema de Control de Accesos")

    with st.form("login_form"):
        st.subheader("Iniciar Sesión")
        usuario = st.text_input("Usuario")
        contraseña = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Acceder")

    if submit:
        if validar_usuario(usuario, contraseña):
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
            st.session_state.rol = USUARIOS[usuario]["rol"]
            st.success("Inicio de sesión exitoso. Redirigiendo...")
            st.rerun()  # ✅ USAR rerun correcto
        else:
            st.error("Credenciales incorrectas.")

# Página principal después del login
else:
    st.set_page_config(page_title="Panel de Usuario", layout="wide")
    st.sidebar.title("Menú")
    st.sidebar.success(f"Sesión: {st.session_state.usuario} ({st.session_state.rol})")
    opcion = st.sidebar.radio("Opciones", ["Panel Principal", "Crear Funciones", "Cerrar Sesión"])

    if opcion == "Panel Principal":
        st.title("🛠️ Panel Principal")
        if st.session_state.rol == "Administrador":
            st.info("Tienes acceso completo a todas las herramientas.")
            st.write("Aquí podrías agregar gestión de usuarios, auditoría, etc.")
        elif st.session_state.rol == "Usuario":
            st.info("Tienes acceso limitado a ciertas herramientas.")
            st.write("Visualización de reportes, acceso a funciones permitidas.")
        else:
            st.warning("Tu acceso es restringido.")
            st.write("Consulta con el administrador para más permisos.")

    elif opcion == "Crear Funciones":
        st.title("🧪 Ejecutar Función Personalizada")
        st.markdown("""
        Escribe una función en Python y ejecútala.
        Por ejemplo:
        ```python
        def mi_funcion():
            return 2 + 2
        ```
        """)

        codigo = st.text_area("Código de la función:", height=200)
        ejecutar = st.button("Ejecutar función")

        if ejecutar:
            try:
                exec(codigo, globals())  # define la función en el entorno global
                nombre_funcion = codigo.strip().split("(")[0].replace("def", "").strip()
                resultado = eval(f"{nombre_funcion}()")
                st.success(f"✅ Resultado de `{nombre_funcion}()`: `{resultado}`")
            except Exception as e:
                st.error(f"❌ Error al ejecutar la función: {e}")

    elif opcion == "Cerrar Sesión":
        st.session_state.autenticado = False
        st.session_state.usuario = ""
        st.session_state.rol = ""
        st.rerun()
