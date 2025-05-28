import streamlit as st
import altair as alt
from utils.helpers import cargar_datos

def app():
    st.title("📊 Visualización de Producción")
    df = cargar_datos()

    st.altair_chart(
        alt.Chart(df).mark_line(point=True).encode(
            x='Fecha:T',
            y='Total Calculado (#1+#2+#3+Pollitas):Q',
            tooltip=['Fecha', 'Total Calculado (#1+#2+#3+Pollitas)']
        ).properties(title="Total Calculado"), use_container_width=True
    )

    st.altair_chart(
        alt.Chart(df).mark_line(strokeDash=[4,2], color='red').encode(
            x='Fecha:T',
            y='Total (Manuscrito):Q'
        ).properties(title="Total Manuscrito"), use_container_width=True
    )
