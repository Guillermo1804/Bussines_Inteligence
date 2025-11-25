import streamlit as st
import streamlit_authenticator as stauth

# ===== 1. Configura usuarios y roles =====
usernames = ['admin', 'analista1', 'viewer1']
names = ['Administrador', 'Analista', 'Visualizador']
passwords = ['admin123', 'analista123', 'viewer123']  # SOLO TEXTO PLANO, sin hashing

roles = {
    'admin': 'admin',
    'analista1': 'analista',
    'viewer1': 'viewer'
}

# ——— Usa argumentos por nombre (NO por posición) ———
authenticator = stauth.Authenticate(
    names=names,
    usernames=usernames,
    passwords=passwords,
    cookie_name="dashboardBI",
    key="abcdef",
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.success(f"Bienvenido, {name} ({roles[username]})")
    # Aquí va tu dashboard, KPIs, scorecard, etc.
    authenticator.logout("Cerrar sesión", "sidebar")
elif authentication_status is False:
    st.error("Usuario o contraseña incorrectos")
elif authentication_status is None:
    st.warning("Por favor, ingresa tus datos")
    
    # =========== 2. Carga el DataFrame desde el CSV ===========
    df = pd.read_csv('data_dashboard.csv')

    # =========== 3. Sidebar: Filtros dinámicos ===========
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

    # =========== 4. Paneles de KPIs ===========
    # ------- Solo admin y analista pueden ver todos los KPIs ------- 
    if roles[username] in ['admin', 'analista']:
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

    # --- Los visualizadores solo pueden ver Scorecard y detalles ----
    # =========== 5. Balanced Scorecard con colores/metas ===========
    st.header("Balanced Scorecard y OKRs (con metas y semáforo)")

    def color_scorecard(val, meta, tipo='max'):
        try:
            x = float(val)
        except:
            return ''
        if tipo == 'max':
            if x >= meta: return 'background-color: #B6FCD5'  # verde
            elif x >= 0.7 * meta: return 'background-color: #FDFDB6'  # amarillo
            else: return 'background-color: #FFB6B6'  # rojo
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

    df_f['Meta ROI'] = 0.15
    df_f['Meta Automatizacion'] = 5
    df_f['Meta Defectos'] = 2

    cols = ["Proyecto", "Cliente", "ROI", "Meta ROI", "Automatizacion", "Meta Automatizacion",
            "Defectos", "Meta Defectos", "Crecimiento", "OKR"]
    st.dataframe(style_scorecard(df_f[cols].head(20)), use_container_width=True)

    # =========== 6. Interpretación y recomendaciones ===========
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

    # =========== 7. Drill-down por Proyecto ===========
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

    authenticator.logout("Cerrar sesión", "sidebar")

elif authentication_status is False:
    st.error("Usuario o contraseña incorrectos")
elif authentication_status is None:
    st.warning("Por favor, ingresa tus datos")
