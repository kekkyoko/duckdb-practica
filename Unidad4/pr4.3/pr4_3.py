"""
Práctica 4.3: Aplicación de técnicas inferenciales en proyectos reales
Asignatura: Análisis y Exploración de Datos (INC-2505)

Proyecto 1: control de calidad de ejes de acero (prueba t de una muestra + IC 95%)
Proyecto 2: eficiencia energética en datacenter (prueba t de Welch, unilateral)

Genera el archivo 'resultados.log' con todos los resultados.
"""
import logging
import sys
from datetime import datetime

import duckdb
import numpy as np
import pandas as pd
import scipy
from scipy import stats

ARCHIVO_LOG = "resultados.log"
ALFA = 0.05

# ---------------------------------------------------------------------
# Registro: consola (igual que en el ejemplo) + archivo .log con fecha y hora
# ---------------------------------------------------------------------
log = logging.getLogger("practica43")
log.setLevel(logging.INFO)
log.handlers.clear()

consola = logging.StreamHandler(sys.stdout)
consola.setFormatter(logging.Formatter("%(message)s"))

archivo = logging.FileHandler(ARCHIVO_LOG, mode="w", encoding="utf-8")
archivo.setFormatter(logging.Formatter("%(asctime)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))

log.addHandler(consola)
log.addHandler(archivo)

log.info("PRÁCTICA 4.3 | Aplicación de técnicas inferenciales en proyectos reales")
log.info(f"Ejecución: {datetime.now():%Y-%m-%d %H:%M:%S} | duckdb {duckdb.__version__} | "
         f"scipy {scipy.__version__} | numpy {np.__version__} | pandas {pd.__version__}")
log.info("")

con = duckdb.connect(database=":memory:")

# =====================================================================
# PROYECTO 1: CONTROL DE CALIDAD DE EJES DE ACERO
# H0: mu = 50.00 mm  |  H1: mu != 50.00 mm  |  alfa = 0.05
# =====================================================================
# 1. Simulación determinista en DuckDB (semilla 0.42)
con.execute("SELECT setseed(0.42);")

con.execute("""
CREATE TABLE control_ejes AS
SELECT
    eje_id,
    -- Proceso simulado con ligera descalibración (media real = 50.08 mm, sigma = 0.15)
    ROUND(50.08 + (random() * 0.30 - 0.15), 3) AS diametro_mm
FROM generate_series(1, 50) AS t(eje_id);
""")

df_ejes = con.execute("SELECT * FROM control_ejes").df()

# 2. Prueba t de una muestra
mu_teorica = 50.00
t_stat, p_value = stats.ttest_1samp(df_ejes["diametro_mm"], popmean=mu_teorica)

# 3. Intervalo de confianza del 95% para la media
media_muestral = df_ejes["diametro_mm"].mean()
sem = stats.sem(df_ejes["diametro_mm"])  # error estándar de la media
ic_inferior, ic_superior = stats.t.interval(
    0.95, df=len(df_ejes) - 1, loc=media_muestral, scale=sem)

log.info("=== PROYECTO 1: CONTROL DE CALIDAD DE EJES DE ACERO ===")
log.info(f"Tamaño de muestra: n = {len(df_ejes)} ejes | Media teórica (H0): {mu_teorica:.2f} mm")
log.info(f"Media Muestral observada: {media_muestral:.4f} mm")
log.info(f"Intervalo de Confianza 95%: [{ic_inferior:.4f} mm, {ic_superior:.4f} mm]")
log.info(f"Estadístico t: {t_stat:.4f} | Valor p: {p_value:.4e}")

if p_value < ALFA:
    log.info("VERDICTO INFERENCIAL: Rechazar H0. La línea está descalibrada. ¡DETENER PRODUCCIÓN!")
else:
    log.info("VERDICTO INFERENCIAL: No se rechaza H0. El proceso opera dentro de tolerancias.")

# =====================================================================
# PROYECTO 2: EFICIENCIA ENERGÉTICA EN DATACENTER
# H0: muA - muB <= 0  |  H1: muA - muB > 0  |  alfa = 0.05
# =====================================================================
# 1. Simulación determinista en DuckDB
con.execute("SELECT setseed(0.42);")

con.execute("""
CREATE TABLE consumo_datacenter AS
SELECT
    hora_id,
    ROUND(120 + (random() * 20), 2) AS consumo_sistema_A_kWh,  -- Tradicional (media ~130 kWh)
    ROUND(108 + (random() * 18), 2) AS consumo_sistema_B_kWh   -- Líquido (media ~117 kWh)
FROM generate_series(1, 60) AS t(hora_id);
""")

df_energia = con.execute("SELECT * FROM consumo_datacenter").df()

# 2. Prueba t de dos muestras independientes (Welch)
t_stat_en, p_val_twoside = stats.ttest_ind(
    df_energia["consumo_sistema_A_kWh"],
    df_energia["consumo_sistema_B_kWh"],
    equal_var=False,
)

# Convertir p-value de dos colas a una cola
p_val_oneside = p_val_twoside / 2 if t_stat_en > 0 else 1.0

# 3. Estimación del ahorro medio
media_A = df_energia["consumo_sistema_A_kWh"].mean()
media_B = df_energia["consumo_sistema_B_kWh"].mean()
diferencia_medias = media_A - media_B

log.info("")
log.info("=== PROYECTO 2: EFICIENCIA ENERGÉTICA EN DATACENTER ===")
log.info(f"Tamaño de muestra: n = {len(df_energia)} horas por sistema")
log.info(f"Consumo Medio Sistema A (Aire):   {media_A:.2f} kWh")
log.info(f"Consumo Medio Sistema B (Líquido): {media_B:.2f} kWh")
log.info(f"Ahorro Estimado Promedio:         {diferencia_medias:.2f} kWh/hora")
log.info(f"Estadístico t: {t_stat_en:.4f} | Valor p (unilateral): {p_val_oneside:.4e}")

if p_val_oneside < ALFA:
    log.info("VERDICTO INFERENCIAL: Rechazar H0. Existe evidencia estadística de que el Sistema B reduce el consumo. APROBAR INVERSIÓN.")
else:
    log.info("VERDICTO INFERENCIAL: No se rechaza H0. La diferencia no es estadísticamente significativa.")

log.info("")
log.info(f"Resultados guardados en '{ARCHIVO_LOG}'")
con.close()