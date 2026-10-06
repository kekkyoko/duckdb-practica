# Proyecto integrador 2

*Asignatura:* Análisis y Exploración de datos (INC-2505)

*Unidad Temática:* Unidad 2. Estadística Descriptiva y Exploratoria

*Nombre del Proyecto:* Simulación y Dragnóstico de Tráfico de Red y Latencia en Servidores mediante DuckDB y Excel

## 1. Datos Generales y Competencia

*Subtemas Integrados:* 
    - 2.1 Medidas de tendencia central y dispersión
    - 2.2 Visualización de datos para análisis exploratorio
    - 2.3 Identificación de patrones y anomalías en los datos

*Competencia a Desarrollar:* Calcular e interpretar medidas de tendencia central y dispersión, así como utilizar herramientas de software (DuckDB y Excel) para explorar conjuntos de datos, caracterizar el comportamiento del sistema e identificar patrones y anomalías.

*Herramientas:* DuckDB (Motor OLAP/SQL) y Microsoft Excel

## 2. Contexto de Ingeniería

Un centro de procesamiento de datos monitorea la latencia en milisegundos (ms) de un servidor de servicios web durante 100 peticiones consecutivas. En condiciones normales de operación, el servidor mantiene un comportamiento estable; sin embargo, eventos imprevistos (bloqueos de memoria, picos de tráfico o ataques de denegación de servicio) generan latencias anómalas.

Objetivo del Proyecto: El estudiante utilizará funciones aleatorias en DuckDB para simular la telemetría, calculará las métricas de dispersión y tendencia central para establecer el patrón base, implementará un algoritmo SQL automatizado basado en la Regla de Tukey (IQR) para detectar anomalías de latencia y exportará el dataset a Microsoft Excel para construir un Diagrama de Caja y Bigotes (Boxplot).

## Entorno virtual
.venv\Scripts\activate

*instalar python-duckdb*
uv pip install duckdb