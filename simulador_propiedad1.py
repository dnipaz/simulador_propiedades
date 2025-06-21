import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit.components.v1 import html

# Cargar datos de propiedades
df = pd.read_csv("propiedades_antofagasta.csv")

st.set_page_config(page_title="Simulador de Compra de Propiedades", layout="wide")

st.title("🏡 Simulador de Compra de Propiedades en Antofagasta")

with st.sidebar:
    st.header("💸 Parámetros de simulación")
    sueldo = st.number_input("Tu sueldo mensual (CLP)", value=1000000, step=50000)
    años = st.slider("Años para pagar la propiedad", 5, 30, 20)
    tasa_interes = st.slider("Tasa de interés anual (%)", 1.0, 10.0, 4.5)

def calcular_cuota(precio, años, tasa):
    n = años * 12
    r = tasa / 100 / 12
    cuota = (precio * r) / (1 - (1 + r) ** -n)
    return cuota

df["Cuota estimada"] = df["Precio"].apply(lambda x: calcular_cuota(x, años, tasa_interes))

# Clasificar si puede comprar o no
df["¿Puedes comprar?"] = df["Cuota estimada"].apply(lambda c: "✅ Sí" if c <= sueldo * 0.3 else "❌ No")

st.subheader("📊 Resultados de simulación:")
st.dataframe(df[["Nombre", "Precio", "Cuota estimada", "¿Puedes comprar?"]])

df_aprobadas = df[df["¿Puedes comprar?"] == "✅ Sí"]

st.markdown("### 📍 Propiedades que puedes pagar:")
if df_aprobadas.empty:
    st.warning("No hay propiedades que puedas pagar con los parámetros actuales.")
else:
    st.success(f"{len(df_aprobadas)} propiedades disponibles dentro de tu presupuesto.")

    mapa = folium.Map(location=[-23.65, -70.4], zoom_start=12)
    cluster = MarkerCluster().add_to(mapa)

    for _, row in df_aprobadas.iterrows():
        popup = f"<strong>{row['Nombre']}</strong><br>Precio: ${int(row['Precio']):,}<br>Cuota: ${int(row['Cuota estimada']):,}<br><a href='{row['Enlace']}' target='_blank'>Ver más</a>"
        folium.Marker(location=[row["Latitud"], row["Longitud"]], popup=popup).add_to(cluster)

    html(mapa._repr_html_(), height=500)

st.markdown("### 📈 Distribución de precios de propiedades")
st.bar_chart(df["Precio"])

