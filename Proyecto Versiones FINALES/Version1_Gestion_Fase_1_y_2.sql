-- -----------------------------------------------------------
-- Base de datos: db_gestion (Modelo Snowflake, FASE 2)
-- Documentada y con los KPI de Fase 2 resaltados
-- -----------------------------------------------------------

CREATE DATABASE IF NOT EXISTS db_gestion DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE db_gestion;

-- -------------------------
-- DIMENSIÓN CLIENTE
-- Permite calcular el KPI "Crecimiento por industria o sector"
-- y ahora KPI ROI del Cliente (FASE 2)
-- -------------------------
CREATE TABLE cliente (
    idCliente INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL,
    Telefono VARCHAR(20) DEFAULT NULL,
    Industria VARCHAR(50) DEFAULT NULL, -- KPI Fase 1: Industria
    MetricaClienteInicial DECIMAL(15,2) DEFAULT NULL  -- FASE 2 NUEVO: Soportar el cálculo del ROI del Cliente (KPI 8)
);

-- -------------------------
-- DIMENSIÓN EQUIPO
-- Permite asociar empleados a equipos para análisis de desempeño grupal
-- -------------------------
CREATE TABLE equipo (
    idEquipo INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Activo TINYINT(4) NOT NULL
);

-- -------------------------
-- DIMENSIÓN EMPLEADO
-- Soporta futuros KPIs como análisis de eficiencia y costes individuales/grupales
-- -------------------------
CREATE TABLE empleado (
    idEmpleado INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Salario DECIMAL(10,2) NOT NULL,
    SalarioxHora DECIMAL(10,4) DEFAULT NULL, -- (Preparado para KPIs: Eficiencia/costo por hora)
    Equipo_idEquipo INT,
    FOREIGN KEY (Equipo_idEquipo) REFERENCES equipo(idEquipo)
);

-- -------------------------
-- DIMENSIÓN TAREA
-- Soporta KPIs de productividad y eficiencia
-- Además... KPI “automatización” (11) y “reutilización” (10) (FASE 2 nuevo)
-- -------------------------
CREATE TABLE tarea (
    idTarea INT AUTO_INCREMENT PRIMARY KEY,
    Titulo VARCHAR(200) NOT NULL,
    Descripcion TEXT DEFAULT NULL,
    Fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Fecha_fin_estimada DATE DEFAULT NULL,
    Fecha_fin_real DATE DEFAULT NULL,
    Estado ENUM('PENDIENTE','EN_PROGRESO','EN_REVISION','COMPLETADA','BLOQUEADA') NOT NULL DEFAULT 'PENDIENTE',
    Prioridad ENUM('BAJA','MEDIA','ALTA','CRITICA') NOT NULL DEFAULT 'MEDIA',
    Horas_estimadas INT NOT NULL DEFAULT 0, -- KPI: Horas estimadas vs reales en asignacion_tarea
    EsAutomatizacion TINYINT(1) DEFAULT 0, -- FASE 2 NUEVO: Marcar si la tarea involucra automatización (KPI 11)
    EsReutilizado TINYINT(1) DEFAULT 0     -- FASE 2 NUEVO: Marcar si la tarea es reutilizable (KPI 10)
);

-- -------------------------
-- DIMENSIÓN ESTADÍSTICAS DEL PROYECTO
-- Opcional para granularidad diaria e insumos para KPIs de gestión
-- -------------------------
CREATE TABLE estadisticas_proyecto (
    idEstadistica INT AUTO_INCREMENT PRIMARY KEY,
    Fecha DATE NOT NULL,
    Tareas_completadas INT NOT NULL DEFAULT 0, -- KPI: Productividad
    Tareas_pendientes INT NOT NULL DEFAULT 0,
    Horas_trabajadas DECIMAL(8,2) NOT NULL DEFAULT 0.00,
    Costo_diario DECIMAL(10,2) NOT NULL DEFAULT 0.00 -- KPI: Control de costos del proyecto
);

-- -------------------------
-- DIMENSIÓN PROYECTO
-- Aquí se soportan varios de los KPIs principales:
--  Fase 1:
--   - KPI Financiero: Desviación presupuestal
--   - KPI Cliente: Cumplimiento de fechas (estimadas vs reales)
--   - KPI Estado finalizado (control y planificación)
--   - KPI Diversidad tecnológica “Tipo”
--  Fase 2 NUEVO:
--   - Métrica final para ROI del cliente (8)
--   - Cumplimiento de políticas de datos/seguridad (12)
-- -------------------------
CREATE TABLE proyecto (
    idProyecto INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Descripcion TEXT DEFAULT NULL,
    Tipo ENUM('WEB','MOVIL','ESCRITORIO','EMBEBIDO') NOT NULL, -- KPI: Diversidad tecnológica
    Fecha_inicio DATE NOT NULL,
    Fecha_fin_estimada DATE NOT NULL, -- KPI: Fecha estimada
    Fecha_fin_real DATE DEFAULT NULL, -- KPI: Hitos/entregas cumplidas
    Estado ENUM('ACTIVO','CANCELADO','EN_PRUEBAS','EN_PLANEACION','FINALIZADO','PAUSADO') NOT NULL DEFAULT 'EN_PLANEACION',
    Presupuesto DECIMAL(15,2) NOT NULL, -- KPI: Presupuesto asignado
    Costo_real DECIMAL(15,2) DEFAULT 0.00, -- KPI: Costo final
    Cliente_idCliente INT NOT NULL, -- Relación para KPI crecimiento por cliente
    Estadisticas_Proyecto_idEstadistica INT,
    MetricaClienteFinal DECIMAL(15,2) DEFAULT NULL,          -- FASE 2 NUEVO: Valor de negocio después del uso (KPI 8)
    CertificacionSeguridad TINYINT(1) DEFAULT 0,             -- FASE 2 NUEVO: Cumplimiento de políticas de seguridad/datos (KPI 12)
    FOREIGN KEY (Cliente_idCliente) REFERENCES cliente(idCliente) ON UPDATE CASCADE,
    FOREIGN KEY (Estadisticas_Proyecto_idEstadistica) REFERENCES estadisticas_proyecto(idEstadistica)
);

-- -------------------------
-- TABLA DE HECHOS: ASIGNACIÓN DE TAREA
-- Soporta KPIs:
--  - Fase 1: esfuerzo estimado vs real, asignación colaborativa
-- -------------------------
CREATE TABLE asignacion_tarea (
    idAsignacion INT AUTO_INCREMENT PRIMARY KEY,
    Tarea_idTarea INT NOT NULL,
    Empleado_idEmpleado INT NOT NULL,
    Fecha_asignacion DATE NOT NULL,
    Horas_estimadas INT NOT NULL, -- KPI: Esfuerzo estimado
    Horas_reales INT DEFAULT NULL, -- KPI: Esfuerzo real
    Proyecto_idProyecto INT NOT NULL,
    UNIQUE KEY asignacion_unica (Tarea_idTarea, Empleado_idEmpleado),
    FOREIGN KEY (Tarea_idTarea) REFERENCES tarea(idTarea) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (Empleado_idEmpleado) REFERENCES empleado(idEmpleado) ON UPDATE CASCADE,
    FOREIGN KEY (Proyecto_idProyecto) REFERENCES proyecto(idProyecto)
);

-- -------------------------
-- TABLA NUEVA: INCIDENTE
-- FASE 2 NUEVO:
-- Soporta KPIs de calidad/tasa de defectos/correcciones y analítica predictiva (KPI 9, 13)
-- -------------------------
CREATE TABLE incidente (
    idIncidente INT AUTO_INCREMENT PRIMARY KEY,
    Proyecto_idProyecto INT NOT NULL,               -- Relación al proyecto donde ocurre el incidente
    Fecha_reporte DATE NOT NULL,                    -- Fecha de reporte del incidente
    Severidad ENUM('BAJA','MEDIA','ALTA','CRITICA') NOT NULL, -- Nivel de gravedad (para segmentación de calidad)
    Estado ENUM('ABIERTO','EN_REVISION','CERRADO') NOT NULL DEFAULT 'ABIERTO',
    idTarea INT DEFAULT NULL,                       -- Opcional, tarea involucrada
    CostoCorreccion DECIMAL(15,2) DEFAULT NULL,     -- Costo de la corrección
    FOREIGN KEY (Proyecto_idProyecto) REFERENCES proyecto(idProyecto),
    FOREIGN KEY (idTarea) REFERENCES tarea(idTarea)
);
