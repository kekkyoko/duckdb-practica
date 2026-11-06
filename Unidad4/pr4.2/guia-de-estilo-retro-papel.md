# Guía de estilo: "Retro papel" (registro de excursiones ITC)

Estilo retro tipo años 70: papel crema con grano, tinta azul marino, franjas tricolor, tarjetas con sombra dura y tipografía monoespaciada en mayúsculas. Basado en **Bootstrap 5.3.3** con un archivo propio `css/estilos.css`.

Para reutilizarlo en otro proyecto: copia `estilos.css`, carga las fuentes y Bootstrap (sección 1) y usa las clases de la sección 5.

## 1. Dependencias

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="css/estilos.css" rel="stylesheet">
```

## 2. Colores

| Variable | Valor | Uso |
|---|---|---|
| `--papel` | `#efe6d2` | Fondo de la página |
| `--papel-claro` | `#f7f1e3` | Tarjetas, navbar, campos |
| `--papel-oscuro` | `#e3d6b8` | Hover, campos deshabilitados |
| `--tinta` | `#1f2a44` | Texto, bordes, sombras |
| `--tinta-suave` | `#5a6075` | Texto secundario, etiquetas |
| `--rojo` | `#c8402a` | Botón principal, errores, sellos |
| `--naranja` | `#e07a2f` | Acentos, letras de sección |
| `--mostaza` | `#e8b13a` | Subrayado, paso activo, notas |
| `--azul` | `#2f5d8a` | Foco de campos, opción seleccionada |

Extras: rojo hover `#b23620`, campo en foco `#fffaf0`, placeholder `#9a9585`.

## 3. Tipografía

- **Títulos, etiquetas, botones, navbar, footer:** Space Mono, 700, `text-transform: uppercase`.
- **Texto general:** Poppins (400 a 700), color `--tinta`.
- Título principal: `letter-spacing: -1px`, `line-height: 1.05`.
- Etiquetas de formulario: `.72rem`, `letter-spacing: .3px`, color `--tinta-suave`.
- Botones: `.85rem`, `letter-spacing: .5px`.

## 4. Reglas de diseño

- **Bordes:** siempre `2px solid var(--tinta)`. Separadores con `2px dashed`.
- **Sombra dura** (sin desenfoque): tarjetas `4px 4px 0 var(--tinta)`, botones `3px 3px 0`, hover de tarjeta `6px 6px 0`.
- **Radios:** tarjetas `10px`, campos `8px`, botones y etiquetas `999px` (píldora).
- **Fondo:** `--papel` con grano de ruido SVG (`feTurbulence`) incrustado como `background-image`.
- **Franjas tricolor** rojo, naranja y mostaza (14px de alto) arriba de la página y en la banda del comprobante.
- **Giros decorativos:** sello `-2deg`, parche `-6deg`, sello de estatus `8deg`.
- **Interacción:** al presionar, el botón se desplaza `3px 3px` y pierde la sombra. Las transiciones se desactivan con `prefers-reduced-motion`.
- **Foco de campos:** borde `--azul` y sombra `3px 3px 0 var(--azul)`.
- **Validación:** error en `--rojo`; el mensaje se posiciona de forma absoluta para que el contenido no se mueva; sin palomita verde.

## 5. Componentes (clases)

| Clase | Descripción |
|---|---|
| `.franjas` | Banda tricolor superior |
| `.navbar-mision` | Navbar con fondo `--papel-claro`; enlace activo en píldora azul marino |
| `.sello` | Etiqueta roja con borde, girada `-2deg` |
| `.titulo-mision` | Título en Space Mono, mayúsculas |
| `.subrayado` | Resaltado mostaza detrás del texto |
| `.ficha` | Tarjeta: fondo claro, borde 2px, sombra dura |
| `.fase` | Ficha con número grande y efecto hover |
| `.btn-mision` / `.btn-secundario` | Botón rojo / botón claro, en píldora |
| `.hoja`, `.hoja-encabezado` | Hoja del formulario con encabezado y borde inferior punteado |
| `.pasos .paso` | Indicador de pasos (`.activo` mostaza, `.hecho` azul marino) |
| `.seccion-titulo .letra` | Título de sección con círculo naranja con letra |
| `.opciones` | Radios y checkboxes como fichas en píldora |
| `.nota` | Nota con barra mostaza a la izquierda |
| `.pase` | Comprobante tipo boleto con banda tricolor y sello |

## 6. Estructura base de una página

```html
<div class="franjas"></div>
<nav class="navbar navbar-expand-lg navbar-mision">...</nav>
<main class="container">...</main>
<footer class="container pb-3 text-center">...</footer>
```

## 7. Ajustes para otro proyecto

- Cambia solo las variables de `:root` para recolorear todo el sitio (por ejemplo, el verde y dorado del logo del ITC).
- Los nombres de clase con "mision" vienen de la primera versión del tema; se pueden renombrar sin afectar el diseño si se cambian en el HTML y en el CSS.
