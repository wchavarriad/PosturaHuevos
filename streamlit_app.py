import streamlit as st
import pandas as pd
import altair as alt

# --- Base de datos de usuarios ---
USUARIOS = {
    "admin": {"password": "1234", "rol": "Administrador"},
    "usuario1": {"password": "abcd", "rol": "Usuario"},
    "invitado": {"password": "0000", "rol": "Invitado"},
}

# --- Validación de credenciales ---
def validar_usuario(usuario, contraseña):
    return usuario in USUARIOS and USUARIOS[usuario]["password"] == contraseña

# --- Cargar CSV y convertir columnas ---
@st.cache_data(ttl=0)
def cargar_datos():
    try:
        df = pd.read_csv("FuentesDatos/control_produccion_huevos_actualizado.csv")
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
        df["Total (Manuscrito)"] = df["Total (Manuscrito)"].astype(str).str.replace(",", "").astype(float)
        df["% Quebrado"] = df["% Quebrado"].astype(str).str.replace("%", "").astype(float)
        return df.sort_values("Fecha").reset_index(drop=True)
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

    rol = st.session_state.rol
    if rol == "Administrador":
        menu = ["Panel Principal", "🗃️ Admin de Datos", "📊 Visualización de Datos", "Crear Funciones", "🌍 Info Nacional", "Cerrar Sesión"]
    elif rol == "Usuario":
        menu = ["Panel Principal", "📊 Visualización de Datos", "🌍 Info Nacional", "Cerrar Sesión"]
    else:
        menu = ["Panel Principal", "🌍 Info Nacional", "Cerrar Sesión"]

    opcion = st.sidebar.radio("Opciones", menu)

    # Panel Principal
    if opcion == "Panel Principal":
        st.title("🛠️ Panel Principal")
        st.info(f"Rol actual: {rol}")

    # Admin de Datos (solo Admin)
    elif opcion == "🗃️ Admin de Datos":
        if rol != "Administrador":
            st.warning("⚠️ Acceso restringido a administradores.")
        else:
            st.title("🗃️ Administración de Datos de Producción")
            df = cargar_datos()
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

            # Agregar
            if st.session_state.accion == "agregar":
                with st.expander("➕ Agregar nuevo registro", expanded=True):
                    nueva_fecha = pd.to_datetime(st.date_input("Fecha"))
                    campos = ['#1', '#2', '#3', 'Quebrados', 'Pollitas']
                    datos = {c: st.number_input(f"{c}:", value=0, key=f"nuevo_{c}") for c in campos}
                    total_manu = st.number_input("Total (Manuscrito):", value=0, key="nuevo_total_manu")

                    if st.button("Guardar nueva fila"):
                        if nueva_fecha in df["Fecha"].values:
                            st.error("Ya existe un registro con esa fecha.")
                        else:
                            nuevo = pd.DataFrame([{
                                "Fecha": nueva_fecha,
                                **datos,
                                "Total (Manuscrito)": total_manu,
                            }])
                            nuevo["Total Calculado (#1+#2+#3+Pollitas)"] = (
                                nuevo['#1'] + nuevo['#2'] + nuevo['#3'] + nuevo['Pollitas']
                            )
                            nuevo["% Quebrado"] = ((nuevo["Quebrados"] / nuevo["Total Calculado (#1+#2+#3+Pollitas)"]) * 100).round(2)
                            df = pd.concat([df, nuevo], ignore_index=True).sort_values("Fecha")
                            df.to_csv("FuentesDatos/control_produccion_huevos_actualizado.csv", index=False)
                            st.success("✅ Fila agregada.")
                            st.cache_data.clear()
                            st.session_state.accion = None
                            st.rerun()

            # Editar
            elif st.session_state.accion == "editar":
                with st.expander("✏️ Editar registro existente", expanded=True):
                    fechas = df["Fecha"].dt.strftime("%Y-%m-%d")
                    fecha_sel = st.selectbox("Selecciona fecha", fechas)
                    fila = df[df["Fecha"].dt.strftime("%Y-%m-%d") == fecha_sel].iloc[0]
                    campos = ['#1', '#2', '#3', 'Quebrados', 'Pollitas']
                    nuevos = {c: st.number_input(f"{c}:", value=int(fila[c]), key=f"editar_{c}") for c in campos}
                    total_manu = st.number_input("Total (Manuscrito):", value=int(fila["Total (Manuscrito)"]))

                    if st.button("Guardar cambios"):
                        idx = df[df["Fecha"].dt.strftime("%Y-%m-%d") == fecha_sel].index[0]
                        for c in campos:
                            df.at[idx, c] = nuevos[c]
                        df.at[idx, "Total (Manuscrito)"] = total_manu
                        df["Total Calculado (#1+#2+#3+Pollitas)"] = df["#1"] + df["#2"] + df["#3"] + df["Pollitas"]
                        df["% Quebrado"] = (df["Quebrados"] / df["Total Calculado (#1+#2+#3+Pollitas)"] * 100).round(2)
                        df.to_csv("FuentesDatos/control_produccion_huevos_actualizado.csv", index=False)
                        st.success("✅ Registro actualizado.")
                        st.cache_data.clear()
                        st.session_state.accion = None
                        st.rerun()

            # Eliminar
            elif st.session_state.accion == "eliminar":
                with st.expander("🗑️ Eliminar registro", expanded=True):
                    fechas = df["Fecha"].dt.strftime("%Y-%m-%d")
                    fecha_sel = st.selectbox("Fecha a eliminar", fechas)
                    if st.button("Eliminar"):
                        df = df[df["Fecha"].dt.strftime("%Y-%m-%d") != fecha_sel]
                        df.to_csv("FuentesDatos/control_produccion_huevos_actualizado.csv", index=False)
                        st.success(f"✅ Registro del {fecha_sel} eliminado.")
                        st.cache_data.clear()
                        st.session_state.accion = None
                        st.rerun()

    # Visualización de datos
    elif opcion == "📊 Visualización de Datos":
        if rol not in ["Administrador", "Usuario"]:
            st.warning("⚠️ Esta vista es solo para usuarios autenticados.")
        else:
            st.title("📊 Producción de Huevos - Visualización")
            df = cargar_datos()

            if df.empty:
                st.warning("No hay datos disponibles.")
            else:
                st.dataframe(df, use_container_width=True)
                if st.button("🔄 Actualizar datos"):
                    st.cache_data.clear()
                    st.rerun()

                df["Día"] = df["Fecha"].dt.day
                df["Mes"] = df["Fecha"].dt.month_name()
                df["DíaSemana"] = df["Fecha"].dt.day_name()

                # Línea: Total Calculado vs Manuscrito
                st.markdown("### 📈 Total Calculado vs Manuscrito")
                c1 = alt.Chart(df).mark_line(point=True, color='blue').encode(
                    x='Fecha:T', y='Total Calculado (#1+#2+#3+Pollitas):Q'
                )
                c2 = alt.Chart(df).mark_line(strokeDash=[5,5], color='red').encode(
                    x='Fecha:T', y='Total (Manuscrito):Q'
                )
                st.altair_chart(c1 + c2, use_container_width=True)

                # Línea: % Quebrado
                st.markdown("### 📉 % de Huevos Quebrados")
                st.altair_chart(alt.Chart(df).mark_line().encode(
                    x='Fecha:T', y='% Quebrado:Q'
                ), use_container_width=True)

                # Línea: por galpón
                st.markdown("### 🐔 Producción por Galpón")
                long = df.melt(id_vars='Fecha', value_vars=['#1', '#2', '#3', 'Pollitas'],
                               var_name='Galpón', value_name='Producción')
                st.altair_chart(alt.Chart(long).mark_line().encode(
                    x='Fecha:T', y='Producción:Q', color='Galpón:N'
                ), use_container_width=True)

                # Dispersión: Producción vs Quebrados
                st.markdown("### 🧮 Relación Producción vs Quebrados")
                st.altair_chart(alt.Chart(df).mark_circle(size=60).encode(
                    x='Total Calculado (#1+#2+#3+Pollitas):Q', y='Quebrados:Q'
                ).interactive(), use_container_width=True)

                # Mapa calor
                st.markdown("### 🔥 Mapa de Calor por Día")
                st.altair_chart(alt.Chart(df).mark_rect().encode(
                    x='Día:O', y='Mes:N', color='Total Calculado (#1+#2+#3+Pollitas):Q'
                ), use_container_width=True)

                # Pie: total por galpón
                st.markdown("### 📊 Total por Galpón")
                galp = df[['#1', '#2', '#3', 'Pollitas']].sum().reset_index()
                galp.columns = ['Galpón', 'Producción']
                st.altair_chart(alt.Chart(galp).mark_arc().encode(
                    theta='Producción:Q', color='Galpón:N'
                ), use_container_width=True)

                # Barras: por día de semana
                st.markdown("### 📅 Producción por Día de la Semana")
                st.altair_chart(alt.Chart(df).mark_bar().encode(
                    x=alt.X('DíaSemana:N', sort=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']),
                    y='sum(Total Calculado (#1+#2+#3+Pollitas)):Q'
                ), use_container_width=True)

    # Info Nacional
    elif opcion == "🌍 Info Nacional":
        st.title("🇨🇷 Producción de Huevos en Costa Rica")
        st.markdown("""
        - 🐔 En Costa Rica se producen más de **1.6 mil millones de huevos** al año.
        - 🍳 El consumo per cápita es de aproximadamente **230 huevos por persona**.
        - 📍 Zonas clave: **Alajuela, San Carlos, Cartago**.
        - 🌱 La avicultura es vital para la seguridad alimentaria nacional.
        - 📊 Fuente: [MAG](https://www.mag.go.cr) | [INEC](https://www.inec.cr)
        """)
        st.image("https://www.mag.go.cr/sites/default/files/styles/large/public/media/image/produccion-huevos-cr.jpg", use_column_width=True)

    # Crear funciones
    elif opcion == "Crear Funciones":
        st.title("🧪 Ejecutar Función Personalizada")
        codigo = st.text_area("Código de la función:", height=200)
        if st.button("Ejecutar función"):
            try:
                exec(codigo, globals())
                nombre_funcion = codigo.strip().split("(")[0].replace("def", "").strip()
                resultado = eval(f"{nombre_funcion}()")
                st.success(f"✅ Resultado: `{resultado}`")
            except Exception as e:
                st.error(f"❌ Error: {e}")

    # Cerrar sesión
    elif opcion == "Cerrar Sesión":
        for key in ["autenticado", "usuario", "rol", "accion"]:
            st.session_state[key] = False if key == "autenticado" else ""
        st.rerun()

