import duckdb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import streamlit as st
from scipy import stats

st.set_page_config(page_title="Torre de Control · Aerolínea", page_icon="✈",
                   layout="wide", initial_sidebar_state="collapsed")

NAVY, BLUE, SKY, GOLD, RED, GREEN = "#0b2545", "#134074", "#1d8fd6", "#f5b700", "#e63946", "#2a9d8f"

# ---------------------------------------------------------------
# Estilo visual: sensación de aerolínea, sin barra lateral ni scroll
# ---------------------------------------------------------------
st.markdown(f"""
<style>
.stApp {{background: linear-gradient(180deg,#cfe8fb 0%,#eaf4fc 35%,#f8fbff 100%);}}
.block-container {{padding: 1.2rem 2rem 2.5rem 2rem; max-width: 100%;}}
#MainMenu, header, footer {{visibility: hidden; height: 0;}}
[data-testid="stSidebar"], [data-testid="collapsedControl"] {{display: none;}}
[data-testid="stVerticalBlock"] {{gap: 1.1rem;}}

.hero {{background: linear-gradient(100deg,{NAVY} 0%,{BLUE} 60%,#1d6fa5 100%);
        border-radius: 14px; padding: 16px 26px; display: flex;
        justify-content: space-between; align-items: center; color: #fff;
        box-shadow: 0 4px 14px rgba(11,37,69,.28);}}
.hero h1 {{font-size: 1.35rem; margin: 0; padding: 0; color: #fff; letter-spacing: .5px;}}
.hero small {{opacity: .8;}}
.runway {{letter-spacing: 7px; opacity: .65; font-size: .9rem;}}
.tag {{background: {GOLD}; color: {NAVY}; padding: 3px 11px; border-radius: 6px;
       font-weight: 800; font-size: .75rem; letter-spacing: 1.5px;}}

.pass {{background: #fff; border-radius: 12px; border-left: 7px solid {BLUE};
        padding: 14px 18px; box-shadow: 0 2px 10px rgba(11,37,69,.12);
        position: relative; margin-bottom: 2px;}}
.pass:after {{content: "✈"; position: absolute; right: 12px; top: 8px; color: #b9cfe4; font-size: 1.2rem;}}
.pass .lab {{font-size: .66rem; letter-spacing: 1.6px; text-transform: uppercase; color: #6b7a90;}}
.pass .val {{font-size: 1.6rem; font-weight: 800; color: {NAVY}; line-height: 1.15;}}
.pass .sub {{font-size: .72rem; color: {SKY}; font-weight: 600;}}
.pass.gold {{border-left-color: {GOLD};}}
.pass.green {{border-left-color: {GREEN};}}

.verdict {{border-radius: 12px; padding: 14px 18px; height: 100%; color: #fff; font-weight: 700; font-size: .85rem;
           box-shadow: 0 2px 10px rgba(11,37,69,.18); border: 2px dashed rgba(255,255,255,.55);}}
.verdict.ok {{background: linear-gradient(120deg,#1b7f6f,{GREEN});}}
.verdict.no {{background: linear-gradient(120deg,#b07d00,{GOLD}); color: {NAVY};}}
.verdict .big {{font-size: 1rem; letter-spacing: 1px; display: block; margin-bottom: 2px;}}

[data-testid="stImage"] img, [data-testid="stImageContainer"] img {{
    border-radius: 12px; box-shadow: 0 2px 10px rgba(11,37,69,.14); background: #fff;}}
.seccion {{margin: .8rem 0 .2rem; padding-bottom: 5px; font-weight: 800; font-size: .78rem;
           letter-spacing: 2px; text-transform: uppercase; color: {BLUE};
           border-bottom: 2px dashed #b9cfe4;}}
label p {{font-size: .78rem !important; font-weight: 700; color: {NAVY};}}
</style>
""", unsafe_allow_html=True)

sns.set_theme(style="whitegrid", rc={"axes.titlesize": 9, "axes.titleweight": "bold",
                                      "axes.labelsize": 8, "xtick.labelsize": 7.5,
                                      "ytick.labelsize": 7.5, "axes.titlecolor": NAVY})


# ---------------------------------------------------------------
# Datos (Fase 1): simulación determinista con DuckDB
# ---------------------------------------------------------------
@st.cache_data
def cargar_datos() -> pd.DataFrame:
    con = duckdb.connect(database=":memory:")
    con.execute("SELECT setseed(0.42)")
    con.execute("""
        CREATE TABLE base AS
        SELECT
            i AS vuelo_id,
            CAST(ROUND(100 + random() * 200) AS INTEGER)  AS pasajeros_abordo,
            CAST(ROUND(500 + random() * 2500) AS INTEGER) AS distancia_km,
            CAST(ROUND(random() * 60) AS INTEGER)         AS retraso_min,
            CASE WHEN random() < 0.50 THEN 'Estrategia_A' ELSE 'Estrategia_B' END AS tipo_estrategia,
            (random() * 4.0 - 2.0) AS ruido
        FROM generate_series(1, 100) AS t(i)
    """)
    con.execute("""
        CREATE TABLE telemetria AS
        SELECT vuelo_id, pasajeros_abordo, distancia_km, retraso_min, tipo_estrategia,
               ROUND(5.0 + 0.08 * pasajeros_abordo + 0.003 * distancia_km
                     + CASE WHEN tipo_estrategia = 'Estrategia_B' THEN 4.0 ELSE 0.0 END
                     + ruido, 2) AS ingreso_miles_usd
        FROM base
    """)
    return con.execute("SELECT * FROM telemetria ORDER BY vuelo_id").df()


df = cargar_datos()

# ---------------------------------------------------------------
# Encabezado
# ---------------------------------------------------------------
st.markdown("""
<div class="hero">
  <div>
    <h1>✈ TORRE DE CONTROL · Rendimiento Operativo de Vuelos</h1>
    <small>Proyecto Integrador U4 · Análisis y Exploración de Datos (INC-2505)</small>
  </div>
  <div style="text-align:right">
    <span class="tag">VUELO INC-2505</span><br>
    <span class="runway">— — — — — ✈</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Orden de la página: KPIs arriba, luego controles, luego gráficas.
# Los contenedores reservan su lugar; los KPIs se llenan después de calcular.
zona_kpi = st.container()
zona_filtros = st.container()

# ---------------------------------------------------------------
# Controles (Fase 5, punto 2)
# ---------------------------------------------------------------
with zona_filtros:
    st.markdown('<div class="seccion">Controles de vuelo</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([1.2, 1.4, 1.4], gap="large")
    with f1:
        estrategias = st.multiselect("Tipo de estrategia", ["Estrategia_A", "Estrategia_B"],
                                     default=["Estrategia_A", "Estrategia_B"])
    with f2:
        pax_min, pax_max = st.slider("Pasajeros a bordo",
                                     int(df.pasajeros_abordo.min()), int(df.pasajeros_abordo.max()),
                                     (int(df.pasajeros_abordo.min()), int(df.pasajeros_abordo.max())))
    with f3:
        dist_min, dist_max = st.slider("Distancia (km)",
                                       int(df.distancia_km.min()), int(df.distancia_km.max()),
                                       (int(df.distancia_km.min()), int(df.distancia_km.max())))

dff = df[
    df.tipo_estrategia.isin(estrategias)
    & df.pasajeros_abordo.between(pax_min, pax_max)
    & df.distancia_km.between(dist_min, dist_max)
]

if len(dff) < 10:
    st.warning("Hay muy pocos vuelos con estos filtros (mínimo 10). Amplía los rangos o selecciona más estrategias.")
    st.stop()

# ---------------------------------------------------------------
# Modelos sobre los datos filtrados
# ---------------------------------------------------------------
X = sm.add_constant(dff[["pasajeros_abordo", "distancia_km"]])
modelo = sm.OLS(dff["ingreso_miles_usd"], X).fit()
residuos = modelo.resid

grupo_A = dff.loc[dff.tipo_estrategia == "Estrategia_A", "ingreso_miles_usd"]
grupo_B = dff.loc[dff.tipo_estrategia == "Estrategia_B", "ingreso_miles_usd"]
hay_ambos = len(grupo_A) >= 2 and len(grupo_B) >= 2
if hay_ambos:
    t_stat, p_valor = stats.ttest_ind(grupo_B, grupo_A, equal_var=True, alternative="greater")
    dif = grupo_B.mean() - grupo_A.mean()


def tarjeta(etiqueta, valor, sub, clase=""):
    return (f'<div class="pass {clase}"><div class="lab">{etiqueta}</div>'
            f'<div class="val">{valor}</div><div class="sub">{sub}</div></div>')


# ---------------------------------------------------------------
# Indicadores (Fase 5, punto 1) - se dibujan en la zona de arriba
# ---------------------------------------------------------------
with zona_kpi:
    st.markdown('<div class="seccion">Indicadores clave</div>', unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4, gap="large")
    k1.markdown(tarjeta("Ingreso promedio global", f"${dff.ingreso_miles_usd.mean():.2f}k",
                        f"USD por vuelo · {len(dff)} vuelos"), unsafe_allow_html=True)
    k2.markdown(tarjeta("R² ajustado del modelo", f"{modelo.rsquared_adj * 100:.1f}%",
                        "Variabilidad explicada", "gold"), unsafe_allow_html=True)
    if hay_ambos:
        k3.markdown(tarjeta("P-valor prueba t", f"{p_valor:.6f}",
                            "Significativo (p < 0.05)" if p_valor < 0.05 else "No significativo",
                            "green"), unsafe_allow_html=True)
        if p_valor < 0.05:
            k4.markdown(f'<div class="verdict ok"><span class="big">✔ DESPEGUE AUTORIZADO</span>'
                        f'Estrategia B: +{dif:.2f}k USD por vuelo. Escalar a toda la red.</div>',
                        unsafe_allow_html=True)
        else:
            k4.markdown('<div class="verdict no"><span class="big">⏸ EN REVISIÓN</span>'
                        'Sin evidencia suficiente de que la Estrategia B mejore el ingreso.</div>',
                        unsafe_allow_html=True)
    else:
        k3.markdown(tarjeta("P-valor prueba t", "N/D", "Selecciona A y B", "green"),
                    unsafe_allow_html=True)
        k4.markdown('<div class="verdict no"><span class="big">! FALTA UN GRUPO</span>'
                    'Selecciona ambas estrategias para ver el veredicto.</div>',
                    unsafe_allow_html=True)

# ---------------------------------------------------------------
# Gráficas: cuadrícula 2x2 (Fase 4 + Fase 5)
# ---------------------------------------------------------------
st.markdown('<div class="seccion">Análisis de datos</div>', unsafe_allow_html=True)

FIG = (6.2, 3.1)
fila1 = st.columns(2, gap="large")
fila2 = st.columns(2, gap="large")

# Gráfica 1: Heatmap de correlación
with fila1[0]:
    corr = dff[["pasajeros_abordo", "distancia_km", "retraso_min", "ingreso_miles_usd"]].corr()
    corr.columns = corr.index = ["Pasajeros", "Distancia", "Retraso", "Ingreso"]
    fig, ax = plt.subplots(figsize=FIG)
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="Blues", vmin=-0.2, vmax=1,
                annot_kws={"size": 9}, cbar=False, ax=ax)
    ax.set_title("1 · Correlación de Pearson")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# Gráfica 2: Dispersión + recta OLS con banda de confianza
with fila1[1]:
    fig, ax = plt.subplots(figsize=FIG)
    sns.regplot(data=dff, x="pasajeros_abordo", y="ingreso_miles_usd", ci=95,
                scatter_kws={"alpha": 0.65, "s": 20, "color": SKY},
                line_kws={"color": RED, "linewidth": 1.8}, ax=ax)
    ax.set(xlabel="Pasajeros a bordo", ylabel="Ingreso (miles USD)")
    ax.set_title("2 · Regresión OLS: pasajeros vs. ingreso")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# Gráfica 3: Boxplot por estrategia
with fila2[0]:
    fig, ax = plt.subplots(figsize=FIG)
    orden = [e for e in ["Estrategia_A", "Estrategia_B"] if e in estrategias]
    sns.boxplot(data=dff, x="tipo_estrategia", y="ingreso_miles_usd", order=orden,
                hue="tipo_estrategia", palette={"Estrategia_A": SKY, "Estrategia_B": GOLD},
                legend=False, linewidth=1, ax=ax)
    ax.set(xlabel="", ylabel="Ingreso (miles USD)")
    ax.set_title("3 · Ingreso por estrategia (A vs B)")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# Gráfica 4: Histograma de residuos + KDE
with fila2[1]:
    fig, ax = plt.subplots(figsize=FIG)
    sns.histplot(residuos, kde=True, bins=15, color=NAVY, ax=ax)
    ax.axvline(0, color=RED, linestyle="--", linewidth=1.3)
    ax.set(xlabel="Residuo (miles USD)", ylabel="Frecuencia")
    ax.set_title("4 · Diagnóstico: residuos del modelo")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)