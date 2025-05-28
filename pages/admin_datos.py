import streamlit as st
import pandas as pd
from utils.helpers import cargar_datos

def app():
    st.title("🗃️ Admin de Datos (solo Admin)")
    df = cargar_datos()
    st.dataframe(df, use_container_width=True)
    st.info("Funcionalidad de edición, adición y eliminación se implementa aquí.")
