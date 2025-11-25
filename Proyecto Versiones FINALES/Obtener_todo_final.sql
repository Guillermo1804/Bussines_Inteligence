DELIMITER //

DROP PROCEDURE IF EXISTS obtener_todo//
CREATE PROCEDURE obtener_todo()
BEGIN
    -- CLIENTES
    SELECT idCliente, Nombre, Email, Telefono, Industria, MetricaClienteInicial FROM cliente;

    -- EQUIPOS
    SELECT idEquipo, Nombre, Activo FROM equipo;

    -- EMPLEADOS
    SELECT idEmpleado, Nombre, Email, Salario, SalarioxHora, Equipo_idEquipo FROM empleado;

    -- ESTADÍSTICAS DEL PROYECTO
    SELECT idEstadistica, Fecha, Tareas_completadas, Tareas_pendientes, Horas_trabajadas, Costo_diario FROM estadisticas_proyecto;

    -- PROYECTOS
    SELECT idProyecto, Nombre, Descripcion, Tipo, Fecha_inicio, Fecha_fin_estimada, Fecha_fin_real, Estado, Presupuesto, Costo_real, Cliente_idCliente, Estadisticas_Proyecto_idEstadistica, MetricaClienteFinal, CertificacionSeguridad FROM proyecto;

    -- TAREAS
    SELECT idTarea, Titulo, Descripcion, Fecha_creacion, Fecha_fin_estimada, Fecha_fin_real, Estado, Prioridad, Horas_estimadas, EsAutomatizacion, EsReutilizado FROM tarea;

    -- ASIGNACIONES DE TAREA
    SELECT idAsignacion, Tarea_idTarea, Empleado_idEmpleado, Fecha_asignacion, Horas_estimadas, Horas_reales, Proyecto_idProyecto FROM asignacion_tarea;

    -- INCIDENTES
    SELECT idIncidente, Proyecto_idProyecto, Fecha_reporte, Severidad, Estado, idTarea, CostoCorreccion FROM incidente;
END//

DELIMITER ;
