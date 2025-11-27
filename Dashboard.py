import streamlit as st
import pandas as pd

# -----------------------------
# Carga de datos desde CSV
# -----------------------------
@st.cache_data
def load_data():
    proyectos = pd.read_csv("dw_proyectos.csv")
    tareas = pd.read_csv("dw_tareas.csv")
    incidentes = pd.read_csv("dw_incidentes.csv")
    return proyectos, tareas, incidentes

proyectos, tareas, incidentes = load_data()

st.set_page_config(page_title="Balanced Scorecard - DW Gestión", layout="wide")
st.title("📊 Balanced Scorecard - Data Warehouse de Proyectos")
st.markdown("---")

# Filtros globales opcionales
st.sidebar.header("Filtros Generales")
anios_disponibles = sorted(proyectos["AnioCierre"].dropna().unique())
anio_sel = st.sidebar.multiselect(
    "Filtrar por año de cierre",
    anios_disponibles,
    default=anios_disponibles
)
if anio_sel:
    proyectos = proyectos[proyectos["AnioCierre"].isin(anio_sel)]

# -----------------------------
# SECTOR 1: Perspectiva Financiera
# ¿Qué % de proyectos finalizados se mantuvieron dentro del presupuesto?
# -----------------------------
st.header("1️⃣ Perspectiva Financiera")
st.subheader("¿Qué porcentaje de proyectos finalizados se mantuvieron en el presupuesto original?")

proy_finalizados = proyectos[proyectos["EstadoProyecto"].str.upper() == "FINALIZADO"]

if not proy_finalizados.empty:
    dentro_presupuesto = proy_finalizados[proy_finalizados["costo_real"] <= proy_finalizados["presupuesto"]]
    total_final = len(proy_finalizados)
    total_dentro = len(dentro_presupuesto)
    pct_dentro = (total_dentro / total_final * 100) if total_final > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Proyectos finalizados", total_final)
    with col2:
        st.metric("Dentro de presupuesto", total_dentro)
    with col3:
        st.metric("% Dentro presupuesto", f"{pct_dentro:.1f}%")

    # Gráfico de barras
    status_df = pd.DataFrame({
        "Categoría": ["Dentro presupuesto", "Fuera presupuesto"],
        "Cantidad": [total_dentro, total_final - total_dentro]
    })
    st.bar_chart(status_df.set_index("Categoría"))

    st.caption("**Cálculo:** Porcentaje = (Proyectos con costo_real ≤ presupuesto) / (Total de proyectos finalizados) × 100")
else:
    st.info("No hay proyectos finalizados en el período seleccionado.")

st.markdown("---")

# -----------------------------
# SECTOR 2: Perspectiva de Clientes/Mercado
# ¿Qué industrias tienen más proyectos cancelados?
# -----------------------------
st.header("2️⃣ Perspectiva de Clientes / Mercado")
st.subheader("¿Qué industrias o sectores tienen más proyectos cancelados?")

proy_cancelados = proyectos[proyectos["EstadoProyecto"].str.upper() == "CANCELADO"]

if not proy_cancelados.empty:
    industria_counts = (
        proy_cancelados.groupby("Industria")["idProyecto"]
        .count()
        .reset_index(name="ProyectosCancelados")
        .sort_values("ProyectosCancelados", ascending=False)
    )

    st.dataframe(industria_counts, use_container_width=True)
    st.bar_chart(industria_counts.set_index("Industria")["ProyectosCancelados"])

    st.caption("**Cálculo:** Agrupación de proyectos con EstadoProyecto = 'CANCELADO' por industria del cliente.")
else:
    st.info("No hay proyectos cancelados en el período seleccionado.")

st.markdown("---")

# -----------------------------
# SECTOR 3: Perspectiva de Procesos Internos
# ¿Qué % de tareas fueron automatizadas?
# -----------------------------
st.header("3️⃣ Perspectiva de Procesos Internos")
st.subheader("¿Qué porcentaje de tareas fueron automatizadas?")

if not tareas.empty:
    total_tareas = len(tareas)
    tareas_auto = tareas[tareas["EsAutomatizacion"] == 1]
    total_auto = len(tareas_auto)
    pct_auto = (total_auto / total_tareas * 100) if total_tareas > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de tareas", total_tareas)
    with col2:
        st.metric("Tareas automatizadas", total_auto)
    with col3:
        st.metric("% Automatización", f"{pct_auto:.1f}%")

    # Gráfico
    auto_df = pd.DataFrame({
        "Tipo": ["Automatizada", "No automatizada"],
        "Cantidad": [total_auto, total_tareas - total_auto]
    })
    st.bar_chart(auto_df.set_index("Tipo"))

    st.caption("**Cálculo:** Porcentaje = (Tareas con es_automatizacion = 1) / (Total de tareas) × 100")
else:
    st.info("No hay información de tareas disponible.")

st.markdown("---")

# -----------------------------
# SECTOR 4: Perspectiva de Aprendizaje y Crecimiento
# ¿En qué proyectos existe mayor % de incidentes?
# -----------------------------
st.header("4️⃣ Perspectiva de Aprendizaje y Crecimiento")
st.subheader("¿En qué proyectos existe mayor porcentaje de incidentes?")

if not incidentes.empty:
    # Contar incidentes por proyecto
    inc_por_proy = (
        incidentes.groupby("Proyecto_idProyecto")["idIncidente"]
        .count()
        .reset_index(name="NumIncidentes")
    )

    # Contar tareas por proyecto
    tareas_por_proy = (
        tareas.groupby("Proyecto_idProyecto")["idTarea"]
        .count()
        .reset_index(name="NumTareas")
    )

    # Merge
    resumen = inc_por_proy.merge(tareas_por_proy, on="Proyecto_idProyecto", how="left")
    resumen["NumTareas"] = resumen["NumTareas"].fillna(1)  # Evitar división por 0
    resumen["PctIncidentes"] = (resumen["NumIncidentes"] / resumen["NumTareas"]) * 100

    # Unir con nombres de proyecto
    resumen = resumen.merge(
        proyectos[["idProyecto", "nombre_proyecto"]],
        left_on="Proyecto_idProyecto",
        right_on="idProyecto",
        how="left"
    )

    # Top N proyectos
    top_n = st.slider("Mostrar Top N proyectos con más incidentes", 5, 20, 10)
    top_inc = resumen.sort_values("PctIncidentes", ascending=False).head(top_n)

    st.dataframe(
        top_inc[["nombre_proyecto", "NumIncidentes", "NumTareas", "PctIncidentes"]],
        use_container_width=True
    )
    st.bar_chart(top_inc.set_index("nombre_proyecto")["PctIncidentes"])

    st.caption("**Cálculo:** PctIncidentes = (Nº incidentes del proyecto / Nº tareas del proyecto) × 100")
else:
    st.info("No hay información de incidentes disponible.")

st.markdown("---")
st.caption("📂 Balanced Scorecard construido sobre datos del Data Warehouse (db_soporte).")
