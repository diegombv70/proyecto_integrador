# Proyecto integrador - Analitica de Datos

**Caracterizacion descriptiva de la cancelacion de clientes en una empresa de telecomunicaciones a partir del dataset Telco Customer Churn**

Autor: Diego Mauricio Bedoya Valencia - Institucion Universitaria Digital de Antioquia

## Proposito

Proyecto de analitica descriptiva que, a partir de un dataset publico de Hugging Face, caracteriza y compara la cancelacion de clientes (*churn*) de una compania de telecomunicaciones. La etapa **AE2** define y documenta la necesidad analitica, obtiene el dataset, lo describe en Jupyter y genera automaticamente un resumen del DataFrame en `.txt`.

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

Los datos **no se guardan en el repositorio**: se descargan de Hugging Face al ejecutar el notebook. El dataset es publico y no requiere token ni aceptar condiciones de acceso.

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
```

## Pasos de ejecucion

Requisitos: Python 3.10 o superior y conexion a internet.

```bash
git clone https://gitlab.com/deigo.bedoya/proyecto_integrador.git
cd proyecto_integrador
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook AE2/notebooks/AE2_exploracion_dataset.ipynb
```

Ejecutar todas las celdas en orden (*Kernel > Restart & Run All*). El notebook:

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

## Contenido del resumen `.txt`

Procedencia (identificador, configuracion, split, revision, licencia, si es muestra), cantidad de filas y columnas, nombres y tipos de las columnas, valores nulos por columna (incluye textos vacios) y una muestra de 5 filas.
