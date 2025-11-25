import pandas as pd
import streamlit as st

# ---- Diccionario de usuarios, contraseñas y roles ----
usuarios = {
    "admin": "admin123",
    "analista1": "analista123",
    "viewer1": "viewer123"
}

roles = {
    "admin": "admin",
    "analista1": "analista",
    "viewer1": "viewer"
}

# ---- Login ----
usuario = st.text_input("Usuario")
password = st.text_input("Contraseña", type="password")
btn = st.button("Login")

if "log_ok" not in st.session_state:
    st.session_state["log_ok"] = False
    st.session_state["usuario"] = ""

# --- Muestra el dashboard SOLO si login es válido o sesión activa ---
if (btn and usuario in usuarios and usuarios[usuario] == password) or st.session_state["log_ok"]:
    if usuario in usuarios and usuarios[usuario] == password and not st.session_state["log_ok"]:
        st.session_state["log_ok"] = True
        st.session_state["usuario"] = usuario

    usuario_actual = st.session_state["usuario"] if st.session_state["usuario"] else usuario
    st.success(f"Bienvenido, {usuario_actual} (rol: {roles[usuario_actual]})")
    rol = roles[usuario_actual]

    # ===== Carga DataFrame e implementa filtros (todos los roles pueden filtrar) =====
    df = pd.read_csv('data_dashboard.csv')
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

    # --------------- Vistas según rol -----------------
    if rol in ['admin', 'analista']:
        # Paneles de KPIs (solo admin/analista)
        st.header("KPI Financieros")
        col1, col2, col3 = st.columns(3)
        col1.metric("Presupuesto Total", f"${df_f['Presupuesto'].sum():,.2f}")
        col2.metric("Desviación Promedio", f"${df_f['Desviacion'].mean():,.2f}")
        col3.metric("ROI Promedio", f"{df_f['ROI'].mean()*100:.2f}%")

        st.header("KPI de Cumplimiento")
        col1, col2, col3 = st.columns(3)
        col1.metric("Tareas Totales", int(df_f['Tareas_Total'].sum()))
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

    # TODOS los roles ven el scorecard, sugerencias y análisis rápido
    st.header("Balanced Scorecard y OKRs (con metas y semáforo)")

    def color_scorecard(val, meta, tipo='max'):
        try:
            x = float(val)
        except:
            return ''
        if tipo == 'max':
            if x >= meta: return 'background-color: #B6FCD5'
            elif x >= 0.7 * meta: return 'background-color: #FDFDB6'
            else: return 'background-color: #FFB6B6'
        else:
            if x <= meta: return 'background-color: #B6FCD5'
            elif x <= meta*1.5: return 'background-color: #FDFDB6'
            else: return 'background-color: #FFB6B6'

    def style_scorecard(df):
        styled = df.style
        styled = styled.applymap(lambda x: color_scorecard(x, 0.15, 'max'), subset=['ROI'])
        styled = styled.applymap(lambda x: color_scorecard(x, 5, 'max'), subset=['Automatizacion'])
        styled = styled.applymap(lambda x: color_scorecard(x, 2, 'min'), subset=['Defectos'])
        return styled

    # Metas para scorecard
    df_f['Meta ROI'] = 0.15
    df_f['Meta Automatizacion'] = 5
    df_f['Meta Defectos'] = 2

    cols = ["Proyecto", "Cliente", "ROI", "Meta ROI", "Automatizacion", "Meta Automatizacion",
            "Defectos", "Meta Defectos", "Crecimiento", "OKR"]
    st.dataframe(style_scorecard(df_f[cols].head(20)), use_container_width=True)

    # Sugerencias automáticas (todos los roles)
    mejorar = []
    if df_f['ROI'].mean() < 0.15:
        mejorar.append("El ROI promedio está debajo de la meta (15%).")
    if df_f['Defectos'].mean() > 2:
        mejorar.append("Demasiados defectos promedio (>2 por proyecto).")
    if df_f['Automatizacion'].mean() < 5:
        mejorar.append("La automatización promedio por proyecto es baja (<5 tareas).")

    if mejorar:
        st.warning("**Sugerencias automáticas:**\n- " + "\n- ".join(mejorar))
    else:
        st.success("¡Todos los KPIs clave superan la meta!")

    st.markdown(
        "> **Análisis rápido:**\n"
        "Prioriza proyectos con ROI bajo. \n"
        "Atiende específicamente a los proyectos o clientes que están en rojo o amarillo, y fortalece capacitación en casos de baja automatización o alto número de defectos.\n"
        "Recuerda ajustar las metas si cambian los objetivos de negocio."
    )

    # Drill-down solo para admin/analista
    if rol in ['admin', 'analista']:
        st.header("Detalle por Proyecto")
        if len(proyectos) > 0:
            proyecto_drill = st.selectbox("Selecciona un proyecto:", proyectos)
            st.dataframe(df[df["Proyecto"] == proyecto_drill])
        else:
            st.info("No hay proyectos para mostrar.")

    st.sidebar.info("""
    Desarrollado con Streamlit y vinculado al DW.
    Los indicadores cambian en tiempo real (al actualizar el CSV).
    """)

    # Botón cerrar sesión
    if st.sidebar.button("Cerrar sesión"):
        st.session_state["log_ok"] = False
        st.session_state["usuario"] = ""
        st.experimental_rerun()

elif btn:
    st.error("Usuario o contraseña incorrectos")
