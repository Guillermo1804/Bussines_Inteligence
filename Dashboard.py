import pandas as pd
import streamlit as st
import plotly.graph_objects as go

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
usuario = st.text_input("Usuario", key="usuario_input")
password = st.text_input("Contraseña", type="password", key="password_input")
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
        st.header("Panel visual de KPI's")

        # KPIs: Calcula los valores
        presupuesto_total = df_f['Presupuesto'].sum()
        desviacion_prom = df_f['Desviacion'].mean()
        roi_prom = df_f['ROI'].mean()
        automatizacion_prom = df_f['Automatizacion'].mean()
        defectos_prom = df_f['Defectos'].mean()
        tareas_total = df_f['Tareas_Total'].sum()
        proyectos_seguridad = df_f['Seguridad'].sum()
        clientes_activos = df_f["Cliente"].nunique()
        sectores_atendidos = df_f["Industria"].nunique()

        # KPI 1: ROI Promedio Gauge
        st.subheader("🔍 Retorno sobre inversión (ROI)")
        st.markdown("Mide la **rentabilidad promedio de los proyectos respecto a la meta**. Queremos ROI >= 0.15 (15%).")
        fig_roi = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = roi_prom,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "ROI promedio"},
            gauge = {
                'axis': {'range': [0, 0.3]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 0.15], 'color': '#FFB6B6'},
                    {'range': [0.15, 0.3], 'color': '#B6FCD5'}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 0.15}
            }
        ))
        st.plotly_chart(fig_roi, use_container_width=True)

        # KPI 2: Automatización promedio por proyecto
        st.subheader("⚡ Nivel de Automatización")
        st.markdown("Indica **cuántas tareas se automatizan por proyecto**. Queremos más de 5 tareas/proyecto.")
        fig_auto = go.Figure(go.Bar(
            x=["Automatización Promedio"], y=[automatizacion_prom],
            marker_color="#4286f4", text=[f"{automatizacion_prom:.1f} tareas"], textposition="auto"
        ))
        fig_auto.update_yaxes(range=[0,10])
        st.plotly_chart(fig_auto, use_container_width=True)

        # KPI 3: Defectos promedio por proyecto
        st.subheader("🛡️ Calidad: Defectos promedio")
        st.markdown("Monitorea la **calidad de los proyectos**. Meta: menos de 2 defectos/proyecto.")
        fig_def = go.Figure(go.Indicator(
            mode = "number+gauge",
            value = defectos_prom,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Defectos promedio"},
            gauge = {
                'axis': {'range': [0, 5]},
                'bar': {'color': "orange"},
                'steps': [
                    {'range': [0, 2], 'color': '#B6FCD5'},
                    {'range': [2, 5], 'color': '#FFB6B6'}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 2}
            }
        ))
        st.plotly_chart(fig_def, use_container_width=True)

        # KPI 4: Distribución de presupuesto (pastel)
        st.subheader("💰 Presupuesto por proyecto")
        st.markdown("Visualiza **cómo se distribuye el presupuesto entre los proyectos** actuales.")
        fig_pie = go.Figure(go.Pie(
            labels=df_f['Proyecto'],
            values=df_f['Presupuesto'],
            hole=0.4
        ))
        st.plotly_chart(fig_pie, use_container_width=True)

        # KPI 5: Clientes activos y sectores atendidos
        st.subheader("🌎 Alcance: Clientes y sectores atendidos")
        st.markdown("Refleja el **alcance y la diversidad del portafolio** actual de proyectos.")
        fig_bar = go.Figure(data=[go.Bar(
            x=["Clientes activos", "Sectores atendidos"],
            y=[clientes_activos, sectores_atendidos],
            marker_color=["#49BEAA", "#FFC947"]
        )])
        st.plotly_chart(fig_bar, use_container_width=True)

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

    df_f['Meta ROI'] = 0.15
    df_f['Meta Automatizacion'] = 5
    df_f['Meta Defectos'] = 2

    cols = ["Proyecto", "Cliente", "ROI", "Meta ROI", "Automatizacion", "Meta Automatizacion",
            "Defectos", "Meta Defectos", "Crecimiento", "OKR"]
    st.dataframe(style_scorecard(df_f[cols].head(20)), use_container_width=True)

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

    # ---------- Cierre de sesión mejorado ----------
    if st.sidebar.button("Cerrar sesión"):
        st.session_state["log_ok"] = False
        st.session_state["usuario"] = ""
        st.session_state["usuario_input"] = ""
        st.session_state["password_input"] = ""
        st.experimental_rerun()

elif btn:
    st.error("Usuario o contraseña incorrectos")
