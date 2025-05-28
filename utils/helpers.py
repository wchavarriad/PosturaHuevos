import pandas as pd

def cargar_datos():
    df = pd.read_csv("data/control_produccion_huevos_actualizado.csv")
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Total (Manuscrito)"] = df["Total (Manuscrito)"].astype(str).str.replace(",", "").astype(float)
    return df.sort_values("Fecha").reset_index(drop=True)
