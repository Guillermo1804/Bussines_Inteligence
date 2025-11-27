import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Balanced Scorecard - DW Gestión",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Reducir al máximo márgenes, ocultar header y ajustar textos
st.markdown(
    """
    <style>
    header {visibility: hidden;}
    .block-container {padding-top: 0.1rem; padding-bottom: 0.2rem;}
    h1, h2, h3, h4 {margin-top: 0.1rem; margin-bottom: 0.1rem;}
    [data-testid="stMetricValue"] {font-size: 1.1rem;}
    [data-testid="stMetricLabel"] {font-size: 0.8rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def load_data(version: int = 1):
    proyectos = pd.read_csv("dw_proyectos.csv")
    tareas = pd.read_csv("dw_tareas.csv")
    incidentes = pd.read_csv("dw_incidentes.csv")
    hechos = pd.read_csv("dw_hechos_proyecto.csv")
    return proyectos, tareas, incidentes, hechos

proyectos, tareas, incidentes, hechos = load_data(version=1)

# Título más compacto con HTML
st.markdown(
    "<h3 style='margin-bottom:0.3rem;'>Balanced Scorecard de Proyectos (DW)</h3>",
    unsafe_allow_html=True,
)

# Filtro global compacto + botón de navegación
anios = sorted(proyectos["AnioCierre"].dropna().unique()) if "AnioCierre" in proyectos.columns else []
col_filtro1, col_filtro2, col_boton = st.columns([1, 4, 1])

with col_filtro1:
    if anios:
        anio_sel = st.selectbox("Año", options=["Todos"] + list(anios), index=0)
        if anio_sel != "Todos":
            proyectos = proyectos[proyectos["AnioCierre"] == anio_sel]

with col_boton:
    st.markdown(
        """
        <a href="https://modelo-hrr4m48jvojcjvgftqdrrg.streamlit.app/siguiente" 
           target="_blank" 
           style="display:inline-block; padding:10px 20px; background-color:#4CAF50; 
                  color:white; text-decoration:none; border-radius:5px; font-weight:bold;">
           ➜ Modelo de Predicción
        </a>
        """,
        unsafe_allow_html=True
    )

# Layout 2x2
fila1_col1, fila1_col2 = st.columns(2)
fila2_col1, fila2_col2 = st.columns(2)


# =====================================================
# 1) Financiera – Proyectos dentro de presupuesto (barras por año)
# =====================================================
with fila1_col1:
    st.markdown("#### 1. Financiera – Proyectos dentro de presupuesto")
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

        if "AnioCierre" in proy_final.columns:
            resumen_anio = (
                proy_final
                .assign(Dentro=lambda df: df["costo_real"] <= df["presupuesto"])
                .groupby("AnioCierre")
                .agg(
                    Finalizados=("idProyecto", "count"),
                    DentroPresupuesto=("Dentro", "sum")
                )
                .reset_index()
            )
            resumen_anio["FueraPresupuesto"] = (
                resumen_anio["Finalizados"] - resumen_anio["DentroPresupuesto"]
            )

            # pasar a formato largo para barras agrupadas
            resumen_anio["AnioCierre"] = resumen_anio["AnioCierre"].astype(str)
            long_df = resumen_anio.melt(
                id_vars=["AnioCierre"],
                value_vars=["DentroPresupuesto", "FueraPresupuesto"],
                var_name="Tipo",
                value_name="Proyectos"
            )
            long_df["Tipo"] = long_df["Tipo"].map({
                "DentroPresupuesto": "Dentro del presupuesto",
                "FueraPresupuesto": "Fuera del presupuesto"
            })

            fig1 = px.bar(
                long_df,
                x="AnioCierre",
                y="Proyectos",
                color="Tipo",
                barmode="group",
                height=140,
                labels={"AnioCierre": "Año", "Proyectos": "Número de proyectos"}
            )
            fig1.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig1, use_container_width=True)
        else:
            # Sin año, solo una barra global
            resumen = pd.DataFrame({
                "Tipo": ["Dentro del presupuesto", "Fuera del presupuesto"],
                "Proyectos": [total_dentro, total_final - total_dentro]
            })
            fig1 = px.bar(
                resumen,
                x="Tipo",
                y="Proyectos",
                text="Proyectos",
                height=140
            )
            fig1.update_traces(textposition="outside")
            fig1.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig1, use_container_width=True)

        st.caption(
            "Cálculo: por cada año se cuentan los proyectos finalizados con costo_real "
            "≤ presupuesto (Dentro del presupuesto) y el resto como Fuera del presupuesto."
        )
    else:
        st.info("Sin proyectos finalizados en el período seleccionado.")

# =====================================================
# 2) Cliente / Mercado – Industrias con más cancelaciones (solo barras)
# =====================================================
with fila1_col2:
    st.markdown("#### 2. Cliente – Industrias con más proyectos cancelados")
    proy_cancel = proyectos[proyectos["EstadoProyecto"].str.upper() == "CANCELADO"]

    if not proy_cancel.empty and "Industria" in proy_cancel.columns:
        industria_counts = (
            proy_cancel.groupby("Industria")["idProyecto"]
            .count()
            .reset_index(name="ProyectosCancelados")
            .sort_values("ProyectosCancelados", ascending=False)
        )
        top = industria_counts.head(5)

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
# 3) Procesos Internos – Tareas automatizadas vs no automatizadas por proyecto
# =====================================================
with fila2_col1:
    st.markdown("#### 3. Procesos – Tareas automatizadas vs no automatizadas por proyecto")
    if not tareas.empty and "EsAutomatizacion" in tareas.columns:
        total_tareas = len(tareas)
        tareas_auto = tareas[tareas["EsAutomatizacion"] == 1]
        total_auto = len(tareas_auto)
        pct_auto = (total_auto / total_tareas * 100) if total_tareas > 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Tareas totales", total_tareas)
        c2.metric("Automatizadas", total_auto)
        c3.metric("% Automatizadas", f"{pct_auto:.1f}%")

        # Cantidad de tareas auto / no auto por proyecto
        if "Proyecto_idProyecto" in tareas.columns:
            resumen_auto = (
                tareas.groupby("Proyecto_idProyecto")
                .agg(
                    TareasTotales=("idTarea", "count"),
                    TareasAuto=("EsAutomatizacion", "sum")
                )
                .reset_index()
            )
            resumen_auto["TareasNoAuto"] = (
                resumen_auto["TareasTotales"] - resumen_auto["TareasAuto"]
            )

            # Unir nombres de proyecto
            resumen_auto = resumen_auto.merge(
                proyectos[["idProyecto", "nombre_proyecto"]],
                left_on="Proyecto_idProyecto",
                right_on="idProyecto",
                how="left"
            )

            # Top N por total de tareas (o por automatizadas, como prefieras)
            top_auto = resumen_auto.sort_values(
                "TareasTotales", ascending=False
            ).head(5)

            # Pasar a formato largo para barras agrupadas
            plot_df = top_auto.melt(
                id_vars=["nombre_proyecto"],
                value_vars=["TareasAuto", "TareasNoAuto"],
                var_name="Tipo",
                value_name="Cantidad"
            )
            plot_df["Tipo"] = plot_df["Tipo"].map(
                {"TareasAuto": "Automatizadas", "TareasNoAuto": "No automatizadas"}
            )

            fig3 = px.bar(
                plot_df,
                x="nombre_proyecto",
                y="Cantidad",
                color="Tipo",
                barmode="group",
                height=140,
                labels={"nombre_proyecto": "Proyecto", "Cantidad": "Tareas"},
            )

            fig3.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                legend_title_text="Tipo",
                xaxis_tickangle=-20,          # menos inclinación
                xaxis_tickfont=dict(size=9),  # texto más pequeño
            )

            st.plotly_chart(fig3, use_container_width=True)

        else:
            st.info("No se encontró la columna Proyecto_idProyecto en tareas.")

        st.caption(
            "Cálculo: por cada proyecto se cuentan las tareas con EsAutomatizacion = 1 "
            "(Automatizadas) y las restantes como No automatizadas."
        )
    else:
        st.info("No hay información suficiente de tareas.")


# =====================================================
# 4) Aprendizaje / Riesgo – Proyectos con mayor % de incidentes (barras verticales 0–1)
# =====================================================
with fila2_col2:
    st.markdown("#### 4. Aprendizaje/Riesgo – Proyectos con mayor % de incidentes")
    if not incidentes.empty:
        # Incidentes por proyecto
        inc_por_proy = (
            incidentes.groupby("Proyecto_idProyecto")["idIncidente"]
            .count()
            .reset_index(name="NumIncidentes")
        )

        # Tareas por proyecto
        tareas_por_proy = (
            tareas.groupby("Proyecto_idProyecto")["idTarea"]
            .count()
            .reset_index(name="NumTareas")
        )

        # Unir y calcular proporción (0–1)
        resumen = inc_por_proy.merge(
            tareas_por_proy, on="Proyecto_idProyecto", how="left"
        )
        resumen["NumTareas"] = resumen["NumTareas"].fillna(1)
        resumen["IncidentesPorTarea"] = (
            resumen["NumIncidentes"] / resumen["NumTareas"]
        )

        # Añadir nombre de proyecto
        resumen = resumen.merge(
            proyectos[["idProyecto", "nombre_proyecto"]],
            left_on="Proyecto_idProyecto",
            right_on="idProyecto",
            how="left"
        )

        # Top 5 proyectos distintos por proporción de incidentes
        top_inc = (
            resumen
            .sort_values("IncidentesPorTarea", ascending=False)
            .drop_duplicates(subset=["nombre_proyecto"])
            .head(5)
        )

        fig4 = px.bar(
            top_inc,
            x="nombre_proyecto",
            y="IncidentesPorTarea",
            text="IncidentesPorTarea",
            labels={
                "nombre_proyecto": "Proyecto",
                "IncidentesPorTarea": "Incidentes por tarea"
            },
            height=140
        )
        fig4.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig4.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            yaxis=dict(range=[0, 1]),          # escala fija de 0 a 1
            xaxis_tickangle=-20,               # nombres menos inclinados
            xaxis_tickfont=dict(size=9)
        )
        st.plotly_chart(fig4, use_container_width=True)

        st.caption(
            "Cálculo: Incidentes por tarea = número de incidentes del proyecto / número de tareas del proyecto. "
            "Se muestran los proyectos con mayor proporción de incidentes por tarea, en escala 0–1."
        )
    else:
        st.info("No hay información de incidentes en el DW.")
