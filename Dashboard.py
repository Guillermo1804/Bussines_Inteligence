import pandas as pd
import streamlit as st

st.title("Dashboard Dinámico y Balanced Scorecard")

# Carga el DataFrame desde el CSV. NO intentes conectar a la BD en la nube.
df = pd.read_csv('data_dashboard.csv')

# ----------- Sidebar: Filtros dinámicos ----------
st.sidebar.header("Filtros avanzados")
proyectos = df["Proyecto"].unique().tolist()
clientes = df["Cliente"].unique().tolist()
sectores = df["Industria"].unique().tolist()
proyecto_sel = st.sidebar.multiselect("Proyecto", proyectos, default=proyectos)
cliente_sel = st.sidebar.multiselect("Cliente", clientes, default=clientes)
sector_sel = st.sidebar.multiselect("Sector", sectores, default=sectores)
filtro = (
    df["Proyecto"].isin(proyecto_sel) &
    df["Cliente"].isin(cliente_sel) &
    df["Industria"].isin(sector_sel)
)
df_f = df[filtro]

# ----------- 3. Paneles de KPIs ----------
st.header("KPI Financieros")
col1, col2, col3 = st.columns(3)
col1.metric("Presupuesto Total", f"${df_f['Presupuesto'].sum():,.2f}")
col2.metric("Desviación Promedio", f"${df_f['Desviacion'].mean():,.2f}")
col3.metric("ROI Promedio", f"{df_f['ROI'].mean()*100:.2f}%")
st.header("KPI de Cumplimiento")
col1, col2, col3 = st.columns(3)
col1.metric("Tareas Totales", int(df_f['Tareas_Total'].sum()))  # antes era 'Tareas_Finalizadas'
col2.metric("Automatización", int(df_f['Automatizacion'].sum()))
col3.metric("Defectos", int(df_f['Defectos'].sum()))
st.header("KPI de Calidad")
col1, col2 = st.columns(2)
col1.metric("Defectos Totales", int(df_f['Defectos'].sum()))
col2.metric("Proyectos Seguros", int(df_f['Seguridad'].sum()))
st.header("KPI de Crecimiento")
col1, col2 = st.columns(2)
col1.metric("Clientes Activos", df_f["Cliente"].nunique())
col2.metric("Sectores Atendidos", df_f["Industria"].nunique())

# ---------- 4. Balanced Scorecard/OKRs ----------
st.header("Balanced Scorecard y OKRs")
bsc_cols = ["Proyecto", "Cliente", "ROI", "Tareas_Total", "Automatizacion", "Defectos", "Crecimiento", "OKR"]
st.dataframe(df_f[bsc_cols].head(20))
# ---------- 5. Drill-down por Proyecto ----------
st.header("Detalle por Proyecto")
if len(proyectos) > 0:
    proyecto_drill = st.selectbox("Selecciona un proyecto:", proyectos)
    st.dataframe(df[df["Proyecto"] == proyecto_drill])
else:
    st.info("No hay proyectos para mostrar.")

st.sidebar.info("""
Desarrollado con Streamlit y vinculado a tu DW.  
Actualiza tu DW y los indicadores cambian en tiempo real.
""")
