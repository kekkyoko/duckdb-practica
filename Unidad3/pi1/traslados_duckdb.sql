-- Limpieza de tiempos de traslado: datos SIMULADOS, minutos de ida.
-- Ejecutar todo en orden en DuckDB. Solo reemplaza tablas de este ejercicio.
CREATE OR REPLACE TABLE traslado_muestra (
 id_estudiante INTEGER PRIMARY KEY,
 tiempo_min DOUBLE
);
INSERT INTO traslado_muestra VALUES
(1,15),(2,20),(3,22),(4,25),(5,28),(6,30),(7,30),(8,32),
(9,35),(10,35),(11,38),(12,40),(13,40),(14,42),(15,45),
(16,45),(17,48),(18,50),(19,52),(20,55),(21,60),(22,65),
(23,70),(24,120),(25,180),(26,240),(27,NULL),(28,NULL),
(29,-10),(30,0);

-- 1. Diagnóstico: COUNT(*) incluye nulos; COUNT(columna) no.
SELECT COUNT(*) AS total,
 COUNT(*) - COUNT(tiempo_min) AS nulos,
 COUNT(*) FILTER (WHERE tiempo_min <= 0) AS invalidos,
 MIN(tiempo_min) AS minimo_original,
 MAX(tiempo_min) AS maximo_original
FROM traslado_muestra;

-- 2. Regla del ejercicio: el estudiante se desplaza al campus y tarda > 0.
-- Conservar original; convertir valores inválidos a NULL.
CREATE OR REPLACE TABLE traslado_validado AS
SELECT id_estudiante, tiempo_min AS tiempo_original,
 CASE WHEN tiempo_min > 0 THEN tiempo_min ELSE NULL END AS tiempo_valido,
 CASE WHEN tiempo_min IS NULL THEN 'nulo_original'
      WHEN tiempo_min <= 0 THEN 'invalido'
      ELSE 'observado' END AS origen
FROM traslado_muestra;

-- 3. Estimar mediana y cuartiles SOLO con observaciones válidas.
-- quantile_cont usa interpolación; no necesariamente coincide con
-- el método manual de medianas de mitades. Se mantiene esta convención.
CREATE OR REPLACE TABLE traslado_parametros AS
WITH resumen AS (
 SELECT COUNT(tiempo_valido) AS n_validos,
 MEDIAN(tiempo_valido) AS mediana,
 QUANTILE_CONT(tiempo_valido, 0.25) AS q1,
 QUANTILE_CONT(tiempo_valido, 0.75) AS q3
 FROM traslado_validado
)
SELECT *, q3-q1 AS ric,
 q1-1.5*(q3-q1) AS limite_inferior,
 q3+1.5*(q3-q1) AS limite_superior
FROM resumen;
SELECT * FROM traslado_parametros;
-- Si n_validos = 0 o RIC = 0, revisar datos antes de aplicar este método.

-- 4. Detectar atípicos observados con las cercas de Tukey.
SELECT v.id_estudiante, v.tiempo_original, p.limite_inferior,
 p.limite_superior
FROM traslado_validado v CROSS JOIN traslado_parametros p
WHERE v.tiempo_valido < p.limite_inferior
   OR v.tiempo_valido > p.limite_superior
ORDER BY v.id_estudiante;

-- 5. Imputar nulos con mediana; después aplicar capping.
-- CASE explícito conserva NULL si no hubiera mediana disponible.
CREATE OR REPLACE TABLE traslado_limpio AS
WITH imputacion AS (
 SELECT v.*, p.mediana, p.limite_inferior, p.limite_superior,
 COALESCE(v.tiempo_valido, p.mediana) AS tiempo_imputado,
 v.tiempo_valido IS NULL AS fue_imputado,
 CASE WHEN v.tiempo_valido IS NULL THEN FALSE
      ELSE v.tiempo_valido < p.limite_inferior
        OR v.tiempo_valido > p.limite_superior END AS es_atipico
 FROM traslado_validado v CROSS JOIN traslado_parametros p
)
SELECT *,
 CASE WHEN tiempo_imputado < limite_inferior THEN limite_inferior
      WHEN tiempo_imputado > limite_superior THEN limite_superior
      ELSE tiempo_imputado END AS tiempo_final
FROM imputacion;
SELECT id_estudiante, tiempo_original, origen, fue_imputado,
 es_atipico, tiempo_imputado, tiempo_final
FROM traslado_limpio ORDER BY id_estudiante;

-- 6. Comparar etapas; media cruda contiene los valores inválidos.
WITH etapas AS (
 SELECT '1. Original' AS etapa, tiempo_min AS tiempo FROM traslado_muestra
 UNION ALL
 SELECT '2. Valido observado', tiempo_valido FROM traslado_validado
 UNION ALL
 SELECT '3. Imputado', tiempo_imputado FROM traslado_limpio
 UNION ALL
 SELECT '4. Capping', tiempo_final FROM traslado_limpio
)
SELECT etapa, COUNT(*) AS filas, COUNT(tiempo) AS disponibles,
 ROUND(AVG(tiempo),2) AS media, MEDIAN(tiempo) AS mediana,
 MIN(tiempo) AS minimo, MAX(tiempo) AS maximo,
 ROUND(STDDEV_SAMP(tiempo),2) AS desviacion_muestral
FROM etapas GROUP BY etapa ORDER BY etapa;

-- 7. Verificación final: esperamos 30, 0, 0, 4, 3.
SELECT COUNT(*) AS total,
 COUNT(*) FILTER (WHERE tiempo_final IS NULL) AS nulos_finales,
 COUNT(*) FILTER (WHERE tiempo_final <= 0) AS invalidos_finales,
 COUNT(*) FILTER (WHERE fue_imputado) AS imputados,
 COUNT(*) FILTER (WHERE es_atipico) AS atipicos
FROM traslado_limpio;
