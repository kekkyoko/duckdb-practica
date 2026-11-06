import duckdb
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from scipy import stats
from statsmodels.stats.stattools import durbin_watson
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

st.set_page_config(page_title="Regresión Lineal Múltiple | CPC de agua", layout="wide")

# =====================================================================
# ESTILO "RETRO PAPEL" · TEMÁTICA AGUA
# =====================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

:root {
    --papel: #efe6d2;
    --papel-claro: #f7f1e3;
    --papel-oscuro: #e3d6b8;
    --tinta: #1f2a44;
    --tinta-suave: #5a6075;
    --oceano: #1b6f8f;
    --turquesa: #3fb5c4;
    --espuma: #bfe6ea;
    --mostaza: #e8b13a;
    --azul: #2f5d8a;
    --coral: #c8402a;
}

/* Fondo de papel con grano */
.stApp {
    background-color: var(--papel);
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .12  0 0 0 0 .16  0 0 0 0 .27  0 0 0 .09 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
    color: var(--tinta);
    font-family: 'Poppins', sans-serif;
}
.stApp p, .stApp li, .stApp label, .stApp td, .stApp th { font-family: 'Poppins', sans-serif; color: var(--tinta); }
[data-testid="stHeader"] { background: transparent; }

/* Franjas superiores (azul océano, turquesa, espuma) */
.franjas {
    position: fixed; top: 0; left: 0; right: 0; height: 14px; z-index: 999991;
    background: linear-gradient(90deg,
        var(--oceano) 0 33.33%, var(--turquesa) 33.33% 66.66%, var(--espuma) 66.66% 100%);
    border-bottom: 2px solid var(--tinta);
}

/* Gota dibujada con CSS y franja de olas */
.gota {
    display: inline-block; width: 12px; height: 12px; margin-right: 10px;
    background: var(--espuma); border: 2px solid var(--tinta);
    border-radius: 0 50% 50% 50%; transform: rotate(45deg) translateY(-1px);
}
.olas {
    height: 26px; margin: 6px 0 18px 0;
    background-image:
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='48' height='26'><path d='M0 9 Q12 -3 24 9 T48 9' fill='none' stroke='%231f2a44' stroke-width='2.5'/></svg>"),
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='48' height='26'><path d='M0 9 Q12 -3 24 9 T48 9' fill='none' stroke='%233fb5c4' stroke-width='2.5'/></svg>");
    background-repeat: repeat-x;
    background-position: 0 0, 12px 10px;
}

/* Sello, título, subrayado */
.sello {
    display: inline-block; transform: rotate(-2deg);
    background: var(--oceano); color: var(--papel-claro);
    border: 2px solid var(--tinta); border-radius: 999px;
    padding: 5px 16px; margin-bottom: 14px;
    font-family: 'Space Mono', monospace; font-weight: 700;
    font-size: .75rem; letter-spacing: .5px; text-transform: uppercase;
}
.titulo-mision {
    font-family: 'Space Mono', monospace; font-weight: 700;
    text-transform: uppercase; letter-spacing: -1px; line-height: 1.05;
    font-size: clamp(1.8rem, 4vw, 3rem); color: var(--tinta); margin: 4px 0 10px 0;
}
.subrayado { background: linear-gradient(transparent 60%, var(--turquesa) 60% 92%, transparent 92%); }
[data-testid="stCaptionContainer"] p { color: var(--tinta-suave); font-size: .85rem; }

/* Tarjeta de portada */
.hero {
    position: relative; overflow: hidden;
    background-color: var(--oceano);
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='48' height='26'><path d='M0 9 Q12 -3 24 9 T48 9' fill='none' stroke='white' stroke-opacity='.16' stroke-width='2.5'/></svg>");
    background-size: 48px 26px;
    border: 2px solid var(--tinta); border-radius: 10px;
    box-shadow: 6px 6px 0 var(--tinta); padding: 26px 30px; margin: 6px 0 26px 0;
}
.hero-etiqueta {
    display: inline-block; background: var(--mostaza); color: var(--tinta);
    border: 2px solid var(--tinta); border-radius: 999px; padding: 2px 12px;
    font-family: 'Space Mono', monospace; font-weight: 700; font-size: .7rem;
    text-transform: uppercase; letter-spacing: .5px; margin-bottom: 12px;
}
.hero-titulo {
    font-family: 'Space Mono', monospace; font-weight: 700; text-transform: uppercase;
    color: var(--papel-claro); font-size: clamp(1.3rem, 2.6vw, 2rem); line-height: 1.15; margin-bottom: 10px;
}
.stApp .hero p { color: var(--papel-claro); font-size: 1.02rem; margin: 0; max-width: 900px; }

/* Título de sección con círculo */
.seccion-titulo {
    display: flex; align-items: center; gap: 12px; margin: 26px 0 12px 0;
    font-family: 'Space Mono', monospace; font-weight: 700; text-transform: uppercase;
    font-size: 1.05rem; color: var(--tinta);
}
.seccion-titulo .letra {
    display: inline-flex; align-items: center; justify-content: center;
    width: 34px; height: 34px; border-radius: 50%; flex: 0 0 34px;
    background: var(--turquesa); border: 2px solid var(--tinta);
    box-shadow: 2px 2px 0 var(--tinta); font-size: .95rem;
}

/* Fichas (tarjetas) */
.fichas { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; margin: 8px 0 14px 0; }
.ficha {
    background: var(--papel-claro); border: 2px solid var(--tinta); border-radius: 10px;
    box-shadow: 4px 4px 0 var(--tinta); padding: 14px 16px; transition: transform .15s, box-shadow .15s;
}
.ficha:hover { transform: translate(-2px, -2px); box-shadow: 6px 6px 0 var(--tinta); }
.ficha-sim {
    display: inline-block; background: var(--oceano); color: var(--papel-claro);
    border: 2px solid var(--tinta); border-radius: 999px; padding: 0 12px;
    font-family: 'Space Mono', monospace; font-weight: 700; font-size: .8rem;
}
.ficha-nombre { font-family: 'Space Mono', monospace; font-weight: 700; margin-top: 8px; font-size: .95rem; word-break: break-all; }
.ficha-uni { color: var(--tinta-suave); font-family: 'Space Mono', monospace; font-size: .75rem; text-transform: uppercase; margin-bottom: 6px; }
.stApp .ficha p { font-size: .9rem; margin: 0; }

/* Nota con barra */
.nota {
    background: var(--papel-claro); border: 2px solid var(--tinta);
    border-left: 10px solid var(--mostaza); border-radius: 8px;
    box-shadow: 4px 4px 0 var(--tinta); padding: 10px 16px; margin: 12px 0 22px 0;
}
.nota-titulo {
    font-family: 'Space Mono', monospace; font-weight: 700; font-size: .72rem;
    letter-spacing: .3px; text-transform: uppercase; color: var(--tinta-suave); margin-bottom: 4px;
}
.stApp .nota p { margin: 0; font-size: .95rem; line-height: 1.5; }

/* Métricas */
[data-testid="stMetric"] {
    background: var(--papel-claro); border: 2px solid var(--tinta);
    border-radius: 10px; box-shadow: 4px 4px 0 var(--tinta);
    padding: 14px 18px; transition: transform .15s, box-shadow .15s;
}
[data-testid="stMetric"]:hover { transform: translate(-2px, -2px); box-shadow: 6px 6px 0 var(--tinta); }
[data-testid="stMetricLabel"] p {
    font-family: 'Space Mono', monospace !important; font-weight: 700;
    font-size: .72rem !important; letter-spacing: .3px; text-transform: uppercase; color: var(--tinta-suave);
}
[data-testid="stMetricValue"] { font-family: 'Space Mono', monospace !important; font-weight: 700; color: var(--tinta); }

/* Pestañas en píldora */
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; padding: 6px 0 12px 0; flex-wrap: wrap; }
.stTabs [data-baseweb="tab"] {
    background: var(--papel-claro); border: 2px solid var(--tinta);
    border-radius: 999px; padding: 6px 16px; height: auto; box-shadow: 3px 3px 0 var(--tinta);
}
.stTabs [data-baseweb="tab"] p {
    font-family: 'Space Mono', monospace !important; font-weight: 700;
    font-size: .8rem !important; text-transform: uppercase; letter-spacing: .5px;
}
.stTabs [aria-selected="true"] { background: var(--oceano); }
.stTabs [aria-selected="true"] p { color: var(--papel-claro) !important; }

/* Tablas, código, gráficas, alertas */
[data-testid="stDataFrame"], .stCodeBlock {
    border: 2px solid var(--tinta); border-radius: 10px; box-shadow: 4px 4px 0 var(--tinta); overflow: hidden;
}
.stCodeBlock pre, .stCodeBlock code { font-family: 'Space Mono', monospace !important; font-size: .8rem; }
[data-testid="stImage"] img {
    background: var(--papel-claro); border: 2px solid var(--tinta);
    border-radius: 10px; box-shadow: 4px 4px 0 var(--tinta);
}
[data-testid="stAlert"] {
    background: var(--papel-claro); color: var(--tinta);
    border: 2px solid var(--tinta); border-left: 10px solid var(--turquesa);
    border-radius: 8px; box-shadow: 4px 4px 0 var(--tinta);
}
.katex-display { background: var(--papel-claro); border: 2px dashed var(--tinta); border-radius: 8px; padding: 10px 0; }

.pie {
    margin-top: 40px; padding-top: 14px; border-top: 2px dashed var(--tinta);
    text-align: center; font-family: 'Space Mono', monospace; font-size: .72rem;
    text-transform: uppercase; color: var(--tinta-suave);
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
""", unsafe_allow_html=True)

# Gráficas con paleta de papel
TINTA = "#1f2a44"
sns.set_theme(style="whitegrid", rc={
    "figure.facecolor": "#f7f1e3", "axes.facecolor": "#fffaf0",
    "axes.edgecolor": TINTA, "axes.linewidth": 1.6,
    "axes.labelcolor": TINTA, "text.color": TINTA,
    "xtick.color": TINTA, "ytick.color": TINTA, "grid.color": "#e3d6b8",
})


def seccion(letra, texto):
    st.markdown(f'<div class="seccion-titulo"><span class="letra">{letra}</span><span>{texto}</span></div>',
                unsafe_allow_html=True)


def nota(texto, titulo="Nota"):
    st.markdown(f'<div class="nota"><div class="nota-titulo">{titulo}</div><p>{texto}</p></div>',
                unsafe_allow_html=True)


# =====================================================================
# PASO 1: datos simulados en DuckDB (reproducible)
# =====================================================================
@st.cache_data
def cargar_datos():
    con = duckdb.connect(database=':memory:')
    con.execute("SELECT setseed(0.42)")
    con.execute("""
    CREATE TABLE telemetria_agua AS
    WITH base AS (
        SELECT
            residencia_id,
            ROUND(20 + (random() * 11), 2)          AS temperatura_max,
            ROUND(50 + (random() * 40), 2)          AS humedad_max,
            ROUND(3 + (random() * 4))::DOUBLE       AS personas_familia,
            ROUND(0.2 + (random() * 1.8), 2)        AS consumo_bidon_pc,
            random()                                AS ruido
        FROM generate_series(1, 100) AS t(residencia_id)
    )
    SELECT
        residencia_id,
        temperatura_max,
        humedad_max,
        personas_familia,
        consumo_bidon_pc,
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
    df = con.execute("SELECT * FROM telemetria_agua").df()
    con.close()
    return df


df_agua = cargar_datos()

# PASO 2: correlación
matriz_correlacion = df_agua.drop(columns=['residencia_id']).corr(method='pearson')

# PASO 3: OLS
X = df_agua[['temperatura_max', 'humedad_max', 'personas_familia', 'consumo_bidon_pc']]
Y = df_agua['cpc_consumo']
modelo_ols = sm.OLS(Y, sm.add_constant(X)).fit()

# PASO 4: supuestos
residuos = modelo_ols.resid
stat_sw, p_sw = stats.shapiro(residuos)
dw_stat = durbin_watson(residuos)

# PASO 5: scikit-learn
modelo_sk = LinearRegression().fit(X, Y)
y_pred = modelo_sk.predict(X)
r2_sk = r2_score(Y, y_pred)
rmse_sk = np.sqrt(mean_squared_error(Y, y_pred))
b0 = modelo_sk.intercept_
b1, b2, b3, b4 = modelo_sk.coef_

# Valores para las notas dinámicas
corr_resp = matriz_correlacion['cpc_consumo'].drop('cpc_consumo')
var_fuerte = corr_resp.abs().idxmax()
r_fuerte = corr_resp[var_fuerte]
offdiag = matriz_correlacion.loc[X.columns, X.columns].values[~np.eye(4, dtype=bool)]
r_pred_max = np.abs(offdiag).max()
pend_simple = np.polyfit(df_agua['humedad_max'], Y, 1)[0]


def sube_baja(v):
    return "aumenta" if v > 0 else "disminuye"


# =====================================================================
# ENCABEZADO
# =====================================================================
st.markdown('<div class="franjas"></div>', unsafe_allow_html=True)
st.markdown('<span class="sello"><span class="gota"></span>Práctica 4.2 · INC-2505 · TecNM</span>',
            unsafe_allow_html=True)
st.markdown('<div class="titulo-mision">Regresión lineal <span class="subrayado">múltiple</span> y correlación</div>',
            unsafe_allow_html=True)
st.caption("Análisis y Exploración de Datos · Unidad 4: Análisis Estadístico Inferencial · Subtema 4.2")
st.markdown('<div class="olas"></div>', unsafe_allow_html=True)

tab_inicio, tab_teoria, tab_datos, tab_corr, tab_ols, tab_diag, tab_graf = st.tabs(
    ["Inicio", "Marco teórico", "Datos", "Correlación", "Modelo OLS", "Supuestos", "Gráficas"])

# =====================================================================
# INICIO
# =====================================================================
with tab_inicio:
    st.markdown(
        '<div class="hero"><div class="hero-etiqueta">Caso de estudio</div>'
        '<div class="hero-titulo">Predecir cuánta agua consume una persona al día</div>'
        '<p>Una consultora de gestión de recursos hídricos necesita saber si un modelo de regresión lineal '
        'múltiple puede predecir el consumo per cápita de agua potable (CPC, en lt/hab-día) en comunidades '
        'residenciales, usando el clima, el tamaño del hogar y el consumo de agua en bidón.</p></div>',
        unsafe_allow_html=True)

    seccion("A", "De qué trata la práctica")
    st.markdown(
        "El caso se basa en el artículo de investigación de **Arellano & Peña (2020)**, publicado en NovaSinergia. "
        "Se simulan los datos de **100 viviendas** dentro de **DuckDB**, con una semilla fija para que cualquiera "
        "obtenga los mismos resultados. Después se exploran las relaciones entre variables, se ajusta un modelo "
        "de regresión, se comprueba que cumpla sus supuestos y se mide qué tan bien predice.")

    seccion("B", "Finalidad")
    st.markdown(
        "- **Construir un pipeline analítico completo** en Python, desde la generación de datos hasta la evaluación del modelo.\n"
        "- **Estimar e interpretar** un modelo de mínimos cuadrados ordinarios (OLS): coeficientes, p-valores y residuos.\n"
        "- **Evaluar la capacidad predictiva** con R² y RMSE, y **validar los supuestos** de la regresión.")

    seccion("C", "Variables del estudio")
    variables = [
        ("Y", "cpc_consumo", "lt/hab-día", "Consumo per cápita de agua potable. Es la variable que se quiere predecir."),
        ("X1", "temperatura_max", "°C", "Temperatura máxima ambiental."),
        ("X2", "humedad_max", "%", "Humedad atmosférica máxima."),
        ("X3", "personas_familia", "hab/vivienda", "Densidad demográfica por hogar."),
        ("X4", "consumo_bidon_pc", "lt/hab-día", "Consumo de agua en bidón."),
    ]
    fichas = "".join(
        f'<div class="ficha"><span class="ficha-sim">{s}</span><div class="ficha-nombre">{n}</div>'
        f'<div class="ficha-uni">{u}</div><p>{d}</p></div>' for s, n, u, d in variables)
    st.markdown(f'<div class="fichas">{fichas}</div>', unsafe_allow_html=True)

    seccion("D", "Cómo está armado el análisis")
    pasos = [
        ("01", "DuckDB", "datos", "Genera la tabla de telemetría con SQL y semilla fija."),
        ("02", "Pearson", "correlación", "Mide la relación lineal entre cada par de variables."),
        ("03", "statsmodels", "modelo OLS", "Estima los coeficientes y su significancia."),
        ("04", "Residuos", "supuestos", "Revisa normalidad e independencia de los errores."),
        ("05", "scikit-learn", "predicción", "Calcula R² y RMSE del modelo ajustado."),
    ]
    fichas = "".join(
        f'<div class="ficha"><span class="ficha-sim">{a}</span><div class="ficha-nombre">{b}</div>'
        f'<div class="ficha-uni">{c}</div><p>{d}</p></div>' for a, b, c, d in pasos)
    st.markdown(f'<div class="fichas">{fichas}</div>', unsafe_allow_html=True)

    nota("Usa las pestañas de arriba en orden: primero el <b>Marco teórico</b>, luego los <b>Datos</b>, la "
         "<b>Correlación</b>, el <b>Modelo OLS</b>, los <b>Supuestos</b> y al final las <b>Gráficas</b>. "
         "En cada una hay una nota como esta que explica lo que estás viendo.", "🧭 Cómo recorrer la página")

# =====================================================================
# MARCO TEÓRICO
# =====================================================================
with tab_teoria:
    seccion("A", "Regresión lineal múltiple")
    st.markdown("Modela una variable de respuesta como una combinación lineal de varias variables predictoras, "
                "más un término de error aleatorio.")
    st.latex(r"Y = \beta_0 + \beta_1 X_1 + \beta_2 X_2 + \beta_3 X_3 + \beta_4 X_4 + \varepsilon")
    nota("Cada <b>β</b> dice cuánto cambia Y cuando su variable sube una unidad y las demás se mantienen fijas. "
         "β₀ es el valor base (intercepto) y ε es la parte que el modelo no logra explicar.", "💡 ¿Cómo se lee?")

    seccion("B", "Mínimos cuadrados ordinarios (OLS)")
    st.markdown("OLS elige los coeficientes que hacen mínima la suma de los errores al cuadrado.")
    st.latex(r"\hat{\boldsymbol{\beta}} = (\mathbf{X}^{\top}\mathbf{X})^{-1}\,\mathbf{X}^{\top}\mathbf{Y}"
             r"\qquad\qquad e_i = y_i - \hat{y}_i")
    nota("El <b>residuo</b> e es la diferencia entre lo observado y lo que predice el modelo. "
         "OLS busca la recta (en realidad, el plano) que deja esos residuos lo más pequeños posible.", "💡 Idea clave")

    seccion("C", "Correlación de Pearson")
    st.markdown("Mide qué tan lineal es la relación entre dos variables. Va de -1 a 1.")
    st.latex(r"r = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}"
             r"{\sqrt{\sum (x_i - \bar{x})^2 \; \sum (y_i - \bar{y})^2}}")
    nota("Regla práctica: cerca de 0 es relación débil o nula, alrededor de ±0.5 es moderada y arriba de ±0.7 es fuerte. "
         "El signo indica la dirección: positivo si ambas suben juntas, negativo si una sube y la otra baja.",
         "💡 Interpretación")

    seccion("D", "Calidad del ajuste")
    st.latex(r"R^2 = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}"
             r"\qquad\qquad RMSE = \sqrt{\frac{1}{n}\sum (y_i - \hat{y}_i)^2}")
    nota("<b>R²</b> es la proporción de la variación de Y que explica el modelo (1 sería perfecto). "
         "<b>RMSE</b> es el error típico de la predicción, en las mismas unidades que Y (aquí, lt/hab-día).",
         "💡 ¿Para qué sirven?")

    seccion("E", "Supuestos del modelo")
    st.markdown(
        "- **Linealidad:** la relación entre predictores y respuesta es lineal.\n"
        "- **Independencia de errores:** se revisa con el estadístico de Durbin-Watson.\n"
        "- **Homocedasticidad:** la varianza de los errores es constante.\n"
        "- **Normalidad de errores:** se revisa con la prueba de Shapiro-Wilk y el gráfico Q-Q.\n"
        "- **Sin multicolinealidad:** los predictores no deben estar muy correlacionados entre sí.")
    st.latex(r"d = \frac{\sum_{t=2}^{n} (e_t - e_{t-1})^2}{\sum_{t=1}^{n} e_t^2}")
    nota("Durbin-Watson (d) vale cerca de 2 cuando no hay autocorrelación; entre 1.5 y 2.5 se considera aceptable. "
         "En Shapiro-Wilk, un p-valor mayor a 0.05 indica que no se rechaza la normalidad.", "💡 Cómo decidir")

    seccion("F", "Herramientas usadas")
    st.markdown(
        "- **DuckDB:** base de datos SQL embebida, usada para simular y consultar los datos.\n"
        "- **pandas y NumPy:** manejo de tablas y cálculo numérico.\n"
        "- **statsmodels:** modelo OLS y resumen estadístico.\n"
        "- **scikit-learn:** ajuste del modelo y métricas R² y RMSE.\n"
        "- **matplotlib y seaborn:** gráficas de diagnóstico.\n"
        "- **Streamlit:** esta página web.")

# =====================================================================
# DATOS
# =====================================================================
with tab_datos:
    seccion("A", "Tabla de datos generada con DuckDB")
    st.dataframe(df_agua, use_container_width=True, height=350)
    nota("Cada fila es una vivienda (100 en total). Los datos <b>no son mediciones reales</b>: se generan en DuckDB "
         "con la semilla 0.42 a partir de un modelo con ruido, por eso el experimento es reproducible.",
         "📋 ¿Qué estoy viendo?")

    seccion("B", "Resumen estadístico")
    st.dataframe(df_agua.drop(columns=['residencia_id']).describe().round(2), use_container_width=True)
    nota("Muestra el promedio, la desviación estándar, el mínimo, el máximo y los cuartiles de cada variable. "
         "Sirve para confirmar que los rangos coinciden con lo esperado (por ejemplo, temperatura de 20 a 31 °C).",
         "📊 Para qué sirve")

# =====================================================================
# CORRELACIÓN
# =====================================================================
with tab_corr:
    seccion("A", "Matriz de correlación de Pearson (r)")
    st.dataframe(matriz_correlacion.round(4), use_container_width=True)
    seccion("B", "Correlación de cada variable con cpc_consumo")
    st.dataframe(corr_resp.round(4).to_frame("r"), use_container_width=True)
    nota(f"La relación lineal más fuerte con el consumo es la de <b>{var_fuerte}</b> (r = {r_fuerte:.4f}). "
         f"Entre los propios predictores, la correlación más alta en valor absoluto es {r_pred_max:.4f}, "
         "así que no hay señales de multicolinealidad y el modelo puede usar las cuatro variables sin problema.",
         "🔎 Cómo interpretarlo")

# =====================================================================
# MODELO OLS
# =====================================================================
with tab_ols:
    seccion("A", "Calidad del ajuste")
    c1, c2 = st.columns(2)
    c1.metric("R²", f"{r2_sk*100:.2f}%")
    c2.metric("RMSE", f"{rmse_sk:.4f} lt/hab-día")
    nota(f"El modelo explica el {r2_sk*100:.1f}% de la variación del consumo, y su error típico de predicción "
         f"es de unos {rmse_sk:.2f} lt/hab-día.", "📈 Lectura rápida")

    seccion("B", "Ecuación ajustada")
    st.latex(rf"\widehat{{CPC}} = {b0:.2f} {b1:+.2f}\,Temp {b2:+.2f}\,Hum {b3:+.2f}\,Pers {b4:+.2f}\,Bid")
    nota(f"Por cada grado más de temperatura, el consumo {sube_baja(b1)} {abs(b1):.2f} lt/hab-día; "
         f"por cada punto más de humedad {sube_baja(b2)} {abs(b2):.2f}; "
         f"por cada persona más en la vivienda {sube_baja(b3)} {abs(b3):.2f}; "
         f"y por cada litro más de bidón {sube_baja(b4)} {abs(b4):.2f}. "
         "Estos valores se parecen mucho a los coeficientes con los que se generaron los datos "
         "(94.5, 2.5, -0.8, -5.2 y 15.0), lo que confirma que el modelo recupera la relación real.",
         "🧮 Qué dice cada coeficiente")

    seccion("C", "Coeficientes y significancia")
    tabla = pd.DataFrame({
        "Coeficiente": modelo_ols.params, "Error est.": modelo_ols.bse,
        "t": modelo_ols.tvalues, "p-valor": modelo_ols.pvalues,
    }).round(4)
    tabla.index = ["intercepto", "temperatura_max", "humedad_max", "personas_familia", "consumo_bidon_pc"]
    st.dataframe(tabla, use_container_width=True)
    nota("Un p-valor menor a 0.05 significa que esa variable aporta información real al modelo. "
         "Si todos son muy pequeños, las cuatro variables son estadísticamente significativas.", "✅ Significancia")

    seccion("D", "Resumen completo de statsmodels")
    st.code(str(modelo_ols.summary()), language="text")

# =====================================================================
# SUPUESTOS
# =====================================================================
with tab_diag:
    seccion("A", "Pruebas sobre los residuos")
    c1, c2 = st.columns(2)
    c1.metric("Shapiro-Wilk (p)", f"{p_sw:.4f}")
    c2.metric("Durbin-Watson", f"{dw_stat:.4f}")

    st.markdown(f"**Normalidad (Shapiro-Wilk):** estadístico = {stat_sw:.4f}, p = {p_sw:.4f}")
    if p_sw > 0.05:
        st.success("Los residuos cumplen el supuesto de normalidad (p > 0.05).")
    else:
        st.error("Se rechaza la normalidad de los residuos (p <= 0.05).")

    st.markdown(f"**Independencia (Durbin-Watson):** {dw_stat:.4f}")
    if 1.5 <= dw_stat <= 2.5:
        st.success("Valor entre 1.5 y 2.5: no hay autocorrelación.")
    else:
        st.warning("Valor fuera de 1.5 a 2.5: posible autocorrelación.")

    nota("Si no se cumplen los supuestos, los p-valores y los intervalos de confianza del modelo pierden confiabilidad. "
         "La homocedasticidad y la normalidad también se pueden revisar a simple vista en la pestaña Gráficas.",
         "🧪 Por qué importa")

# =====================================================================
# GRÁFICAS
# =====================================================================
with tab_graf:
    seccion("A", "Panel de diagnóstico visual")
    fa, fb = st.columns(2)

    with fa:
        fig, ax = plt.subplots(figsize=(6.2, 4.6))
        sns.heatmap(matriz_correlacion, annot=True, fmt=".2f", cmap="coolwarm",
                    vmin=-1, vmax=1, ax=ax)
        ax.set_title('1. Matriz de Correlación de Pearson (r)')
        st.pyplot(fig)
        plt.close(fig)
        nota(f"Rojo es correlación positiva y azul negativa. Lo más fuerte con el consumo es <b>{var_fuerte}</b> "
             f"(r = {r_fuerte:.2f}).", "🌡️ Mapa de calor")

    with fb:
        fig, ax = plt.subplots(figsize=(6.2, 4.6))
        sns.regplot(data=df_agua, x='humedad_max', y='cpc_consumo', color='#2f5d8a', ax=ax,
                    line_kws={'color': '#c8402a', 'linewidth': 2})
        ax.set_title('2. Tendencia: Humedad Máx vs Consumo')
        ax.set_xlabel('Humedad Máxima (%)')
        ax.set_ylabel('CPC Consumo (lt/hab-día)')
        st.pyplot(fig)
        plt.close(fig)
        nota(f"La pendiente de esta recta simple es {pend_simple:.2f}: a más humedad, menos consumo. "
             "Difiere del coeficiente del modelo múltiple porque aquí no se controlan las otras variables.",
             "📉 Tendencia")

    fc, fd = st.columns(2)

    with fc:
        fig, ax = plt.subplots(figsize=(6.2, 4.6))
        ax.scatter(y_pred, Y, alpha=0.8, color='#1b6f8f', edgecolor='#1f2a44', linewidth=0.5)
        ax.plot([Y.min(), Y.max()], [Y.min(), Y.max()], '--', color='#c8402a', lw=2)
        ax.set_title(f'3. Reales vs Predichos (R² = {r2_sk*100:.1f}%)')
        ax.set_xlabel('CPC Predicho (ŷ)')
        ax.set_ylabel('CPC Real (y)')
        st.pyplot(fig)
        plt.close(fig)
        nota("Mientras más cerca estén los puntos de la línea punteada (la diagonal ideal), mejor predice el modelo.",
             "🎯 Reales vs predichos")

    with fd:
        fig, ax = plt.subplots(figsize=(6.2, 4.6))
        ax.scatter(y_pred, residuos, color='#3fb5c4', alpha=0.8, edgecolor='#1f2a44', linewidth=0.5)
        ax.axhline(y=0, color='#c8402a', linestyle='--', lw=2)
        ax.set_title('4. Residuos vs Ajustados (Homocedasticidad)')
        ax.set_xlabel('Valores Predichos (ŷ)')
        ax.set_ylabel('Residuos (e = y - ŷ)')
        st.pyplot(fig)
        plt.close(fig)
        nota("Los puntos deben repartirse al azar alrededor de cero. Si formaran un embudo o una curva, "
             "la varianza no sería constante.", "🧪 Homocedasticidad")

    fe, ff = st.columns(2)

    with fe:
        fig, ax = plt.subplots(figsize=(6.2, 4.6))
        sm.qqplot(residuos, line='45', fit=True, ax=ax)
        ax.set_title('5. Gráfico Q-Q Normal (Residuos)')
        st.pyplot(fig)
        plt.close(fig)
        nota(f"Si los puntos siguen la diagonal, los residuos son normales. Coincide con Shapiro-Wilk (p = {p_sw:.4f}).",
             "📏 Normalidad")

    with ff:
        nota("Las gráficas 1, 2 y 3 hablan de la relación entre variables y la precisión del modelo; "
             "la 4 y la 5 validan los supuestos. Si las cinco se ven bien, el modelo es confiable para predecir.",
             "🧭 Cómo leer el panel")

st.markdown('<div class="pie">Análisis y Exploración de Datos · INC-2505 · TecNM · '
            'Python, DuckDB, statsmodels, scikit-learn</div>', unsafe_allow_html=True)