# dashboard/dashboard_app.py

# Panel de Streamlit para visualizar resultados de análisis de sentimientos y urgencias sobre reseñas de Amazon.


import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

# reports_dir es la carpeta donde guardamos los CSV (results_log.csv y alerts_log.csv).
# El try/except hace que funcione tanto si ejecutas desde el repositorio, como en el Colab.
try:
    from src.utils.config_rutas import reports_dir
except ModuleNotFoundError:
    import sys
    # añadimos a sys.path la carpeta src para poder importar utils/config_rutas.py
    sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
    from utils.config_rutas import reports_dir

# Rutas de los ficheros
RESULTS_CSV = reports_dir / "results_log.csv"   # reseñas procesadas (con ts, text, sentiment, urgency, aspects)
ALERTS_CSV  = reports_dir / "alerts_log.csv"    # alertas registradas 

# Estilo del dashboard
st.set_page_config(page_title="Panel de Análisis de Sentimientos", layout="wide")
PASTEL_BG   = "#F7F6FB"
PASTEL_H1   = "#5C5470"
PASTEL_H3   = "#7D8CA3"
PASTEL_LINE = "#E8E8F4"

# Fondo claro y títulos
st.markdown(f"<style>body {{ background-color: {PASTEL_BG}; }}</style>", unsafe_allow_html=True)
st.markdown(f"<h1 style='color:{PASTEL_H1};'>📊 Panel de Análisis de Sentimientos en Tiempo Real</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='color:{PASTEL_H3};'>Amazon Product Reviews – Celulares y Accesorios</h3>", unsafe_allow_html=True)
st.markdown(f"<hr style='border:1px solid {PASTEL_LINE};'/>", unsafe_allow_html=True)

#Funcion para leer el csv
def load_csv(path: Path) -> pd.DataFrame:
    """
    Lee un CSV si existe. Si no existe, devuelve un DataFrame vacío
    con las columnas que esperamos para evitar errores en el resto del código.
    """
    if not path.exists():
        return pd.DataFrame(columns=["ts", "text", "sentiment", "urgency", "aspects"])
    df = pd.read_csv(path)
    # Garantiza que siempre tengamos estas columnas
    for c in ["ts", "text", "sentiment", "urgency", "aspects"]:
        if c not in df.columns:
            df[c] = ""
    return df

# Cargamos los datos
results = load_csv(RESULTS_CSV)
alerts  = load_csv(ALERTS_CSV)

# Si está la columna ts (timestamp), la convertimos a datetime (con zona horaria UTC)
if "ts" in results.columns:
    results["ts"] = pd.to_datetime(results["ts"], errors="coerce", utc=True)

# Filtros del dashboard
# (1) Filtro por urgencia, (2) filtro por sentimiento, (3) slider para "N últimos"
c1, c2, c3 = st.columns([1, 1, 1.2])

with c1:
    urg_filter = st.multiselect(
        "Filtrar urgencia",
        ["low", "medium", "high"],
        default=["low", "medium", "high"]
    )

with c2:
    sent_filter = st.multiselect(
        "Filtrar sentimiento",
        ["positive", "neutral", "negative"],
        default=["positive", "neutral", "negative"]
    )

with c3:
    # Este N controla cuántas reseñas recientes mostramos (tras aplicar filtros)
    show_n = st.slider("Mostrar últimos N registros", 50, 5000, 500)
    # KPI global de alertas 
    st.metric("Alertas (global)", f"{len(alerts)}")

# si hay datos, se aplica los filtros correspondientes
if len(results):

    # Filtramos por urgencia y sentimiento (todo a minúsculas para evitar problemas de mayúsculas/minúsculas)
    df_filtered = results[
        results["urgency"].astype(str).str.lower().isin([u.lower() for u in urg_filter]) &
        results["sentiment"].astype(str).str.lower().isin([s.lower() for s in sent_filter])
    ].copy()

    # Ordenamos por tiempo y nos quedamos con los últimos N
    df_filtered = df_filtered.sort_values("ts").tail(show_n)

    # KPIs del rango actual (dependen de filtros y N) 
    total_rango    = len(df_filtered)
    neg_pct_rango  = (df_filtered["sentiment"].astype(str).str.lower().eq("negative").mean() * 100) if total_rango else 0.0
    high_pct_rango = (df_filtered["urgency"].astype(str).str.lower().eq("high").mean() * 100) if total_rango else 0.0

    k1, k2, k3 = st.columns(3)
    k1.metric("Reseñas (rango)", f"{total_rango}")
    k2.metric("% Negativas (rango)", f"{neg_pct_rango:.1f}%")
    k3.metric("% Urgencia alta (rango)", f"{high_pct_rango:.1f}%")

    # Aclaraciones para el usuario (qué significa "rango" y "global")
    a, b = st.columns([2, 3])
    with a:
        st.caption("**Rango** = aplica N y filtros superiores.")
    with b:
        st.caption("**Global** = total histórico en *alerts_log.csv* (no depende de N).")

    # Boxplot de distribución
    st.subheader("Distribución de sentimiento y urgencia")

    # Orden fijo para que las barras salgan siempre en el mismo orden
    order_sent = ["negative", "neutral", "positive"]
    order_urg  = ["low", "medium", "high"]

    # Conteos por sentimiento y urgencia
    sent_counts = (
        df_filtered.assign(sentiment=df_filtered["sentiment"].astype(str).str.lower())
        .groupby("sentiment").size().reindex(order_sent, fill_value=0).reset_index(name="count")
    )
    urg_counts = (
        df_filtered.assign(urgency=df_filtered["urgency"].astype(str).str.lower())
        .groupby("urgency").size().reindex(order_urg, fill_value=0).reset_index(name="count")
    )

    # Dos columnas: izquierda (sentimiento), derecha (urgencia)
    col1, col2 = st.columns(2)

    with col1:
        chart_sent = (
            alt.Chart(sent_counts)
            .mark_bar(color="#A5B4FC")
            .encode(
                x=alt.X("sentiment:N", title="Sentimiento", sort=order_sent),
                y=alt.Y("count:Q", title="Conteo"),
                tooltip=[
                    alt.Tooltip("sentiment:N", title="Sentimiento"),
                    alt.Tooltip("count:Q", title="Conteo"),
                ]
            )
            .properties(height=360)
        )
        st.altair_chart(chart_sent, use_container_width=True)

    with col2:
        chart_urg = (
            alt.Chart(urg_counts)
            .mark_bar(color="#FBC4AB")
            .encode(
                x=alt.X("urgency:N", title="Urgencia", sort=order_urg),
                y=alt.Y("count:Q", title="Conteo"),
                tooltip=[
                    alt.Tooltip("urgency:N", title="Urgencia"),
                    alt.Tooltip("count:Q", title="Conteo"),
                ]
            )
            .properties(height=360)
        )
        st.altair_chart(chart_urg, use_container_width=True)

    # heatmap entre urgencia y sentimiento
    st.subheader("Cruce urgencia × sentimiento")
    if total_rango:
        # Creamos todas las combinaciones urgencia×sentimiento aunque alguna no aparezca (relleno a 0)
        cross = (
            df_filtered.assign(
                urgency=df_filtered["urgency"].astype(str).str.lower(),
                sentiment=df_filtered["sentiment"].astype(str).str.lower()
            )
            .groupby(["urgency", "sentiment"]).size().reset_index(name="count")
        )
        full_idx = pd.MultiIndex.from_product([order_urg, order_sent], names=["urgency", "sentiment"])
        cross = cross.set_index(["urgency", "sentiment"]).reindex(full_idx, fill_value=0).reset_index()

        heat = (
            alt.Chart(cross)
            .mark_rect()
            .encode(
                y=alt.Y("urgency:N", title="Urgencia", sort=order_urg),
                x=alt.X("sentiment:N", title="Sentimiento", sort=order_sent),
                color=alt.Color("count:Q", title="Conteo"),
                tooltip=[
                    alt.Tooltip("urgency:N", title="Urgencia"),
                    alt.Tooltip("sentiment:N", title="Sentimiento"),
                    alt.Tooltip("count:Q", title="Conteo"),
                ],
            )
            .properties(height=260)
        )
        st.altair_chart(heat, use_container_width=True)
    else:
        st.info("No hay datos en el rango seleccionado para el cruce.")

    # barras apiladas para demostrar el nivel de urgencia en porcentaje
    st.subheader("Composición de sentimiento por nivel de urgencia (%)")
    if total_rango:
        stack_df = (
            df_filtered.assign(
                urgency=df_filtered["urgency"].astype(str).str.lower(),
                sentiment=df_filtered["sentiment"].astype(str).str.lower()
            )
            .groupby(["urgency", "sentiment"]).size().reset_index(name="count")
        )
        full_idx = pd.MultiIndex.from_product([order_urg, order_sent], names=["urgency", "sentiment"])
        stack_df = stack_df.set_index(["urgency", "sentiment"]).reindex(full_idx, fill_value=0).reset_index()

        stack_chart = (
            alt.Chart(stack_df)
            .mark_bar()
            .encode(
                x=alt.X("urgency:N", title="Urgencia", sort=order_urg),
                # stack="normalize" hace que el eje Y sea porcentaje (100%)
                y=alt.Y("count:Q", stack="normalize", title="%"),
                color=alt.Color(
                    "sentiment:N", title="Sentimiento", sort=order_sent,
                    # Colores suaves (rojo suave, gris claro, verde suave)
                    scale=alt.Scale(range=["#FCA5A5", "#E5E7EB", "#A7F3D0"])
                ),
                tooltip=[
                    alt.Tooltip("urgency:N", title="Urgencia"),
                    alt.Tooltip("sentiment:N", title="Sentimiento"),
                    alt.Tooltip("count:Q", title="Conteo"),
                ],
            )
            .properties(height=280)
        )
        st.altair_chart(stack_chart, use_container_width=True)
    else:
        st.info("No hay datos en el rango seleccionado para la composición.")

    # tabla de los ultimos resultados
    st.subheader("Últimos resultados")
    table = df_filtered.copy()

    # Si hay timestamps válidos, los convertimos a hora local 
    if "ts" in table.columns and table["ts"].notna().sum() > 0:
        table["Fecha/Hora"] = table["ts"].dt.tz_convert("America/Guayaquil").dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        table["Fecha/Hora"] = ""

    # Renombramos columnas al español y mostramos lo más útil
    table = table[["Fecha/Hora", "sentiment", "urgency", "aspects", "text"]].rename(columns={
        "sentiment": "Sentimiento",
        "urgency":   "Urgencia",
        "aspects":   "Aspectos",
        "text":      "Texto",
    })
    st.dataframe(table, use_container_width=True)

# Si no hay datos todavía, avisamos al usuario cómo generarlos
else:
    st.warning("Aún no hay datos en results_log.csv. Usa la API /predict o /batch para generar datos.")
