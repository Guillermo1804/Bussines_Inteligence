DELIMITER //

DROP PROCEDURE IF EXISTS cargar_todo_dw//
CREATE PROCEDURE cargar_todo_dw(
    -- Cliente
    IN p_idCliente INT, IN p_nombre_cliente VARCHAR(100), IN p_email_cliente VARCHAR(100),
    IN p_telefono_cliente VARCHAR(20), IN p_industria_cliente VARCHAR(50), IN p_metrica_base_roi DECIMAL(15,2),

    -- Equipo
    IN p_idEquipo INT, IN p_nombre_equipo VARCHAR(100), IN p_activo_equipo TINYINT(1),

    -- Empleado
    IN p_idEmpleado INT, IN p_nombre_empleado VARCHAR(100), IN p_email_empleado VARCHAR(100),
    IN p_salario_empleado DECIMAL(10,2), IN p_salarioxhora_empleado DECIMAL(10,4), IN p_idEquipo_empleado INT,

    -- Estado Proyecto
    IN p_idEstado INT, IN p_estado VARCHAR(20),

    -- Proyecto (fechas con sufijo _proyecto)
    IN p_idProyecto INT, IN p_nombre_proyecto VARCHAR(100), IN p_tipo_proyecto VARCHAR(20),
    IN p_descripcion_proyecto TEXT, IN p_presupuesto_proyecto DECIMAL(15,2), IN p_costo_real_proyecto DECIMAL(15,2), IN p_metrica_final_roi DECIMAL(15,2),
    IN p_certificacion_seguridad TINYINT(1), IN p_fecha_inicio_proyecto DATE, IN p_fecha_fin_estimada_proyecto DATE, IN p_fecha_fin_real_proyecto DATE,
    IN p_idCliente_proyecto INT, IN p_idEquipo_proyecto INT, IN p_idEstado_proyecto INT,

    -- Tarea (fechas con sufijo _tarea)
    IN p_idTarea INT, IN p_nombre_tarea VARCHAR(50), IN p_descripcion_tarea TEXT, IN p_fecha_creacion_tarea DATETIME,
    IN p_fecha_fin_estimada_tarea DATETIME, IN p_fecha_fin_real_tarea DATETIME, IN p_prioridad_tarea INT,
    IN p_es_automatizacion_tarea TINYINT(1), IN p_es_reutilizado_tarea TINYINT(1), IN p_idProyecto_tarea INT,

    -- Tiempo
    IN p_idTiempo INT, IN p_fecha_completa DATE, IN p_anio INT, IN p_trimestre INT, IN p_mes INT, IN p_semana INT, IN p_dia INT,

    -- Calidad
    IN p_idCalidad INT, IN p_severidad_defecto VARCHAR(10), IN p_tipo_incidente VARCHAR(50), IN p_cert_calidad TINYINT(1),

    -- Hecho proyecto
    IN p_idFact INT, IN p_idProyecto_fact INT, IN p_idCliente_fact INT, IN p_idEquipo_fact INT, IN p_idTiempo_fact INT, IN p_idEstado_fact INT,
    IN p_presupuesto_fact DECIMAL(15,2), IN p_costo_real_fact DECIMAL(15,2), IN p_desviacion_presupuestal DECIMAL(15,2),
    IN p_metrica_base_roi_fact DECIMAL(15,2), IN p_metrica_final_roi_fact DECIMAL(15,2), IN p_tareas_automatizacion_total INT,
    IN p_tareas_reutilizadas_total INT, IN p_defectos_reportados INT, IN p_costo_defecto DECIMAL(15,2), IN p_avance DECIMAL(10,2),
    IN p_horas_estimadas_total DECIMAL(10,2), IN p_horas_reales_total DECIMAL(10,2),

    -- Hecho incidente (fechas con sufijo _hecho)
    IN p_idIncidente INT, IN p_idProyecto_incidente INT, IN p_idTarea_incidente INT, IN p_idCalidad_incidente INT, IN p_fecha_reporte_incidente DATE,
    IN p_severidad_incidente VARCHAR(10), IN p_estado_incidente VARCHAR(10), IN p_costo_correccion_incidente DECIMAL(15,2)
)
BEGIN
    -- Carga cliente
    INSERT IGNORE INTO dim_cliente VALUES (
        p_idCliente, p_nombre_cliente, p_email_cliente, p_telefono_cliente, p_industria_cliente, p_metrica_base_roi
    );

    -- Carga equipo
    INSERT IGNORE INTO dim_equipo VALUES (
        p_idEquipo, p_nombre_equipo, p_activo_equipo
    );

    -- Carga empleado
    INSERT IGNORE INTO dim_empleado VALUES (
        p_idEmpleado, p_nombre_empleado, p_email_empleado, p_salario_empleado, p_salarioxhora_empleado, p_idEquipo_empleado
    );

    -- Carga estado proyecto
    INSERT IGNORE INTO dim_estado_proyecto VALUES (
        p_idEstado, p_estado
    );

    -- Carga proyecto
    INSERT IGNORE INTO dim_proyecto VALUES (
        p_idProyecto, p_nombre_proyecto, p_tipo_proyecto, p_descripcion_proyecto, p_presupuesto_proyecto, p_costo_real_proyecto,
        p_metrica_final_roi, p_certificacion_seguridad, p_fecha_inicio_proyecto, p_fecha_fin_estimada_proyecto, p_fecha_fin_real_proyecto,
        p_idCliente_proyecto, p_idEquipo_proyecto, p_idEstado_proyecto
    );

    -- Carga tarea
    INSERT IGNORE INTO dim_tarea VALUES (
        p_idTarea, p_nombre_tarea, p_descripcion_tarea, p_fecha_creacion_tarea,
        p_fecha_fin_estimada_tarea, p_fecha_fin_real_tarea, p_prioridad_tarea,
        p_es_automatizacion_tarea, p_es_reutilizado_tarea, p_idProyecto_tarea
    );

    -- Carga tiempo
    INSERT IGNORE INTO dim_tiempo VALUES (
        p_idTiempo, p_fecha_completa, p_anio, p_trimestre, p_mes, p_semana, p_dia
    );

    -- Carga calidad
    INSERT IGNORE INTO dim_calidad VALUES (
        p_idCalidad, p_severidad_defecto, p_tipo_incidente, p_cert_calidad
    );

    -- Carga hecho_proyecto
    INSERT IGNORE INTO hecho_proyecto VALUES (
        p_idFact, p_idProyecto_fact, p_idCliente_fact, p_idEquipo_fact, p_idTiempo_fact, p_idEstado_fact,
        p_presupuesto_fact, p_costo_real_fact, p_desviacion_presupuestal, p_metrica_base_roi_fact, p_metrica_final_roi_fact,
        p_tareas_automatizacion_total, p_tareas_reutilizadas_total, p_defectos_reportados, p_costo_defecto, p_avance,
        p_horas_estimadas_total, p_horas_reales_total
    );

    -- Carga hecho_incidente
    INSERT IGNORE INTO hecho_incidente VALUES (
        p_idIncidente, p_idProyecto_incidente, p_idTarea_incidente, p_idCalidad_incidente, p_fecha_reporte_incidente,
        p_severidad_incidente, p_estado_incidente, p_costo_correccion_incidente
    );
END//

DELIMITER ;
