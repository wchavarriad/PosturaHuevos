import streamlit as st
import pandas as pd

# --- Base de datos de usuarios ---
USUARIOS = {
    "admin": {"password": "1234", "rol": "Administrador"},
    "usuario1": {"password": "abcd", "rol": "Usuario"},
    "invitado": {"password": "0000", "rol": "Invitado"},
}

# --- Validación de credenciales ---
def validar_usuario(usuario, contraseña):
    return usuario in USUARIOS and USUARIOS[usuario]["password"] == contraseña

# --- Cargar CSV y convertir Fecha ---
@st.cache_data(ttl=0)
def cargar_datos():
    try:
        df = pd.read_csv("FuentesDatos/control_produccion_huevos_actualizado.csv")
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
        df = df.sort_values("Fecha").reset_index(drop=True)
        return df
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo CSV.")
        return pd.DataFrame()

# --- Inicializar sesión ---
for key in ["autenticado", "usuario", "rol", "accion"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "autenticado" else ""

# --- Login ---
if not st.session_state.autenticado:
    st.set_page_config(page_title="Control de Accesos", layout="centered")
    st.title("🔐 Sistema de Control de Accesos")

    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        contraseña = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Acceder"):
            if validar_usuario(usuario, contraseña):
                st.session_state.autenticado = True
                st.session_state.usuario = usuario
                st.session_state.rol = USUARIOS[usuario]["rol"]
                st.success("Inicio de sesión exitoso. Redirigiendo...")
                st.rerun()
            else:
                st.error("Credenciales incorrectas.")

# --- Panel después del login ---
else:
    st.set_page_config(page_title="Panel de Usuario", layout="wide")
    st.sidebar.title("Menú")
    st.sidebar.success(f"Sesión: {st.session_state.usuario} ({st.session_state.rol})")

    opcion = st.sidebar.radio("Opciones", ["Panel Principal", "📋 Ver Tabla de Producción", "Crear Funciones", "Cerrar Sesión"])

    if opcion == "Panel Principal":
        st.title("🛠️ Panel Principal")
        if st.session_state.rol == "Administrador":
            st.info("Tienes acceso completo a todas las funciones.")
        else:
            st.info("Tienes acceso limitado al sistema.")

    elif opcion == "📋 Ver Tabla de Producción":
        st.title("📊 Tabla de Producción de Huevos")
        df = cargar_datos()

        if df.empty:
            st.warning("No hay datos para mostrar.")
        else:
            st.dataframe(df, use_container_width=True)

            st.markdown("---")
            st.subheader("🧰 Acciones sobre la tabla")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("➕ Agregar fila"):
                    st.session_state.accion = "agregar"
            with col2:
                if st.button("✏️ Editar fila"):
                    st.session_state.accion = "editar"
            with col3:
                if st.button("🗑️ Eliminar fila"):
                    st.session_state.accion = "eliminar"

            # AGREGAR
            if st.session_state.accion == "agregar":
                with st.expander("➕ Agregar nuevo registro", expanded=True):
                    nueva_fecha = pd.to_datetime(st.date_input("Fecha"))
                    columnas = ['#1', '#2', '#3', 'Quebrados', 'Pollitas']
                    nuevo = {col: st.number_input(f"{col}:", value=0, key=f"nuevo_{col}") for col in columnas}
                    total_manu = st.text_input("Total (Manuscrito):", key="nuevo_total_manu")

                    if st.button("Guardar nueva fila"):
                        if nueva_fecha in df["Fecha"].values:
                            st.error("Ya existe un registro con esa fecha.")
                        else:
                            nuevo_df = pd.DataFrame([{
                                "Fecha": nueva_fecha,
                                **nuevo,
                                "Total (Manuscrito)": total_manu
                            }])
                            nuevo_df["Total Calculado (#1+#2+#3+Pollitas)"] = (
                                nuevo_df['#1'] + nuevo_df['#2'] + nuevo_df['#3'] + nuevo_df['Pollitas']
                            )
                            nuevo_df["% Quebrado"] = (
                                (nuevo_df["Quebrados"] / nuevo_df["Total Calculado (#1+#2+#3+Pollitas)"]) * 100
                            ).round(2).astype(str) + '%'

                            df = pd.concat([df, nuevo_df], ignore_index=True)
                            df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
                            df = df.sort_values("Fecha")
                            df["Fecha"] = df["Fecha"].dt.strftime("%Y-%m-%d")
                            df.to_csv("FuentesDatos/control_produccion_huevos_actualizado.csv", index=False)

                            st.success("✅ Fila agregada correctamente.")
                            st.cache_data.clear()  # <- BORRAR CACHÉ
                            st.session_state.accion = None
                            st.rerun()

            # EDITAR
            elif st.session_state.accion == "editar":
                with st.expander("✏️ Editar registro existente", expanded=True):
                    fechas_opciones = df["Fecha"].dt.strftime("%Y-%m-%d")
                    fecha_editar_str = st.selectbox("Selecciona la fecha", fechas_opciones)
                    fila = df[df["Fecha"].dt.strftime("%Y-%m-%d") == fecha_editar_str].iloc[0]
                    columnas = ['#1', '#2', '#3', 'Quebrados', 'Pollitas']
                    nuevos = {col: st.number_input(f"{col}:", value=int(fila[col]), key=f"editar_{col}") for col in columnas}
                    total_manu = st.text_input("Total (Manuscrito):", value=str(fila["Total (Manuscrito)"]), key="editar_total_manu")

                    if st.button("Guardar cambios"):
                        idx = df[df["Fecha"].dt.strftime("%Y-%m-%d") == fecha_editar_str].index[0]
                        for col in columnas:
                            df.at[idx, col] = nuevos[col]
                        df.at[idx, "Total (Manuscrito)"] = total_manu
                        df["Total Calculado (#1+#2+#3+Pollitas)"] = df["#1"] + df["#2"] + df["#3"] + df["Pollitas"]
                        df["% Quebrado"] = ((df["Quebrados"] / df["Total Calculado (#1+#2+#3+Pollitas)"]) * 100).round(2).astype(str) + '%'

                        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
                        df = df.sort_values("Fecha")
                        df["Fecha"] = df["Fecha"].dt.strftime("%Y-%m-%d")
                        df.to_csv("FuentesDatos/control_produccion_huevos_actualizado.csv", index=False)

                        st.success("✅ Registro actualizado.")
                        st.cache_data.clear()
                        st.session_state.accion = None
                        st.rerun()

            # ELIMINAR
            elif st.session_state.accion == "eliminar":
                with st.expander("🗑️ Eliminar registro", expanded=True):
                    fechas_opciones = df["Fecha"].dt.strftime("%Y-%m-%d")
                    fecha_eliminar_str = st.selectbox("Fecha a eliminar", fechas_opciones)
                    if st.button("Eliminar"):
                        df = df[df["Fecha"].dt.strftime("%Y-%m-%d") != fecha_eliminar_str]
                        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
                        df = df.sort_values("Fecha")
                        df["Fecha"] = df["Fecha"].dt.strftime("%Y-%m-%d")
                        df.to_csv("FuentesDatos/control_produccion_huevos_actualizado.csv", index=False)

                        st.success(f"✅ Registro del {fecha_eliminar_str} eliminado.")
                        st.cache_data.clear()
                        st.session_state.accion = None
                        st.rerun()

    elif opcion == "Crear Funciones":
        st.title("🧪 Ejecutar Función Personalizada")
        st.markdown("Escribe una función en Python y ejecútala:")
        st.code("def mi_funcion():\n    return 2 + 2")
        codigo = st.text_area("Código de la función:", height=200)
        if st.button("Ejecutar función"):
            try:
                exec(codigo, globals())
                nombre_funcion = codigo.strip().split("(")[0].replace("def", "").strip()
                resultado = eval(f"{nombre_funcion}()")
                st.success(f"✅ Resultado: `{resultado}`")
            except Exception as e:
                st.error(f"❌ Error: {e}")

    elif opcion == "Cerrar Sesión":
        st.session_state.autenticado = False
        st.session_state.usuario = ""
        st.session_state.rol = ""
        st.rerun()
