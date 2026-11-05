import duckdb
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.stats.stattools import durbin_watson
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# =====================================================================
# PASO 1: SIMULACIÓN DE DATOS RELACIONALES EN DUCKDB (REPRODUCIBLE)
# =====================================================================
con = duckdb.connect(database=':memory:')

# Semilla determinista (el valor debe estar entre -1 y 1)
con.execute("SELECT setseed(0.42)")

# Query 1: crear la tabla de telemetría de agua potable
con.execute("""
CREATE TABLE telemetria_agua AS
WITH base AS (
    SELECT
        residencia_id,
        ROUND(20 + (random() * 11), 2)          AS temperatura_max,   -- 20 a 31 °C
        ROUND(50 + (random() * 40), 2)          AS humedad_max,       -- 50 a 90 %
        ROUND(3 + (random() * 4))::DOUBLE       AS personas_familia,  -- 3 a 7 hab/vivienda
        ROUND(0.2 + (random() * 1.8), 2)        AS consumo_bidon_pc,  -- 0.2 a 2.0 lt/hab-día
        random()                                AS ruido
    FROM generate_series(1, 100) AS t(residencia_id)
)
SELECT
    residencia_id,
    temperatura_max,
    humedad_max,
    personas_familia,
    consumo_bidon_pc,
    -- Modelo generador con ruido gaussiano aproximado
    ROUND(
        94.5
        + 2.5  * temperatura_max
        - 0.8  * humedad_max
        - 5.2  * personas_familia
        + 15.0 * consumo_bidon_pc
        + (ruido - 0.5) * 7
    , 2) AS cpc_consumo
FROM base
""")

# Query 2: extraer el dataset a Pandas
df_agua = con.execute("SELECT * FROM telemetria_agua").df()

print("=== PASO 1: PRIMEROS 5 REGISTROS OBTENIDOS DE DUCKDB ===")
print(df_agua.head())
print("\n" + "=" * 70 + "\n")

# =====================================================================
# PASO 2: MATRIZ DE CORRELACIÓN DE PEARSON (r)
# =====================================================================
matriz_correlacion = df_agua.drop(columns=['residencia_id']).corr(method='pearson')

print("=== PASO 2: MATRIZ DE CORRELACIÓN DE PEARSON (r) ===")
print(matriz_correlacion.round(4))
print("\nCorrelación lineal de cada variable con la respuesta 'cpc_consumo':")
print(matriz_correlacion['cpc_consumo'].drop('cpc_consumo').round(4))
print("\n" + "=" * 70 + "\n")

# =====================================================================
# PASO 3: REGRESIÓN LINEAL MÚLTIPLE CON STATSMODELS (OLS)
# =====================================================================
X = df_agua[['temperatura_max', 'humedad_max', 'personas_familia', 'consumo_bidon_pc']]
Y = df_agua['cpc_consumo']

X_const = sm.add_constant(X)          # término independiente (Beta 0)
modelo_ols = sm.OLS(Y, X_const).fit()

print("=== PASO 3: RESUMEN DEL MODELO OLS (statsmodels) ===")
print(modelo_ols.summary())
print("\n" + "=" * 70 + "\n")

# =====================================================================
# PASO 4: VALIDACIÓN DE SUPUESTOS DE REGRESIÓN EN LOS RESIDUOS
# =====================================================================
residuos = modelo_ols.resid

# 1) Normalidad: Shapiro-Wilk
stat_sw, p_sw = stats.shapiro(residuos)
# 2) Independencia: Durbin-Watson
dw_stat = durbin_watson(residuos)

print("=== PASO 4: DIAGNÓSTICO DE RESIDUOS Y SUPUESTOS ===")
print(f"1. Prueba de Normalidad (Shapiro-Wilk): Estadístico = {stat_sw:.4f}, valor p = {p_sw:.4f}")
if p_sw > 0.05:
    print("   -> CONCLUSIÓN: los residuos cumplen con el supuesto de NORMALIDAD (p > 0.05).")
else:
    print("   -> CONCLUSIÓN: se rechaza la normalidad de los residuos (p <= 0.05).")

print(f"2. Estadístico Durbin-Watson (Independencia): {dw_stat:.4f} "
      f"(Valores entre 1.5 y 2.5 indican ausencia de autocorrelación).")
print("\n" + "=" * 70 + "\n")

# =====================================================================
# PASO 5: EVALUACIÓN PREDICTIVA CON SCIKIT-LEARN
# =====================================================================
modelo_sk = LinearRegression()
modelo_sk.fit(X, Y)

y_pred = modelo_sk.predict(X)

r2_sk = r2_score(Y, y_pred)
rmse_sk = np.sqrt(mean_squared_error(Y, y_pred))

b0 = modelo_sk.intercept_
b1, b2, b3, b4 = modelo_sk.coef_

print("=== PASO 5: MÉTRICAS DE RENDIMIENTO DEL MODELO (scikit-learn) ===")
print(f"Coeficiente de Determinación (R²):      {r2_sk*100:.2f}%")
print(f"Error Cuadrático Medio Raíz (RMSE):     {rmse_sk:.4f} lt/hab-día")
print("Ecuación del Modelo Ajustado:")
print(f"CPC = {b0:.2f} + ({b1:.2f} * Temp) + ({b2:.2f} * Humedad) "
      f"+ ({b3:.2f} * Personas) + ({b4:.2f} * Bidon)")

# =====================================================================
# PASO 6: PANEL DE GRÁFICAS DE DIAGNÓSTICO
# =====================================================================
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('Panel de Diagnóstico Visual: Regresión Lineal Múltiple (Subtema 4.2)',
             fontsize=16, fontweight='bold')

# 1. Mapa de calor de correlación
sns.heatmap(matriz_correlacion, annot=True, fmt=".2f", cmap="coolwarm",
            cbar=True, ax=axes[0, 0])
axes[0, 0].set_title('1. Matriz de Correlación de Pearson (r)')

# 2. Scatter: humedad vs consumo
sns.regplot(data=df_agua, x='humedad_max', y='cpc_consumo', color='b', ax=axes[0, 1],
            line_kws={'color': 'red', 'linewidth': 2})
axes[0, 1].set_title('2. Tendencia: Humedad Máx vs Consumo')
axes[0, 1].set_xlabel('Humedad Máxima (%)')
axes[0, 1].set_ylabel('CPC Consumo (lt/hab-día)')

# 3. Reales vs predichos
axes[0, 2].scatter(y_pred, Y, alpha=0.7, color='teal')
axes[0, 2].plot([Y.min(), Y.max()], [Y.min(), Y.max()], 'r--', lw=2)
axes[0, 2].set_title(f'3. Val. Reales vs Predichos (R² = {r2_sk*100:.1f}%)')
axes[0, 2].set_xlabel('CPC Predicho (ŷ)')
axes[0, 2].set_ylabel('CPC Real (y)')

# 4. Residuos vs ajustados (homocedasticidad)
axes[1, 0].scatter(y_pred, residuos, color='purple', alpha=0.6)
axes[1, 0].axhline(y=0, color='r', linestyle='--', lw=2)
axes[1, 0].set_title('4. Residuos vs Ajustados (Homocedasticidad)')
axes[1, 0].set_xlabel('Valores Predichos (ŷ)')
axes[1, 0].set_ylabel('Residuos (e = y - ŷ)')

# 5. Q-Q normal de residuos
sm.qqplot(residuos, line='45', fit=True, ax=axes[1, 1])
axes[1, 1].set_title('5. Gráfico Q-Q Normal (Residuos)')

# Ocultar la celda sobrante
axes[1, 2].axis('off')

plt.tight_layout()
plt.show()