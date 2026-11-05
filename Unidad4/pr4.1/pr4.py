import duckdb
import numpy as np
import pandas as pd
from scipy import stats

# ==============================================================================
# PASO 1: CONEXIÓN A DUCKDB Y GENERACIÓN DE DATOS DETERMINISTAS (SQL)
# ==============================================================================
con = duckdb.connect(database=':memory:')

# Fijamos semilla para que todos los estudiantes obtengan exactamente los mismos datos
con.execute("SELECT setseed(0.42);")

# Creamos la tabla sintética de telemetría con DuckDB SQL
con.execute("""
CREATE TABLE latencia_servidores AS
SELECT
    servidor_id,
    -- Generamos lecturas con una media real simulada de ~52.5 ms (ligeramente superior a la norma)
    ROUND(40 + (random() * 25), 2) AS latencia_ms
FROM generate_series(1, 100) AS t(servidor_id);
""")

# Extraemos los datos desde DuckDB a un DataFrame de Pandas
df_latencia = con.execute("SELECT * FROM latencia_servidores").df()

print("=== PRIMEROS 5 REGISTROS OBTENIDOS DE DUCKDB ===")
print(df_latencia.head())
print("\n" + "=" * 50 + "\n")

# ==============================================================================
# PASO 2: ESTADÍSTICA DESCRIPTIVA BASE (UNIDAD 2 REVISITADA)
# ==============================================================================
n = len(df_latencia)
media_muestral = df_latencia['latencia_ms'].mean()
desv_estandar = df_latencia['latencia_ms'].std(ddof=1)  # ddof=1 para muestra

print("=== ESTADÍSTICOS MUESTRALES ===")
print(f"Tamaño de la muestra (n): {n}")
print(f"Media muestral (x̄):       {media_muestral:.4f} ms")
print(f"Desviación estándar (s):  {desv_estandar:.4f} ms")
print("\n" + "=" * 50 + "\n")

# ==============================================================================
# PASO 3: PLANTEAMIENTO DE LA PRUEBA DE HIPÓTESIS
# ==============================================================================
# H0: mu <= 50 ms (El sistema cumple con la norma especificada)
# H1: mu >  50 ms (El sistema supera el límite de 50 ms; es más lento de lo debido)
mu_0 = 50.0
alpha = 0.05  # Nivel de significancia del 5%

# ==============================================================================
# PASO 4: EJECUCIÓN DE LA PRUEBA T DE STUDENT CON SCIPY.STATS
# ==============================================================================
# Realizamos una prueba t para 1 muestra, de una sola cola (alternative='greater')
t_stat, p_value = stats.ttest_1samp(
    df_latencia['latencia_ms'],
    popmean=mu_0,
    alternative='greater'
)

# Cálculo del Intervalo de Confianza del 95% para la Media Poblacional
intervalo_confianza = stats.t.interval(
    confidence=0.95,
    df=n - 1,
    loc=media_muestral,
    scale=stats.sem(df_latencia['latencia_ms'])
)

print("=== RESULTADOS DEL ANÁLISIS INFERENCIAL (scipy.stats) ===")
print(f"Estadístico t calculado: {t_stat:.4f}")
print(f"Valor p (p-value):        {p_value:.6e}")
print(f"Intervalo de Confianza 95%: [{intervalo_confianza[0]:.4f} ms, {intervalo_confianza[1]:.4f} ms]")

# ==============================================================================
# PASO 5: REGLA DE DECISIÓN Y CONCLUSIÓN EN INGENIERÍA
# ==============================================================================
print("\n=== DECISIÓN DEL ANALISTA DE DATOS ===")
if p_value < alpha:
    print(f"DECISIÓN: Se RECHAZA la Hipótesis Nula (H0) porque p-value ({p_value:.6e}) < alpha ({alpha}).")
    print("CONCLUSIÓN DE INGENIERÍA: Existe evidencia estadística suficiente al 95% de confianza "
          "para afirmar que la latencia media del servidor supera el límite tolerable de 50 ms. "
          "SE RECOMIENDA RECHAZAR EL LOTE DE MEMORIAS.")
else:
    print(f"DECISIÓN: NO se rechaza la Hipótesis Nula (H0) porque p-value ({p_value:.4f}) >= alpha ({alpha}).")
    print("CONCLUSIÓN DE INGENIERÍA: No existe evidencia suficiente para afirmar que el sistema "
          "incumple la norma de 50 ms.")