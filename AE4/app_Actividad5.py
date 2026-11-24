"""
AE4 (Actividad 5) - Aplicacion Streamlit: cancelacion de clientes Telco.

Ejecutar desde la raiz del repositorio:
    streamlit run AE4/app_Actividad5.py

Usa los datos preparados y las tablas de resultados de AE3.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
DATASET = RAIZ / "AE3" / "datos" / "telco_churn_preparado_Actividad4.csv"
TABLAS = RAIZ / "AE3" / "resultados" / "tablas"

AZUL, ROJO, GRIS = "#1F3A5F", "#C8553D", "#9AA5B1"
COLOR_CANCELO = {"No": AZUL, "Sí": ROJO}
PERIODO = "Corte transversal (sin fechas). Cancelación = retiro en el «último mes» (no documentado)."

st.set_page_config(page_title="Cancelación de clientes Telco", page_icon="📉", layout="wide")


# ---------------------------------------------------------------- datos
@st.cache_data
def cargar():
    df = pd.read_csv(DATASET)
    tablas = {p.stem.replace("_Actividad4", ""): pd.read_csv(p) for p in TABLAS.glob("*_Actividad4.csv")}
    return df, tablas


df, T = cargar()
TASA_GLOBAL = df["cancelo_flag"].mean() * 100


def fmt(x, dec=2):
    return f"{x:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def tasa_por(columna, datos=df):
    """Recalcula la tasa desde el dataset preparado (misma formula del notebook)."""
    g = (datos.groupby(columna).agg(clientes=("id_cliente", "count"), cancelaciones=("cancelo_flag", "sum"),
                                    cargo_mensual_perdido=("cargo_mensual_perdido", "sum")).reset_index())
    g["tasa_cancelacion_pct"] = g["cancelaciones"] / g["clientes"] * 100
    g["participacion_cancelaciones_pct"] = g["cancelaciones"] / datos["cancelo_flag"].sum() * 100
    return g


def grafico_tasa(tabla, titulo, eje_y="Segmento", orden=None, horizontal=False):
    """Barras de tasa de cancelacion (%) con linea de la tasa global."""
    t = tabla.copy()
    t["etiqueta"] = t["tasa_cancelacion_pct"].map(lambda v: f"{fmt(v)} %")
    t["color"] = t["tasa_cancelacion_pct"].gt(TASA_GLOBAL).map({True: ROJO, False: AZUL})
    if orden:
        t["segmento"] = pd.Categorical(t["segmento"], orden, ordered=True)
        t = t.sort_values("segmento")
    custom = t[["clientes", "cancelaciones", "participacion_cancelaciones_pct"]]
    hover = ("<b>%{" + ("y" if horizontal else "x") + "}</b><br>Tasa: %{" + ("x" if horizontal else "y")
             + ":.2f} %<br>Clientes: %{customdata[0]:,}<br>Cancelaciones: %{customdata[1]:,}"
               "<br>% del total de cancelaciones: %{customdata[2]:.2f} %<extra></extra>")
    if horizontal:
        fig = go.Figure(go.Bar(y=t["segmento"].astype(str), x=t["tasa_cancelacion_pct"], orientation="h",
                               marker_color=t["color"], text=t["etiqueta"], textposition="outside",
                               customdata=custom, hovertemplate=hover))
        fig.add_vline(x=TASA_GLOBAL, line_dash="dash", line_color=GRIS,
                      annotation_text=f"Global {fmt(TASA_GLOBAL)} %", annotation_position="top")
        fig.update_layout(xaxis_title="Tasa de cancelación (%)", yaxis_title=eje_y,
                          yaxis=dict(autorange="reversed"),
                          xaxis=dict(range=[0, t["tasa_cancelacion_pct"].max() * 1.15]))
    else:
        fig = go.Figure(go.Bar(x=t["segmento"].astype(str), y=t["tasa_cancelacion_pct"], marker_color=t["color"],
                               text=t["etiqueta"], textposition="outside", customdata=custom, hovertemplate=hover))
        fig.add_hline(y=TASA_GLOBAL, line_dash="dash", line_color=GRIS,
                      annotation_text=f"Tasa global {fmt(TASA_GLOBAL)} %", annotation_position="top left")
        fig.update_layout(yaxis_title="Tasa de cancelación (%)", xaxis_title=eje_y)
    fig.update_layout(title=titulo, height=420, margin=dict(t=60, b=40, l=10, r=10), showlegend=False,
                      plot_bgcolor="white")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#EEE")
    return fig


def metrica(definicion, calculo, unidad):
    with st.expander("📐 Métrica utilizada: definición, cálculo y unidad", expanded=False):
        st.markdown(f"- **Métrica:** {definicion}\n- **Cálculo:** {calculo}\n- **Unidad:** {unidad}\n"
                    f"- **Periodo:** {PERIODO}")


def interpretacion(muestra, responde, decision, limitacion):
    c1, c2 = st.columns(2)
    c1.markdown(f"**🔎 Qué muestran los datos**\n\n{muestra}")
    c1.markdown(f"**✅ Respuesta a la pregunta**\n\n{responde}")
    c2.success(f"**Decisión que puede apoyar:** {decision}")
    c2.warning(f"**Limitación:** {limitacion}")


def tabla_detalle(tabla, columnas=None):
    with st.expander("📋 Ver tabla de resultados (AE3)"):
        st.dataframe(tabla if columnas is None else tabla[columnas], hide_index=True, width="stretch")


TASA_DEF = ("Tasa de cancelación", "clientes que cancelaron ÷ clientes del segmento × 100", "porcentaje (%)")

# ---------------------------------------------------------------- navegacion
SECCIONES = ["🏠 Inicio: necesidad y datos", "P0 · Tasa global", "P1 · Condiciones de la cuenta",
             "P2 · Antigüedad", "P3 · Servicios contratados", "P4 · Perfil demográfico",
             "P5 · Cargos", "P6 · Segmentos críticos", "🧭 Conclusiones y recomendaciones"]
st.sidebar.title("📉 Cancelación de clientes")
seccion = st.sidebar.radio("Ir a la sección", SECCIONES, label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.caption("Proyecto integrador · Analítica de Datos\n\nDiego Mauricio Bedoya Valencia\n\n"
                   "IU Digital de Antioquia · 2026")
st.sidebar.caption(f"Datos: `{DATASET.relative_to(RAIZ).as_posix()}` ({fmt(len(df), 0)} filas × {df.shape[1]} columnas)")

# ================================================================ INICIO
if seccion == SECCIONES[0]:
    st.title("Caracterización de la cancelación de clientes en una empresa de telecomunicaciones")
    st.caption("Proyecto integrador · AE4 · Métricas y visualización")
    c = st.columns(4)
    c[0].metric("Clientes analizados", fmt(len(df), 0))
    c[1].metric("Cancelaron", fmt(df["cancelo_flag"].sum(), 0))
    c[2].metric("Tasa global de cancelación", f"{fmt(TASA_GLOBAL)} %")
    c[3].metric("Cargo mensual perdido (u.m./mes)", fmt(df['cargo_mensual_perdido'].sum(), 0))

    st.subheader("Necesidad")
    st.markdown("El **equipo de retención** de la compañía necesita saber **en qué grupos de clientes se concentra "
                "la cancelación**, para dejar de dirigir sus campañas a toda la base por igual y priorizar los "
                "segmentos de mayor riesgo.")
    st.subheader("Preguntas de negocio")
    st.table(pd.DataFrame({
        "Pregunta": ["P0", "P1", "P2", "P3", "P4", "P5", "P6"],
        "Descripción": ["¿Cuál es la tasa global de cancelación? (línea base)",
                        "¿Cómo varía la tasa según las condiciones de la cuenta (contrato, pago, factura)?",
                        "¿Cómo varía la tasa según la antigüedad del cliente?",
                        "¿Cómo varía la tasa según los servicios contratados?",
                        "¿Cómo varía la tasa según el perfil demográfico?",
                        "¿Cómo se diferencian los cargos de quienes cancelan y quienes permanecen?",
                        "¿Qué segmentos combinados tienen las tasas más altas y cuánto ingreso concentran?"]}).set_index("Pregunta"))
    st.subheader("Dataset")
    st.markdown(
        "| Dato | Valor |\n|---|---|\n"
        "| Nombre | Telco Customer Churn (IBM Sample Dataset) |\n"
        "| Fuente | Hugging Face · `scikit-learn/churn-prediction` (licencia CC BY 4.0) |\n"
        "| Unidad de análisis | El cliente (una fila por cliente) |\n"
        f"| Tamaño | {fmt(len(df), 0)} clientes · 21 variables originales + 9 creadas en AE3 |\n"
        "| Naturaleza | Datos **ficticios** de una compañía inventada por IBM |\n"
        "| Periodo | Corte transversal sin fechas |")
    st.info("Usa el menú de la izquierda para recorrer las preguntas P0 a P6 y las conclusiones.")

# ================================================================ P0
elif seccion == SECCIONES[1]:
    st.header("P0 · ¿Cuál es la tasa global de cancelación?")
    p0 = T["P0_tasa_global"]
    si, no = p0.set_index("cancelo").loc["Sí"], p0.set_index("cancelo").loc["No"]
    c = st.columns(4)
    c[0].metric("Tasa global", f"{fmt(si.participacion_clientes_pct)} %")
    c[1].metric("Clientes que cancelaron", fmt(si.clientes, 0))
    c[2].metric("Cargo mensual perdido (u.m./mes)", fmt(si.cargo_mensual_total, 0))
    c[3].metric("% de la facturación mensual", f"{fmt(si.participacion_cargo_mensual_pct)} %")
    metrica("Tasa global de cancelación y participación en el cargo mensual",
            "clientes con cancelo = Sí ÷ 7.043 × 100; cargo mensual de quienes cancelaron ÷ cargo mensual total × 100",
            "porcentaje (%) y unidades monetarias por mes (u.m./mes; moneda no documentada)")
    comp = pd.DataFrame({"Medida": ["% de clientes", "% de clientes", "% del cargo mensual", "% del cargo mensual"],
                         "Canceló": ["No", "Sí", "No", "Sí"],
                         "Porcentaje": [no.participacion_clientes_pct, si.participacion_clientes_pct,
                                        no.participacion_cargo_mensual_pct, si.participacion_cargo_mensual_pct]})
    fig = px.bar(comp, x="Medida", y="Porcentaje", color="Canceló", color_discrete_map=COLOR_CANCELO,
                 text=comp["Porcentaje"].map(lambda v: f"{fmt(v)} %"),
                 title="Peso de los clientes que cancelaron en clientes y en cargo mensual")
    fig.update_layout(barmode="stack", yaxis_title="Porcentaje (%)", xaxis_title="", height=420, plot_bgcolor="white")
    st.plotly_chart(fig, width="stretch")
    interpretacion(
        f"De {fmt(len(df), 0)} clientes, **{fmt(si.clientes, 0)} cancelaron (26,54 %)**. Pero esos clientes "
        f"representaban el **{fmt(si.participacion_cargo_mensual_pct)} % del cargo mensual**, porque pagaban más en "
        f"promedio ({fmt(si.cargo_mensual_promedio)} vs. {fmt(no.cargo_mensual_promedio)} u.m.).",
        "Uno de cada cuatro clientes cancela. Esta tasa es la línea base para comparar todos los segmentos.",
        "Dimensionar el problema: cerca de 139 mil u.m. al mes dejan de facturarse por cancelaciones.",
        "Es **ingreso** dejado de facturar, no rentabilidad: no hay datos de costos.")
    tabla_detalle(p0)

# ================================================================ P1
elif seccion == SECCIONES[2]:
    st.header("P1 · ¿Cómo varía la tasa según las condiciones de la cuenta?")
    p1 = T["P1_tasa_por_cuenta"]
    nombres = {"tipo_contrato": "Tipo de contrato", "metodo_pago": "Método de pago",
               "factura_electronica": "Factura electrónica", "pago_automatico": "Pago automático"}
    c = st.columns(3)
    t = p1.set_index(["variable", "segmento"])
    c[0].metric("Mes a mes", f"{fmt(t.loc[('tipo_contrato', 'Mes a mes'), 'tasa_cancelacion_pct'])} %",
                f"{fmt(t.loc[('tipo_contrato', 'Mes a mes'), 'diferencia_vs_global_pp'])} p.p. vs. global", delta_color="inverse")
    c[1].metric("Dos años", f"{fmt(t.loc[('tipo_contrato', 'Dos años'), 'tasa_cancelacion_pct'])} %",
                f"{fmt(t.loc[('tipo_contrato', 'Dos años'), 'diferencia_vs_global_pp'])} p.p. vs. global", delta_color="inverse")
    c[2].metric("Cheque electrónico", f"{fmt(t.loc[('metodo_pago', 'Cheque electrónico'), 'tasa_cancelacion_pct'])} %",
                f"{fmt(t.loc[('metodo_pago', 'Cheque electrónico'), 'diferencia_vs_global_pp'])} p.p. vs. global", delta_color="inverse")
    metrica(*TASA_DEF)
    var = st.selectbox("Variable a comparar", list(nombres), format_func=nombres.get)
    orden = ["Mes a mes", "Un año", "Dos años"] if var == "tipo_contrato" else None
    st.plotly_chart(grafico_tasa(p1[p1.variable == var], f"Tasa de cancelación por {nombres[var].lower()} (%)",
                                 nombres[var], orden, horizontal=var == "metodo_pago"), width="stretch")
    st.caption("Barras rojas: segmentos por encima de la tasa global. Línea punteada: tasa global (26,54 %).")
    interpretacion(
        "El contrato **mes a mes cancela 42,71 %**, frente a 11,27 % (un año) y 2,83 % (dos años), y reúne el "
        "**88,55 % de todas las cancelaciones**. Con **cheque electrónico** la tasa es 45,29 %; con pago automático, "
        "15–17 %. Con factura electrónica, 33,57 % frente a 16,33 %.",
        "Las condiciones de la cuenta marcan grandes diferencias; el contrato es la variable más diferenciadora.",
        "Ofrecer incentivos para pasar de mes a mes a contratos de 1–2 años y promover el pago automático.",
        "Es una asociación, no una causa: los clientes más comprometidos pueden elegir contratos largos.")
    tabla_detalle(p1[p1.variable == var])

# ================================================================ P2
elif seccion == SECCIONES[3]:
    st.header("P2 · ¿Cómo varía la tasa según la antigüedad?")
    p2 = T["P2_tasa_por_antiguedad"]
    c = st.columns(3)
    c[0].metric("Primer año (0–12 meses)", f"{fmt(p2.tasa_cancelacion_pct[0])} %")
    c[1].metric("Más de 4 años (49–72 meses)", f"{fmt(p2.tasa_cancelacion_pct[3])} %")
    c[2].metric("Cancelaciones en el primer año", f"{fmt(p2.participacion_cancelaciones_pct[0])} %")
    metrica(*TASA_DEF)
    col1, col2 = st.columns(2)
    col1.plotly_chart(grafico_tasa(p2, "Tasa de cancelación por rango de antigüedad (%)", "Antigüedad"), width="stretch")
    comp = p2.melt(id_vars="segmento", value_vars=["participacion_clientes_pct", "participacion_cancelaciones_pct"],
                   var_name="Medida", value_name="Porcentaje")
    comp["Medida"] = comp["Medida"].map({"participacion_clientes_pct": "% de clientes",
                                         "participacion_cancelaciones_pct": "% de cancelaciones"})
    fig = px.bar(comp, x="segmento", y="Porcentaje", color="Medida", barmode="group",
                 color_discrete_sequence=[GRIS, ROJO], text=comp["Porcentaje"].map(lambda v: f"{fmt(v, 1)} %"),
                 title="Peso de cada rango en clientes y en cancelaciones (%)")
    fig.update_layout(xaxis_title="Antigüedad", yaxis_title="Porcentaje (%)", height=420, plot_bgcolor="white",
                      legend=dict(orientation="h", y=-0.2))
    col2.plotly_chart(fig, width="stretch")
    interpretacion(
        "La tasa baja de forma constante con la antigüedad: **47,44 %** en el primer año, 28,71 %, 20,39 % y "
        "**9,51 %** después de 4 años. El primer año tiene el 31 % de los clientes pero el **55,48 % de las cancelaciones**.",
        "A menor antigüedad, mayor cancelación; el primer año es el periodo crítico.",
        "Crear un programa de bienvenida y acompañamiento durante los primeros 12 meses.",
        "Es un corte transversal: no se sigue a los mismos clientes en el tiempo.")
    tabla_detalle(p2)

# ================================================================ P3
elif seccion == SECCIONES[4]:
    st.header("P3 · ¿Cómo varía la tasa según los servicios contratados?")
    p3 = T["P3_tasa_por_servicios"]
    t = p3.set_index(["variable", "segmento"])
    c = st.columns(3)
    c[0].metric("Fibra óptica", f"{fmt(t.loc[('servicio_internet', 'Fibra óptica'), 'tasa_cancelacion_pct'])} %",
                f"{fmt(t.loc[('servicio_internet', 'Fibra óptica'), 'diferencia_vs_global_pp'])} p.p. vs. global", delta_color="inverse")
    c[1].metric("Sin soporte técnico", f"{fmt(t.loc[('soporte_tecnico', 'No'), 'tasa_cancelacion_pct'])} %")
    c[2].metric("Con soporte técnico", f"{fmt(t.loc[('soporte_tecnico', 'Sí'), 'tasa_cancelacion_pct'])} %")
    metrica(*TASA_DEF)
    nombres = {"servicio_internet": "Tipo de internet", "tipo_servicio": "Tipo de servicio",
               "rango_servicios_adicionales": "Cantidad de servicios adicionales"}
    var = st.selectbox("Variable a comparar", list(nombres), format_func=nombres.get)
    st.plotly_chart(grafico_tasa(p3[p3.variable == var], f"Tasa de cancelación por {nombres[var].lower()} (%)",
                                 nombres[var]), width="stretch")
    adic = {"seguridad_en_linea": "Seguridad en línea", "respaldo_en_linea": "Respaldo en línea",
            "proteccion_dispositivos": "Protección de dispositivos", "soporte_tecnico": "Soporte técnico",
            "streaming_tv": "Streaming TV", "streaming_peliculas": "Streaming películas"}
    a = p3[p3.variable.isin(adic) & p3.segmento.isin(["Sí", "No"])].copy()
    a["Servicio"] = a["variable"].map(adic)
    a["¿Lo tiene?"] = a["segmento"]
    fig = px.bar(a, x="Servicio", y="tasa_cancelacion_pct", color="¿Lo tiene?", barmode="group",
                 color_discrete_map={"No": ROJO, "Sí": AZUL},
                 text=a["tasa_cancelacion_pct"].map(lambda v: f"{fmt(v, 1)} %"),
                 title="Tasa de cancelación según tenga o no cada servicio adicional (clientes con internet, %)")
    fig.add_hline(y=TASA_GLOBAL, line_dash="dash", line_color=GRIS)
    fig.update_layout(yaxis_title="Tasa de cancelación (%)", xaxis_title="", height=440, plot_bgcolor="white")
    st.plotly_chart(fig, width="stretch")
    interpretacion(
        "La **fibra óptica cancela 41,89 %** (DSL 18,96 %, sin internet 7,40 %) y genera el 82 % del cargo mensual "
        "perdido. Sin **seguridad en línea (41,77 %)** o **soporte técnico (41,64 %)** la tasa casi triplica la de "
        "quienes sí los tienen (≈15 %). Streaming casi no cambia la tasa.",
        "Los servicios sí se asocian con la cancelación: fibra sin servicios de protección es el perfil de mayor riesgo.",
        "Ofrecer seguridad y soporte técnico (por ejemplo, en promoción) a clientes de fibra que no los tienen.",
        "No hay datos de calidad del servicio ni precios por producto para explicar por qué la fibra cancela más.")
    tabla_detalle(p3[p3.variable == var])

# ================================================================ P4
elif seccion == SECCIONES[5]:
    st.header("P4 · ¿Cómo varía la tasa según el perfil demográfico?")
    p4 = T["P4_tasa_por_perfil"]
    t = p4.set_index(["variable", "segmento"])
    c = st.columns(3)
    c[0].metric("Adultos mayores", f"{fmt(t.loc[('adulto_mayor', 'Sí'), 'tasa_cancelacion_pct'])} %")
    c[1].metric("Sin pareja ni dependientes", f"{fmt(t.loc[('tiene_familia', 'No'), 'tasa_cancelacion_pct'])} %")
    c[2].metric("Diferencia por género", f"{fmt(abs(t.loc[('genero', 'Femenino'), 'tasa_cancelacion_pct'] - t.loc[('genero', 'Masculino'), 'tasa_cancelacion_pct']))} p.p.")
    metrica(*TASA_DEF)
    nombres = {"genero": "Género", "adulto_mayor": "Adulto mayor", "tiene_pareja": "Tiene pareja",
               "tiene_dependientes": "Tiene dependientes", "tiene_familia": "Tiene familia"}
    p = p4.copy()
    p["segmento"] = p["variable"].map(nombres) + ": " + p["segmento"]
    st.plotly_chart(grafico_tasa(p, "Tasa de cancelación por variable de perfil (%)", "", horizontal=True),
                    width="stretch")
    st.caption("Barras rojas: grupos por encima de la tasa global. Línea punteada: tasa global (26,54 %).")
    interpretacion(
        "El **género no marca diferencia** (26,92 % vs. 26,16 %). Los **adultos mayores cancelan 41,68 %** "
        "(vs. 23,61 %) y quienes **no tienen pareja ni dependientes, 34,24 %** (vs. 19,82 %).",
        "El perfil importa en edad y situación familiar, no en género.",
        "Diseñar ofertas para adultos mayores y planes familiares que vinculen a más personas del hogar.",
        "La edad que define «adulto mayor» no está documentada en la fuente.")
    tabla_detalle(p4)

# ================================================================ P5
elif seccion == SECCIONES[6]:
    st.header("P5 · ¿Cómo se diferencian los cargos de quienes cancelan y quienes permanecen?")
    p5a, p5b = T["P5a_estadisticas_cargos"], T["P5b_tasa_por_rango_cargo"]
    est = p5a.set_index(["variable", "estadistica"])
    c = st.columns(4)
    c[0].metric("Cargo mensual medio · cancelan", f"{fmt(est.loc[('cargo_mensual', 'mean'), 'Sí'])} u.m.")
    c[1].metric("Cargo mensual medio · permanecen", f"{fmt(est.loc[('cargo_mensual', 'mean'), 'No'])} u.m.")
    c[2].metric("Antigüedad mediana · cancelan", f"{fmt(est.loc[('antiguedad_meses', '50%'), 'Sí'], 0)} meses")
    c[3].metric("Antigüedad mediana · permanecen", f"{fmt(est.loc[('antiguedad_meses', '50%'), 'No'], 0)} meses")
    metrica("Media, mediana y cuartiles del cargo mensual por grupo; tasa de cancelación por rango de cargo",
            "estadísticas descriptivas de cargo_mensual según cancelo; cancelaciones ÷ clientes × 100 por rango",
            "unidades monetarias por mes (u.m./mes) y porcentaje (%)")
    col1, col2 = st.columns(2)
    fig = px.box(df, x="cancelo", y="cargo_mensual", color="cancelo", color_discrete_map=COLOR_CANCELO,
                 category_orders={"cancelo": ["No", "Sí"]},
                 title="Distribución del cargo mensual según cancelación (u.m./mes)")
    fig.update_layout(xaxis_title="¿Canceló?", yaxis_title="Cargo mensual (u.m./mes)", showlegend=False,
                      height=420, plot_bgcolor="white")
    col1.plotly_chart(fig, width="stretch")
    col2.plotly_chart(grafico_tasa(p5b, "Tasa de cancelación por rango de cargo mensual (%)",
                                   "Rango de cargo mensual (u.m./mes)"), width="stretch")
    interpretacion(
        "Quienes cancelan **pagan más al mes** (mediana 79,65 vs. 64,43 u.m.) pero llevan **mucho menos tiempo** "
        "(mediana 10 vs. 38 meses). La tasa sube de 10,86 % con cargo bajo a **37,95 % con cargo alto (70–90)**; "
        "los rangos alto y muy alto concentran el 81 % del cargo mensual perdido.",
        "El riesgo se concentra en clientes nuevos con cargos mensuales altos.",
        "Revisar la propuesta de valor de los planes caros en los primeros meses (descuentos o beneficios de entrada).",
        "Mayor cargo no significa mayor rentabilidad: sin costos no se puede medir la utilidad. Moneda no documentada.")
    with st.expander("📋 Ver tablas de resultados (AE3)"):
        st.dataframe(p5a, hide_index=True, width="stretch")
        st.dataframe(p5b, hide_index=True, width="stretch")

# ================================================================ P6
elif seccion == SECCIONES[7]:
    st.header("P6 · ¿Qué segmentos combinados tienen las tasas más altas?")
    p6 = T["P6_top10_segmentos"]
    top3 = p6.head(3)
    c = st.columns(3)
    c[0].metric("Segmento #1: tasa", f"{fmt(p6.tasa_cancelacion_pct[0])} %", "Mes a mes · Fibra · 0–12 meses",
                delta_color="off")
    c[1].metric("Top 3: % de cancelaciones", f"{fmt(top3.participacion_cancelaciones_pct.sum())} %",
                f"con {fmt(top3.participacion_clientes_pct.sum())} % de los clientes", delta_color="off")
    c[2].metric("Top 3: % del cargo mensual perdido", f"{fmt(top3.participacion_cargo_perdido_pct.sum())} %")
    metrica("Tasa de cancelación por segmento combinado (contrato × internet × antigüedad), mínimo 50 clientes",
            "cancelaciones ÷ clientes del segmento × 100; ranking de mayor a menor",
            "porcentaje (%); cargo mensual perdido en u.m./mes")
    p = p6.copy()
    p["segmento"] = p["ranking"].astype(str) + ". " + p["segmento"]
    st.plotly_chart(grafico_tasa(p, "Diez segmentos con mayor tasa de cancelación (%)", "", horizontal=True),
                    width="stretch")
    fig = px.scatter(p, x="clientes", y="tasa_cancelacion_pct", size="cargo_mensual_perdido",
                     color="tipo_contrato", hover_name="segmento", size_max=50,
                     color_discrete_map={"Mes a mes": ROJO, "Un año": AZUL},
                     title="Tamaño del segmento vs. tasa (el área indica el cargo mensual perdido)")
    fig.update_layout(xaxis_title="Clientes del segmento", yaxis_title="Tasa de cancelación (%)",
                      legend_title="Contrato", height=420, plot_bgcolor="white")
    st.plotly_chart(fig, width="stretch")
    interpretacion(
        "El segmento **mes a mes + fibra óptica + 0–12 meses cancela 70,20 %** (916 clientes, 34,40 % de todas "
        "las cancelaciones). Los tres primeros son todos mes a mes con fibra: **26 % de los clientes, 58 % de las "
        "cancelaciones y 67 % del cargo mensual perdido**.",
        "La cancelación se concentra en una combinación clara de contrato, servicio y antigüedad.",
        "Priorizar la campaña de retención en estos tres segmentos (≈1.860 clientes) en lugar de toda la base.",
        "Se exigió un mínimo de 50 clientes por segmento para evitar tasas engañosas en grupos pequeños.")
    tabla_detalle(p6)

# ================================================================ CONCLUSIONES
else:
    st.header("🧭 Conclusiones, recomendaciones y limitaciones")
    st.subheader("Conclusiones")
    st.markdown(
        "1. **Uno de cada cuatro clientes cancela (26,54 %)**, y ellos representan el 30,50 % del cargo mensual.\n"
        "2. La cancelación se concentra en clientes con **contrato mes a mes (42,71 %)**, en su **primer año "
        "(47,44 %)**, con **fibra óptica (41,89 %)**, **sin seguridad ni soporte técnico (≈42 %)** y que pagan con "
        "**cheque electrónico (45,29 %)**.\n"
        "3. El segmento **mes a mes + fibra + 0–12 meses alcanza 70,20 %**; los tres segmentos principales reúnen el "
        "58 % de las cancelaciones.\n"
        "4. El género no diferencia; los adultos mayores y quienes no tienen familia cancelan más.")
    st.subheader("Recomendaciones para el equipo de retención")
    st.markdown(
        "- **Focalizar** la campaña en los segmentos mes a mes con fibra óptica y menos de 2 años.\n"
        "- **Migrar contratos**: incentivos para pasar de mes a mes a 1 o 2 años.\n"
        "- **Acompañar el primer año** con un programa de bienvenida.\n"
        "- **Ofrecer seguridad en línea y soporte técnico** a clientes de fibra que no los tienen.\n"
        "- **Promover el pago automático** frente al cheque electrónico.")
    st.subheader("Limitaciones")
    st.markdown(
        "- Datos **ficticios** (IBM): los resultados no se generalizan a empresas reales.\n"
        "- Análisis **descriptivo**: las diferencias no prueban causas.\n"
        "- **Ingreso ≠ rentabilidad**: no hay costos, por lo que no se mide utilidad.\n"
        "- Sin fechas ni motivos de cancelación; moneda no documentada.")
    st.subheader("Verificación de cifras")
    chequeo = []
    for nombre, var in [("P1_tasa_por_cuenta", "tipo_contrato"), ("P2_tasa_por_antiguedad", "rango_antiguedad"),
                        ("P3_tasa_por_servicios", "servicio_internet"), ("P4_tasa_por_perfil", "adulto_mayor"),
                        ("P5b_tasa_por_rango_cargo", "rango_cargo_mensual")]:
        app = tasa_por(var).set_index(var)["tasa_cancelacion_pct"].round(2)
        nb = T[nombre].query("variable == @var").set_index("segmento")["tasa_cancelacion_pct"]
        chequeo.append({"Tabla AE3": nombre, "Variable": var, "¿Coincide con el notebook?":
                        "✅ Sí" if (app.reindex(nb.index) - nb).abs().max() < 0.01 else "❌ No"})
    st.caption("La app recalcula las tasas desde el dataset preparado y las compara con las tablas exportadas por el notebook de AE3.")
    st.dataframe(pd.DataFrame(chequeo), hide_index=True, width="stretch")
