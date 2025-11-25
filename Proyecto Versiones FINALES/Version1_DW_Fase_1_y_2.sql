-- ===============================================================
-- DATA WAREHOUSE: DW_GESTION_SIMPLE (Fase 1 y 2)
-- Modelo Snowflake con relaciones clave, KPIs y restricciones
-- ===============================================================

CREATE DATABASE IF NOT EXISTS db_Soporte;
USE db_Soporte;

-- ----------------------------------
-- Dimensión Cliente
-- ----------------------------------
CREATE TABLE dim_cliente (
    idCliente INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    telefono VARCHAR(20),
    industria VARCHAR(50),
    metrica_base_roi DECIMAL(15,2)  -- Fase 2: Para KPI de ROI del cliente
);

-- ----------------------------------
-- Dimensión Equipo
-- ----------------------------------
CREATE TABLE dim_equipo (
    idEquipo INT PRIMARY KEY,
    nombre VARCHAR(100),
    activo TINYINT(1)
);

-- ----------------------------------
-- Dimensión Empleado (ligado a equipo)
-- ----------------------------------
CREATE TABLE dim_empleado (
    idEmpleado INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    salario DECIMAL(10,2),
    salarioxhora DECIMAL(10,4),
    idEquipo INT,
    FOREIGN KEY (idEquipo) REFERENCES dim_equipo(idEquipo)
);

-- ----------------------------------
-- Dimensión EstadoProyecto (solo 'Finalizado' y 'Cancelado')
-- ----------------------------------
CREATE TABLE dim_estado_proyecto (
    idEstado INT PRIMARY KEY,
    estado ENUM('Finalizado','Cancelado') NOT NULL
);

-- ----------------------------------
-- Dimensión Proyecto (solamente los permitidos por estado)
-- ----------------------------------
CREATE TABLE dim_proyecto (
    idProyecto INT PRIMARY KEY,
    nombre_proyecto VARCHAR(100),
    tipo_proyecto VARCHAR(20),
    descripcion TEXT,
    presupuesto DECIMAL(15,2),
    costo_real DECIMAL(15,2),
    metrica_final_roi DECIMAL(15,2),            -- Fase 2: Para KPI de ROI final cliente
    certificacion_seguridad TINYINT(1),         -- Fase 2: KPI de cumplimiento de políticas de seguridad
    fecha_inicio DATE,
    fecha_fin_estimada DATE,
    fecha_fin_real DATE,
    idCliente INT,
    idEquipo INT,
    idEstado INT,
    FOREIGN KEY (idCliente) REFERENCES dim_cliente(idCliente),
    FOREIGN KEY (idEquipo) REFERENCES dim_equipo(idEquipo),
    FOREIGN KEY (idEstado) REFERENCES dim_estado_proyecto(idEstado)
);

-- ----------------------------------
-- Dimensión Tarea (ligada a proyecto)
-- ----------------------------------
CREATE TABLE dim_tarea (
    idTarea INT PRIMARY KEY,
    nombre VARCHAR(50),
    descripcion TEXT,
    fecha_creacion DATETIME,
    fecha_fin_estimada DATETIME,
    fecha_fin_real DATETIME,
    prioridad INT,
    es_automatizacion TINYINT(1),              -- Fase 2: KPI % tareas automatización
    es_reutilizado TINYINT(1),                 -- Fase 2: KPI reutilización
    idProyecto INT,
    FOREIGN KEY (idProyecto) REFERENCES dim_proyecto(idProyecto)
);

-- ----------------------------------
-- Dimensión Tiempo (para OLAP)
-- ----------------------------------
CREATE TABLE dim_tiempo (
    idTiempo INT PRIMARY KEY,
    fecha_completa DATE,
    anio INT,
    trimestre INT,
    mes INT,
    semana INT,
    dia INT
);

-- --------------------------------------
-- Dimensión Calidad (Defectos, Seguridad)
-- --------------------------------------
CREATE TABLE dim_calidad (
    idCalidad INT PRIMARY KEY,
    severidad_defecto ENUM('Baja','Media','Alta','Crítica'),
    tipo_incidente VARCHAR(50),
    certificacion_seguridad TINYINT(1)     -- ligado a KPI de cumplimiento
);

-- ------------------------------------------
-- Tabla de Hechos Principal ('Fact Table')
-- Incluye medidas y referencias a todas las dimensiones
-- ------------------------------------------
CREATE TABLE hecho_proyecto (
    idFact INT PRIMARY KEY,
    idProyecto INT,
    idCliente INT,
    idEquipo INT,
    idTiempo INT,
    idEstado INT,
    presupuesto DECIMAL(15,2),
    costo_real DECIMAL(15,2),
    desviacion_presupuestal DECIMAL(15,2),
    metrica_base_roi DECIMAL(15,2),      -- para KPI ROI (inicio)
    metrica_final_roi DECIMAL(15,2),     -- para KPI ROI (final)
    tareas_automatizacion_total INT,     -- KPI F2: cantidad
    tareas_reutilizadas_total INT,       -- KPI F2: cantidad
    defectos_reportados INT,             -- KPI F2: calidad/trazabilidad
    costo_defecto DECIMAL(15,2),
    avance_proyecto DECIMAL(10,2),
    horas_estimadas_total DECIMAL(10,2),
    horas_reales_total DECIMAL(10,2),
    FOREIGN KEY (idProyecto) REFERENCES dim_proyecto(idProyecto),
    FOREIGN KEY (idCliente) REFERENCES dim_cliente(idCliente),
    FOREIGN KEY (idEquipo) REFERENCES dim_equipo(idEquipo),
    FOREIGN KEY (idTiempo) REFERENCES dim_tiempo(idTiempo),
    FOREIGN KEY (idEstado) REFERENCES dim_estado_proyecto(idEstado)
);

-- --------------------------------------
-- Tabla de Incidentes/Defectos (para KPIs Fase 2 y modelo Rayleigh)
-- --------------------------------------
CREATE TABLE hecho_incidente (
    idIncidente INT PRIMARY KEY,
    idProyecto INT,
    idTarea INT,
    idCalidad INT,
    fecha_reporte DATE,
    severidad ENUM('Baja','Media','Alta','Crítica'),
    estado ENUM('Cerrado')NOT NULL,
    costo_correccion DECIMAL(15,2),
    FOREIGN KEY (idProyecto) REFERENCES dim_proyecto(idProyecto),
    FOREIGN KEY (idTarea) REFERENCES dim_tarea(idTarea),
    FOREIGN KEY (idCalidad) REFERENCES dim_calidad(idCalidad)
);

