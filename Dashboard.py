import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Balanced Scorecard - DW Gestión",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Reducir al máximo márgenes y tamaños
st.markdown(
    """
    <style>
    .block-container {padding-top: 0.2rem; padding-bottom: 0.2rem;}
    h1, h2, h3 {margin-top: 0.2rem; margin-bottom: 0.2rem;}
    [data-testid="stMetricValue"] {font-size: 1.1rem;}
    [data-testid="stMetricLabel"] {font-size: 0.8rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def load_data():
    proyectos = pd.read_csv("dw_proyectos.csv")
    tareas = pd.read_csv("dw_tareas.csv")
    incidentes = pd.read_csv("dw_incidentes.csv")
    return proyectos, tareas, incidentes

proyectos, tareas, incidentes = load_data()

st.title("Balanced Scorecard de Proyectos (DW)")

# Filtro global compacto
anios = sorted(proyectos["AnioCierre"].dropna().unique()) if "AnioCierre" in proyectos.columns else []
col_filtro1, col_filtro2 = st.columns([1, 5])
with col_filtro1:
    if anios:
        anio_sel = st.selectbox("Año", options=["Todos"] + list(anios), index=0)
        if anio_sel != "Todos":
            proyectos = proyectos[proyectos["AnioCierre"] == anio_sel]

# Layout 2x2
fila1_col1, fila1_col2 = st.columns(2)
fila2_col1, fila2_col2 = st.columns(2)

# =====================================================
# 1) Financiera – Proyectos dentro de presupuesto
# =====================================================
with fila1_col1:
    st.markdown("### 1. Financiera – Proyectos dentro de presupuesto")
    proy_final = proyectos[proyectos["EstadoProyecto"].str.upper() == "FINALIZADO"]

    if not proy_final.empty:
        dentro = proy_final[proy_final["costo_real"] <= proy_final["presupuesto"]]
        total_final = len(proy_final)
        total_dentro = len(dentro)
        pct_dentro = (total_dentro / total_final * 100) if total_final > 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Finalizados", total_final)
        c2.metric("Dentro de presupuesto", total_dentro)
        c3.metric("% Dentro", f"{pct_dentro:.1f}%")

        resumen = pd.DataFrame({
            "Categoría": ["Dentro", "Fuera"],
            "Proyectos": [total_dentro, total_final - total_dentro]
        })
        fig1 = px.bar(
            resumen,
            x="Categoría",
            y="Proyectos",
            text="Proyectos",
            height=140
        )
        fig1.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        fig1.update_traces(textposition="outside")
        st.plotly_chart(fig1, use_container_width=True)

        st.caption(
            "Cálculo: proyectos dentro de presupuesto si costo_real ≤ presupuesto; "
            "porcentaje = dentro / finalizados × 100."
        )
    else:
        st.info("Sin proyectos finalizados en el período seleccionado.")

# =====================================================
# 2) Cliente / Mercado – Industrias con más cancelaciones
# =====================================================
with fila1_col2:
    st.markdown("### 2. Cliente – Industrias con más proyectos cancelados")
    proy_cancel = proyectos[proyectos["EstadoProyecto"].str.upper() == "CANCELADO"]

    if not proy_cancel.empty and "Industria" in proy_cancel.columns:
        industria_counts = (
            proy_cancel.groupby("Industria")["idProyecto"]
            .count()
            .reset_index(name="ProyectosCancelados")
            .sort_values("ProyectosCancelados", ascending=False)
        )
        top = industria_counts.head(5)

        c1, c2 = st.columns([1, 1])
        with c1:
            st.dataframe(top, use_container_width=True, height=120)
        with c2:
            fig2 = px.bar(
                top,
                x="ProyectosCancelados",
                y="Industria",
                orientation="h",
                text="ProyectosCancelados",
                height=140
            )
            fig2.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            fig2.update_traces(textposition="outside")
            st.plotly_chart(fig2, use_container_width=True)

        st.caption(
            "Cálculo: conteo de proyectos con EstadoProyecto = 'CANCELADO' agrupados por Industria."
        )
    else:
        st.info("Sin proyectos cancelados o sin columna 'Industria'.")

# =====================================================
# 3) Procesos Internos – % de tareas automatizadas
# =====================================================
with fila2_col1:
    st.markdown("### 3. Procesos – Porcentaje de tareas automatizadas")
    if not tareas.empty and "EsAutomatizacion" in tareas.columns:
        total_tareas = len(tareas)
        tareas_auto = tareas[tareas["EsAutomatizacion"] == 1]
        total_auto = len(tareas_auto)
        pct_auto = (total_auto / total_tareas * 100) if total_tareas > 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Tareas totales", total_tareas)
        c2.metric("Automatizadas", total_auto)
        c3.metric("% Automatizadas", f"{pct_auto:.1f}%")

        vals = [total_auto, total_tareas - total_auto]
        labels = ["Automatizadas", "No automatizadas"]
        fig3 = px.pie(
            values=vals,
            names=labels,
            hole=0.55,
            height=140
        )
        fig3.update_layout(showlegend=True, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig3, use_container_width=True)

        st.caption(
            "Cálculo: % automatización = tareas con EsAutomatizacion = 1 / total de tareas × 100."
        )
    else:
        st.info("No hay información suficiente de tareas.")

# =====================================================
# 4) Aprendizaje / Riesgo – Proyectos con mayor % de incidentes
# =====================================================
with fila2_col2:
    st.markdown("### 4. Aprendizaje/Riesgo – Proyectos con mayor % de incidentes")
    if not incidentes.empty:
        inc_por_proy = (
            incidentes.groupby("Proyecto_idProyecto")["idIncidente"]
            .count()
            .reset_index(name="NumIncidentes")
        )
        tareas_por_proy = (
            tareas.groupby("Proyecto_idProyecto")["idTarea"]
            .count()
            .reset_index(name="NumTareas")
        )

        resumen = inc_por_proy.merge(tareas_por_proy, on="Proyecto_idProyecto", how="left")
        resumen["NumTareas"] = resumen["NumTareas"].fillna(1)
        resumen["PctIncidentes"] = (resumen["NumIncidentes"] / resumen["NumTareas"]) * 100

        resumen = resumen.merge(
            proyectos[["idProyecto", "nombre_proyecto"]],
            left_on="Proyecto_idProyecto",
            right_on="idProyecto",
            how="left"
        )

        top_inc = resumen.sort_values("PctIncidentes", ascending=False).head(5)

        st.dataframe(
            top_inc[["nombre_proyecto", "NumIncidentes", "NumTareas", "PctIncidentes"]],
            use_container_width=True,
            height=120
        )

        fig4 = px.bar(
            top_inc,
            x="PctIncidentes",
            y="nombre_proyecto",
            orientation="h",
            text="PctIncidentes",
            height=140
        )
        fig4.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        fig4.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        st.plotly_chart(fig4, use_container_width=True)

        st.caption(
            "Cálculo: PctIncidentes = número de incidentes del proyecto / número de tareas del proyecto × 100."
        )
    else:
        st.info("No hay información de incidentes en el DW.")
