# Proyecto integrador - Analitica de Datos

**Caracterizacion descriptiva de la cancelacion de clientes en una empresa de telecomunicaciones a partir del dataset Telco Customer Churn**

Autor: Diego Mauricio Bedoya Valencia - Institucion Universitaria Digital de Antioquia

## Proposito

Proyecto de analitica descriptiva que, a partir de un dataset publico de Hugging Face, caracteriza y compara la cancelacion de clientes (*churn*) de una compania de telecomunicaciones. - **AE2:** define la necesidad, obtiene el dataset, lo describe y genera un resumen `.txt`.
- **AE4 (Actividad 5):** presenta las metricas y graficos que responden las preguntas en una aplicacion de Streamlit e integra el informe final en PDF.
- **AE3 (Actividad 4):** transforma y enriquece el dataset, responde las preguntas de negocio con tablas y exporta los datos preparados, las tablas `.csv` y un resumen `.txt` del DataFrame final.

## Necesidad (escenario hipotetico)

El equipo de **retencion de clientes** de la compania necesita saber **en que grupos de clientes se concentra la cancelacion** para priorizar sus campanas de fidelizacion.

**Pregunta de analisis:** Como varia la tasa de cancelacion (`Churn`) de los 7.043 clientes registrados segun el tipo de contrato, la antiguedad, los servicios contratados, el metodo de pago, el nivel de cargos mensuales y el perfil demografico, y que segmentos presentan las tasas de cancelacion mas altas?

## Dataset

| Dato | Valor |
|---|---|
| Nombre | Telco Customer Churn (IBM Sample Dataset) |
| Identificador | `scikit-learn/churn-prediction` |
| Enlace | https://huggingface.co/datasets/scikit-learn/churn-prediction |
| Configuracion / split | `default` / `train` |
| Revision | `aa09900373d90780ee70d27571775aff0e51569c` |
| Tamano | 7.043 filas x 21 columnas (se usa completo, sin muestra) |
| Licencia | CC BY 4.0 |
| Naturaleza | Datos **ficticios** creados por IBM Sample Datasets |
| Fecha de consulta | 2026-10-25 |

El dataset original se descarga de Hugging Face al ejecutar los notebooks (publico, sin token). El dataset **preparado** de AE3 si se publica en el repositorio, lo que permite la licencia CC BY 4.0 citando la fuente.

## AE4 - Metricas y visualizacion en Streamlit (Actividad 5)

**Aplicacion:** `AE4/app_Actividad5.py` (Streamlit + Plotly).
**Enlace publicado:** https://proyectointegrador-yk2wn8y6ydgqgojp7kzzwm.streamlit.app

La app carga el dataset preparado (`AE3/datos/telco_churn_preparado_Actividad4.csv`) y las tablas de resultados (`AE3/resultados/tablas/*_Actividad4.csv`). Tiene un menu con:

| Seccion | Contenido |
|---|---|
| Inicio | Necesidad, preguntas de negocio, identificacion del dataset e indicadores clave |
| P0 a P6 | Metrica (definicion, calculo, unidad, periodo), graficos interactivos, interpretacion, decision que apoya, limitacion y tabla de resultados |
| Conclusiones | Conclusiones, recomendaciones, limitaciones y verificacion de que las cifras coinciden con el notebook |

### Ejecutar la app

```bash
pip install -r requirements.txt
streamlit run AE4/app_Actividad5.py
```

Se abre en `http://localhost:8501`.

### Publicar en Streamlit Community Cloud

En https://share.streamlit.io: *Create app* -> repositorio `diegombv70/proyecto_integrador`, rama `main`, archivo principal `AE4/app_Actividad5.py`. Las dependencias de la app estan en `AE4/requirements.txt`.

### Archivos AE4

| Archivo | Ruta |
|---|---|
| Aplicacion Streamlit | `AE4/app_Actividad5.py` |
| Dependencias de la app | `AE4/requirements.txt` |
| Informe final (PDF) | `AE4/documento/BedoyaDiego_AE4_Informe_Final_Actividad5.pdf` |
| Informe final (Word) | `AE4/documento/BedoyaDiego_AE4_Informe_Final_Actividad5.docx` |
| Figuras del informe | `AE4/figuras/` |
| Capturas de la app | `AE4/capturas/` |
| Scripts del informe | `AE4/scripts/` (capturar figuras, generar Word y PDF) |

## AE3 - Transformacion y enriquecimiento (Actividad 4)

### Preguntas de negocio abordadas

La pregunta general de AE2 se dividio en una linea base y 6 subpreguntas (mismo alcance):

| # | Pregunta | Tabla de resultados |
|---|---|---|
| P0 | Tasa global de cancelacion (linea base) | `P0_tasa_global_Actividad4.csv` |
| P1 | Tasa segun condiciones de la cuenta (contrato, pago, factura) | `P1_tasa_por_cuenta_Actividad4.csv` |
| P2 | Tasa segun antiguedad | `P2_tasa_por_antiguedad_Actividad4.csv` |
| P3 | Tasa segun servicios contratados | `P3_tasa_por_servicios_Actividad4.csv` |
| P4 | Tasa segun perfil demografico | `P4_tasa_por_perfil_Actividad4.csv` |
| P5 | Cargos de quienes cancelan vs. quienes permanecen | `P5a_estadisticas_cargos_Actividad4.csv`, `P5b_tasa_por_rango_cargo_Actividad4.csv` |
| P6 | Segmentos combinados con mayor cancelacion | `P6_top10_segmentos_Actividad4.csv` |

### Transformaciones

- Espacios sobrantes eliminados en textos (11 valores).
- `TotalCharges` de texto a numero; 11 vacios (clientes con `tenure = 0`) reemplazados por 0.
- `SeniorCitizen` 0/1 a No/Si.
- Categorias y nombres de columnas traducidos al espanol (`Churn` -> `cancelo`); `No` de internet unificado como `Sin internet`.
- Categoricas a tipo `category`. Se conservan los 7.043 clientes (sin eliminar registros).
- Controles: duplicados, nulos, rangos y coherencia entre servicios (todos OK).

### Enriquecimiento (9 variables nuevas)

`cancelo_flag`, `rango_antiguedad`, `rango_cargo_mensual`, `tipo_servicio`, `n_servicios_adicionales`, `rango_servicios_adicionales`, `pago_automatico`, `tiene_familia`, `cargo_mensual_perdido`. No se unio otra tabla.

### Hallazgo principal

Tasa global: **26,54 %**. La cancelacion se concentra en clientes **mes a mes (42,71 %)**, con **fibra optica (41,89 %)** y en su **primer ano (47,44 %)**. El segmento mes a mes + fibra + 0-12 meses llega a **70,20 %**.

### Rutas de resultados

| Archivo | Ruta |
|---|---|
| Notebook ejecutado | `AE3/notebooks/AE3_transformacion_enriquecimiento_Actividad4.ipynb` |
| Funciones (.py) | `AE3/src/preparacion_Actividad4.py` |
| Dataset preparado | `AE3/datos/telco_churn_preparado_Actividad4.csv` (7.043 x 30) |
| Tablas de resultados y calidad | `AE3/resultados/tablas/*_Actividad4.csv` |
| Resumen descriptivo | `AE3/resultados/resumen_dataframe_Actividad4.txt` (se regenera en cada ejecucion) |
| Documento Word | `AE3/documento/BedoyaDiego_AE3_Transformacion_Enriquecimiento_Actividad4.docx` |

### Ejecucion AE3

Con el entorno instalado (ver *Pasos de ejecucion*):

```bash
jupyter notebook AE3/notebooks/AE3_transformacion_enriquecimiento_Actividad4.ipynb
# o sin abrir Jupyter:
cd AE3/notebooks
jupyter nbconvert --to notebook --execute --inplace AE3_transformacion_enriquecimiento_Actividad4.ipynb
```

El notebook descarga el dataset, lo transforma, valida, enriquece, responde P0-P6, exporta los `.csv`, verifica que los archivos coincidan con el notebook y regenera el `.txt`.

## Estructura

```
proyecto_integrador/
├── README.md
├── requirements.txt
├── .gitignore
└── AE2/
    ├── documento/
    │   └── BedoyaDiego_AE2_Necesidad_y_Diseno.docx   # Documento del avance (Word)
    ├── notebooks/
    │   └── AE2_exploracion_dataset.ipynb            # Obtencion y descripcion basica (ejecutado)
    ├── resultados/
    │   └── resumen_dataframe.txt                     # Resumen generado automaticamente
    └── src/
        ├── hf_dataset_loader.py                      # Clase HFDatasetLoader: Hugging Face -> DataFrame
        └── dataset_summarizer.py                     # Clase DatasetSummarizer: DataFrame -> .txt
└── AE3/
    ├── datos/telco_churn_preparado_Actividad4.csv    # Dataset transformado y enriquecido
    ├── documento/BedoyaDiego_AE3_..._Actividad4.docx  # Documento del avance actualizado
    ├── notebooks/AE3_transformacion_enriquecimiento_Actividad4.ipynb
    ├── resultados/
    │   ├── resumen_dataframe_Actividad4.txt           # Resumen del DataFrame final
    │   └── tablas/                                    # P0-P6 y tablas de calidad (.csv)
    └── src/preparacion_Actividad4.py                  # Transformacion, enriquecimiento y tablas
└── AE4/
    ├── app_Actividad5.py                              # Aplicacion Streamlit
    ├── requirements.txt                               # Dependencias de la app
    ├── documento/                                     # Informe final .docx y .pdf
    ├── figuras/ y capturas/                           # Imagenes de la app
    └── scripts/                                       # Generacion de figuras, Word y PDF
```

## Pasos de ejecucion

Requisitos: Python 3.10 o superior y conexion a internet.

```bash
git clone https://github.com/diegombv70/proyecto_integrador.git
cd proyecto_integrador
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook AE2/notebooks/AE2_exploracion_dataset.ipynb   # AE2
jupyter notebook AE3/notebooks/AE3_transformacion_enriquecimiento_Actividad4.ipynb   # AE3
```

Ejecutar todas las celdas en orden (*Kernel > Restart & Run All*). El notebook de AE2:

1. Descarga `scikit-learn/churn-prediction` (split `train`, revision fijada) y lo carga en un DataFrame.
2. Muestra registros, dimensiones, columnas, tipos de datos y valores nulos por columna.
3. Explica que representa cada fila y que variables respaldan la necesidad.
4. Crea la carpeta `AE2/resultados/` si no existe y **regenera** `resumen_dataframe.txt` (UTF-8) en cada ejecucion.
5. Lee el archivo generado y verifica que corresponde al DataFrame.

Ejecucion sin abrir Jupyter:

```bash
cd AE2/notebooks
jupyter nbconvert --to notebook --execute --inplace AE2_exploracion_dataset.ipynb
```

## Contenido de los resumenes `.txt`

Procedencia (identificador, configuracion, split, revision, licencia, si es muestra), cantidad de filas y columnas, nombres y tipos de las columnas, valores nulos por columna (incluye textos vacios) y una muestra de 5 filas.


El resumen de AE3 agrega: estadisticas descriptivas de las variables numericas, frecuencias de las categoricas, tasa global de cancelacion y el registro de transformaciones aplicadas.
