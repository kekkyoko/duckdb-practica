import duckdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from scipy import stats

# 1.1 Conexión en memoria + semilla global
con = duckdb.connect(database=":memory:")
con.execute("SELECT setseed(0.42)")

# 1.2 Variables base (predictoras, estrategia y ruido)
con.execute("""
CREATE OR REPLACE TABLE base AS
SELECT
    i AS vuelo_id,
    CAST(ROUND(100 + random() * 200) AS INTEGER)   AS pasajeros_abordo,   -- 100 a 300
    CAST(ROUND(500 + random() * 2500) AS INTEGER)  AS distancia_km,       -- 500 a 3000
    CAST(ROUND(random() * 60) AS INTEGER)          AS retraso_min,        -- 0 a 60 (no influye en el ingreso)
    CASE WHEN random() < 0.50 THEN 'Estrategia_A' ELSE 'Estrategia_B' END AS tipo_estrategia,
    (random() * 4.0 - 2.0)                         AS ruido              -- -2.0 a +2.0
FROM generate_series(1, 100) AS t(i)
""")

# Variable de respuesta: ingreso por vuelo (miles de USD)
con.execute("""
CREATE OR REPLACE TABLE telemetria AS
SELECT
    vuelo_id, pasajeros_abordo, distancia_km, retraso_min, tipo_estrategia,
    ROUND(5.0
          + 0.08  * pasajeros_abordo
          + 0.003 * distancia_km
          + CASE WHEN tipo_estrategia = 'Estrategia_B' THEN 4.0 ELSE 0.0 END
          + ruido, 2) AS ingreso_miles_usd
FROM base
""")

# 1.3 Extracción SQL (limpieza) -> DataFrame de pandas
df = con.execute("""
    SELECT *
    FROM telemetria
    WHERE ingreso_miles_usd IS NOT NULL
    ORDER BY vuelo_id
""").df()

print(df.shape)
print(df["tipo_estrategia"].value_counts())
df.head(10)

# Validación de escala: ingresos con sentido operativo y B > A
print(df["ingreso_miles_usd"].describe().round(2))
print()
print(df.groupby("tipo_estrategia")["ingreso_miles_usd"].mean().round(2))

# 2.2 Matriz de correlación de Pearson
cols_num = ["pasajeros_abordo", "distancia_km", "retraso_min", "ingreso_miles_usd"]
corr = df[cols_num].corr(method="pearson")
print(corr.round(3))
print("\nCorrelación con el ingreso (de mayor a menor):")
print(corr["ingreso_miles_usd"].drop("ingreso_miles_usd").sort_values(ascending=False).round(3))

# 2.3 Modelo de regresión OLS
X = df[["pasajeros_abordo", "distancia_km", "retraso_min"]].copy()
X["estrategia_B"] = (df["tipo_estrategia"] == "Estrategia_B").astype(int)
X = sm.add_constant(X)
Y = df["ingreso_miles_usd"]
modelo = sm.OLS(Y, X).fit()

# 2.4 Métricas de calidad
residuos = modelo.resid
rmse = np.sqrt(np.mean(residuos ** 2))

print(f"R2 ajustado : {modelo.rsquared_adj:.4f}  ({modelo.rsquared_adj*100:.1f}% de la variabilidad explicada)")
print(f"RMSE        : {rmse:.3f} miles de USD")
print("\nCoeficientes y p-valores:")
print(pd.DataFrame({"coef": modelo.params, "p_valor": modelo.pvalues,
                    "significativo (p<0.05)": modelo.pvalues < 0.05}).round(5))

# 3.2 Segmentación de grupos
grupo_A = df.loc[df["tipo_estrategia"] == "Estrategia_A", "ingreso_miles_usd"]
grupo_B = df.loc[df["tipo_estrategia"] == "Estrategia_B", "ingreso_miles_usd"]
print(f"n_A = {len(grupo_A)}, media_A = {grupo_A.mean():.2f}")
print(f"n_B = {len(grupo_B)}, media_B = {grupo_B.mean():.2f}")                   

# 3.3 t-Student de dos muestras independientes (cola derecha: B > A)
t_stat, p_valor = stats.ttest_ind(grupo_B, grupo_A, equal_var=True, alternative="greater")

# Intervalo de confianza al 95% para la diferencia de medias (muB - muA)
nA, nB = len(grupo_A), len(grupo_B)
dif = grupo_B.mean() - grupo_A.mean()
sp2 = ((nA - 1) * grupo_A.var(ddof=1) + (nB - 1) * grupo_B.var(ddof=1)) / (nA + nB - 2)
se = np.sqrt(sp2 * (1 / nA + 1 / nB))
t_crit = stats.t.ppf(0.975, df=nA + nB - 2)
ic_inf, ic_sup = dif - t_crit * se, dif + t_crit * se

print(f"Diferencia de medias (B - A): {dif:.3f} miles USD")
print(f"Estadístico t : {t_stat:.4f}")
print(f"p-valor       : {p_valor:.6f}")
print(f"IC 95% de la diferencia: [{ic_inf:.3f}, {ic_sup:.3f}]")

# 3.4 Veredicto inferencial
alpha = 0.05
if p_valor < alpha:
    print(f"[SI] p = {p_valor:.6f} < alpha = {alpha}: se RECHAZA H0.")
    print("La Estrategia B incrementa significativamente el ingreso promedio por vuelo.")
    print("Recomendación: autorizar la inversión para escalar la Estrategia B a toda la red de vuelos.")
else:
    print(f"[NO] p = {p_valor:.6f} >= alpha = {alpha}: NO se rechaza H0.")
    print("No hay evidencia suficiente de que la Estrategia B incremente el ingreso.")
    print("Recomendación: no escalar la inversión por ahora.")

sns.set_theme(style="whitegrid")
fig, ax = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Dashboard: Rendimiento operativo e inferencia de estrategias", fontsize=16, fontweight="bold")

# Gráfica 1: Heatmap de correlación de Pearson
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1,
            square=True, ax=ax[0, 0])
ax[0, 0].set_title("1. Mapa de calor de correlación (Pearson)")

# Gráfica 2: Dispersión + recta OLS con banda de confianza
sns.regplot(data=df, x="pasajeros_abordo", y="ingreso_miles_usd", ci=95,
            scatter_kws={"alpha": 0.6}, line_kws={"color": "red"}, ax=ax[0, 1])
ax[0, 1].set(title="2. Regresión OLS: pasajeros vs. ingreso",
             xlabel="Pasajeros a bordo", ylabel="Ingreso (miles USD)")

# Gráfica 3: Boxplot por estrategia
sns.boxplot(data=df, x="tipo_estrategia", y="ingreso_miles_usd",
            order=["Estrategia_A", "Estrategia_B"], hue="tipo_estrategia",
            palette=["#2563eb", "#d97706"], legend=False, ax=ax[1, 0])
ax[1, 0].set(title=f"3. Ingreso por estrategia (p = {p_valor:.4f})",
             xlabel="Tipo de estrategia", ylabel="Ingreso (miles USD)")

# Gráfica 4: Histograma de residuos + KDE
sns.histplot(residuos, kde=True, bins=15, color="#059669", ax=ax[1, 1])
ax[1, 1].axvline(0, color="red", linestyle="--")
ax[1, 1].set(title="4. Diagnóstico: residuos del modelo", xlabel="Residuo (miles USD)", ylabel="Frecuencia")

plt.tight_layout()
plt.show()    