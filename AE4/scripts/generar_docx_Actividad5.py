"""Construye el documento final AE4 (.docx) a partir del documento AE3."""
import copy
import sys
from pathlib import Path

import docx
import docx.enum.table
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
from docx.text.paragraph import Paragraph

RAIZ = Path(sys.argv[1])
URL_APP = sys.argv[2] if len(sys.argv) > 2 else ""
REPO = "https://github.com/diegombv70/proyecto_integrador"
SRC = RAIZ / "AE3/documento/BedoyaDiego_AE3_Transformacion_Enriquecimiento_Actividad4.docx"
OUT = RAIZ / "AE4/documento/BedoyaDiego_AE4_Informe_Final_Actividad5.docx"
FIG = RAIZ / "AE4/figuras"

d = docx.Document(SRC)
P = d.paragraphs


def set_text(p, text):
    runs = p.runs
    if not runs:
        p.add_run(text); return
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


for p in P[:20]:
    if p.text.startswith("Proyecto integrador"):
        set_text(p, "Proyecto integrador – Informe final AE4 (Actividad 5)")
    elif p.text.startswith("Transformación y enriquecimiento"):
        set_text(p, "Métricas y visualización de datos")
    elif p.text.startswith("Medellín"):
        set_text(p, "Medellín, 23 de noviembre de 2026")

anexo_h = next(p for p in P if p.style.name == "Heading 1" and p.text.startswith("Anexo A"))
ae3_intro = next(p for p in P if p.text.startswith("Actualización AE3"))
e = copy.deepcopy(ae3_intro._p); ae3_intro._p.addnext(e)
set_text(Paragraph(e, ae3_intro._parent),
         "Informe final AE4 (Actividad 5). Esta versión integra todas las etapas del proyecto y agrega las métricas y "
         "visualizaciones (sección 12), presentadas en una aplicación de Streamlit vinculada al repositorio del "
         "proyecto, las conclusiones finales y recomendaciones (sección 13) y las referencias (sección 14). Las cifras "
         "de la aplicación y de este documento provienen de los mismos archivos exportados en AE3.")

ANCLA = [anexo_h._p]
mover = lambda el: ANCLA[0].addprevious(el)


def par(text="", style="Normal", bold_prefix=None):
    p = d.add_paragraph(style=style)
    if bold_prefix:
        p.add_run(bold_prefix).bold = True
    p.add_run(text)
    mover(p._p)
    return p


h1 = lambda t: par(t, "Heading 1")
h2 = lambda t: par(t, "Heading 2")
bullet = lambda t, b=None: par(t, "List Bullet", b)

CONT = {"Tabla": 18, "Figura": 0}
TITULOS = {"Tabla": [], "Figura": []}


def caption(tipo, titulo):
    CONT[tipo] += 1
    n = CONT[tipo]
    TITULOS[tipo].append(f"{tipo} {n}. {titulo}")
    p = d.add_paragraph(style="Caption")
    p.add_run(f"{tipo} ")
    fld = OxmlElement("w:fldSimple"); fld.set(qn("w:instr"), f" SEQ {tipo} \\* ARABIC ")
    r = OxmlElement("w:r"); t = OxmlElement("w:t"); t.text = str(n); r.append(t); fld.append(r)
    p._p.append(fld)
    run = p.add_run(f". {titulo}"); run.italic, run.bold = True, False
    p.paragraph_format.keep_with_next = True
    mover(p._p)


def nota(text):
    p = d.add_paragraph(); p.paragraph_format.line_spacing = 1.0
    r = p.add_run("Nota. "); r.italic = True; r.font.size = Pt(9)
    r2 = p.add_run(text); r2.font.size = Pt(9)
    mover(p._p)


def tabla(titulo, enc, filas, anchos, nota_txt):
    caption("Tabla", titulo)
    t = d.add_table(rows=1 + len(filas), cols=len(enc))
    t.style = d.tables[0].style
    t.alignment = docx.enum.table.WD_TABLE_ALIGNMENT.CENTER
    total = sum(anchos); anchos = [int(a * 9360 / total) for a in anchos]
    for i, fila in enumerate([enc] + filas):
        for j, v in enumerate(fila):
            c = t.rows[i].cells[j]; c.width = docx.shared.Twips(anchos[j])
            p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(1); p.paragraph_format.line_spacing = 1.0
            r = p.add_run(str(v)); r.font.size = Pt(8)
            if i == 0:
                r.bold = True; r.font.color.rgb = docx.shared.RGBColor(0xFF, 0xFF, 0xFF)
                shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), "1F3A5F")
                c._tc.get_or_add_tcPr().append(shd)
    mover(t._tbl)
    nota(nota_txt)


def figura(archivo, titulo, muestra, decision, limitacion, ancho=6.3):
    caption("Figura", titulo)
    p = d.add_paragraph(); p.alignment = 1
    p.add_run().add_picture(str(FIG / archivo), width=Inches(ancho))
    mover(p._p)
    nota("Elaboración propia en la aplicación Streamlit (AE4/app_Actividad5.py) a partir de las tablas exportadas en AE3. "
         "Periodo: corte transversal sin fechas.")
    par(muestra, bold_prefix="Qué muestra y cómo responde la pregunta. ")
    par(decision, bold_prefix="Decisión que puede apoyar. ")
    par(limitacion, bold_prefix="Limitación. ")


# ======================================================== 12. METRICAS Y VISUALIZACION
h1("12. Métricas y visualización de datos")
par("En la etapa final se construyeron las métricas y los gráficos que responden cada pregunta de negocio y se "
    "presentaron en una aplicación de Streamlit. Cada gráfico se genera a partir del dataset preparado y de las tablas "
    "de resultados exportadas por el notebook de AE3, por lo que sus cifras coinciden con las tablas 11 a 18.")

h2("12.1 Aplicación en Streamlit")
par("La aplicación (AE4/app_Actividad5.py) tiene un menú lateral con nueve secciones: inicio (necesidad, preguntas de "
    "negocio e identificación del dataset), una sección por cada pregunta P0 a P6 y una sección de conclusiones, "
    "recomendaciones y limitaciones. Cada sección muestra indicadores clave, la definición de la métrica (cálculo, "
    "unidad y periodo), uno o dos gráficos interactivos, la interpretación, la decisión que puede apoyar, la limitación "
    "y la tabla de resultados de AE3. La sección final recalcula las tasas desde el dataset preparado y comprueba que "
    "coincidan con las tablas del notebook.")
par(f"Repositorio: {REPO}", bold_prefix="")
par(f"Aplicación publicada: {URL_APP}" if URL_APP else
    "Ejecución local: desde la raíz del repositorio, pip install -r requirements.txt y luego "
    "streamlit run AE4/app_Actividad5.py.")

h2("12.2 Métricas utilizadas")
par("La Tabla 19 resume la métrica de cada pregunta. La métrica principal es la tasa de cancelación, porque permite "
    "comparar grupos de distinto tamaño en la misma escala. Se complementa con la participación en las cancelaciones "
    "y con el cargo mensual perdido, que muestra cuánto ingreso representa cada grupo. El cargo mensual perdido es un "
    "ingreso dejado de facturar, no una medida de rentabilidad, porque el dataset no tiene costos.")
tabla("Métricas por pregunta de negocio",
      ["Pregunta", "Métrica", "Cálculo", "Unidad", "Gráfico"],
      [["P0", "Tasa global; % del cargo mensual", "Cancelaciones ÷ 7.043 × 100; cargo de quienes cancelaron ÷ cargo total × 100", "%; u.m./mes", "Barras apiladas"],
       ["P1", "Tasa de cancelación por condición de cuenta", "Cancelaciones ÷ clientes del segmento × 100", "%", "Barras con línea de tasa global"],
       ["P2", "Tasa por rango de antigüedad; % de clientes y de cancelaciones", "Igual a P1; participación = segmento ÷ total × 100", "%", "Barras y barras agrupadas"],
       ["P3", "Tasa por servicio contratado", "Igual a P1", "%", "Barras y barras agrupadas (con/sin servicio)"],
       ["P4", "Tasa por variable de perfil", "Igual a P1", "%", "Barras horizontales"],
       ["P5", "Mediana y cuartiles del cargo mensual; tasa por rango de cargo", "Estadísticas por grupo; igual a P1", "u.m./mes; %", "Diagrama de caja y barras"],
       ["P6", "Tasa por segmento combinado (mín. 50 clientes); cargo mensual perdido", "Igual a P1; suma de cargo_mensual de quienes cancelaron", "%; u.m./mes", "Barras horizontales (ranking) y burbujas"]],
      [9, 22, 30, 12, 22],
      "Elaboración propia. u.m. = unidades monetarias (moneda no documentada). Periodo: corte transversal sin fechas.")

h2("12.3 Visualizaciones y respuestas a las preguntas")
par("En todos los gráficos de tasa, las barras rojas indican grupos por encima de la tasa global (26,54 %) y la línea "
    "punteada marca esa tasa global.")
figura("P0_1.png", "Peso de los clientes que cancelaron en clientes y en cargo mensual (P0)",
       "El 26,54 % de los clientes cancelaron (1.869 de 7.043), pero representaban el 30,50 % del cargo mensual "
       "(139.130,85 u.m./mes), porque pagaban más en promedio. Esta es la línea base del análisis.",
       "Dimensionar el problema para justificar el presupuesto de retención.",
       "Es ingreso dejado de facturar, no rentabilidad: no hay datos de costos.")
figura("P1_1.png", "Tasa de cancelación por tipo de contrato (P1)",
       "Mes a mes cancela 42,71 %, frente a 11,27 % (un año) y 2,83 % (dos años), y reúne el 88,55 % de las "
       "cancelaciones. En la aplicación, el selector muestra además el método de pago (cheque electrónico 45,29 %) y la "
       "factura electrónica (33,57 % con factura frente a 16,33 % sin ella).",
       "Incentivos para migrar de mes a mes a contratos de uno o dos años y promover el pago automático.",
       "Es una asociación, no una causa: los clientes más comprometidos pueden elegir contratos largos.")
figura("P2_1.png", "Tasa de cancelación por rango de antigüedad (P2)",
       "La tasa baja de 47,44 % en el primer año a 9,51 % después de cuatro años.",
       "Programa de bienvenida y acompañamiento durante los primeros 12 meses.",
       "Corte transversal: no se sigue a los mismos clientes en el tiempo.", 5.0)
figura("P2_2.png", "Peso de cada rango de antigüedad en clientes y en cancelaciones (P2)",
       "El primer año tiene el 31,04 % de los clientes pero el 55,48 % de las cancelaciones.",
       "Concentrar los recursos de retención en clientes nuevos.",
       "Los rangos de antigüedad se definieron en AE2; otros cortes podrían cambiar los porcentajes.", 5.0)
figura("P3_1.png", "Tasa de cancelación por tipo de internet (P3)",
       "Fibra óptica cancela 41,89 %, DSL 18,96 % y sin internet 7,40 %. La fibra concentra el 82,15 % del cargo "
       "mensual perdido.",
       "Revisar la experiencia de los clientes de fibra óptica.",
       "No hay datos de calidad del servicio ni de precios por producto para explicar la diferencia.")
figura("P3_2.png", "Tasa de cancelación según tenga o no cada servicio adicional (P3)",
       "Sin seguridad en línea (41,77 %) o soporte técnico (41,64 %) la tasa casi triplica la de quienes sí los "
       "tienen (14,61 % y 15,17 %). Streaming casi no cambia la tasa.",
       "Ofrecer seguridad y soporte técnico a clientes de fibra que no los tienen.",
       "Solo incluye clientes con internet; la diferencia no prueba que el servicio evite la cancelación.")
figura("P4_1.png", "Tasa de cancelación por variable de perfil (P4)",
       "El género no marca diferencia (26,92 % frente a 26,16 %). Los adultos mayores cancelan 41,68 % y quienes no "
       "tienen pareja ni dependientes 34,24 %.",
       "Ofertas para adultos mayores y planes familiares.",
       "La edad que define a un adulto mayor no está documentada.")
figura("P5_1.png", "Distribución del cargo mensual según cancelación (P5)",
       "Quienes cancelan tienen un cargo mensual mediano mayor (79,65 frente a 64,43 u.m.) y una antigüedad mediana "
       "mucho menor (10 frente a 38 meses).",
       "Revisar la propuesta de valor de los planes de mayor precio en los primeros meses.",
       "Mayor cargo no significa mayor rentabilidad; la moneda no está documentada.", 5.0)
figura("P5_2.png", "Tasa de cancelación por rango de cargo mensual (P5)",
       "La tasa sube de 10,86 % con cargo bajo a 37,95 % con cargo alto (70–90 u.m.) y 32,86 % con muy alto (≥90). "
       "Los rangos alto y muy alto suman el 81 % del cargo mensual perdido.",
       "Priorizar a los clientes de cargo alto en las campañas de retención.",
       "El cargo alto se relaciona con la fibra óptica; sus efectos no se pueden separar con este análisis.", 5.0)
figura("P6_1.png", "Diez segmentos con mayor tasa de cancelación (P6)",
       "Mes a mes + fibra óptica + 0–12 meses cancela 70,20 % (916 clientes, 34,40 % de todas las cancelaciones).",
       "Lista concreta de segmentos para la campaña de retención.",
       "Se exigió un mínimo de 50 clientes por segmento para evitar tasas engañosas.")
figura("P6_2.png", "Tamaño del segmento frente a su tasa de cancelación (P6)",
       "Los tres primeros segmentos (todos mes a mes con fibra) reúnen el 26,44 % de los clientes, pero el 57,99 % de "
       "las cancelaciones y el 66,83 % del cargo mensual perdido.",
       "Enfocar la campaña en cerca de 1.860 clientes en lugar de toda la base.",
       "Combinar más variables reduce el tamaño de los grupos.")

# ======================================================== 13. CONCLUSIONES FINALES
h1("13. Conclusiones finales y recomendaciones")
par("El proyecto respondió la necesidad del equipo de retención: identificar en qué grupos de clientes se concentra "
    "la cancelación. Uno de cada cuatro clientes cancela (26,54 %) y ellos representan el 30,50 % del cargo mensual. "
    "La cancelación se concentra en clientes con contrato mes a mes, en su primer año, con fibra óptica, sin seguridad "
    "en línea ni soporte técnico, que pagan con cheque electrónico y tienen cargos mensuales altos. El segmento mes a "
    "mes + fibra + 0–12 meses alcanza 70,20 %.")
par("Recomendaciones para el equipo de retención:")
bullet("Focalizar la campaña en los segmentos mes a mes con fibra óptica y menos de dos años.")
bullet("Ofrecer incentivos para migrar de contratos mes a mes a contratos de uno o dos años.")
bullet("Crear un programa de acompañamiento para el primer año.")
bullet("Ofrecer seguridad en línea y soporte técnico a clientes de fibra que no los tienen.")
bullet("Promover el pago automático frente al cheque electrónico.")
par("Limitaciones: los datos son ficticios; el análisis es descriptivo y no demuestra causas; el cargo mensual perdido "
    "es ingreso y no rentabilidad, porque no hay costos; no hay fechas ni motivos de cancelación. Como trabajo futuro "
    "se propone incorporar costos, motivos y datos en el tiempo para pasar a análisis diagnósticos o predictivos.")

# ======================================================== 14. REFERENCIAS
h1("14. Referencias")
REFS = [
    "BlastChar. (2018). Telco customer churn [Conjunto de datos]. Kaggle. https://www.kaggle.com/datasets/blastchar/telco-customer-churn",
    "Evans, J. R. (2017). Business analytics: Methods, models, and decisions (2.ª ed.). Pearson.",
    "Han, J., Kamber, M. y Pei, J. (2012). Data mining: Concepts and techniques (3.ª ed.). Morgan Kaufmann.",
    "IBM. (2019). Telco customer churn [Conjunto de datos de muestra]. IBM Business Analytics Community.",
    "Knaflic, C. N. (2015). Storytelling with data: A data visualization guide for business professionals. Wiley.",
    "Lhoest, Q., Villanova del Moral, A., Jernite, Y., Thakur, A., von Platen, P., Patil, S., … Wolf, T. (2021). Datasets: A community library for natural language processing. En Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing: System Demonstrations (pp. 175–184). Association for Computational Linguistics. https://doi.org/10.18653/v1/2021.emnlp-demo.21",
    "McKinney, W. (2010). Data structures for statistical computing in Python. En Proceedings of the 9th Python in Science Conference (pp. 56–61). https://doi.org/10.25080/Majora-92bf1922-00a",
    "Plotly Technologies Inc. (2015). Collaborative data science. Plotly Technologies Inc. https://plot.ly",
    "Reichheld, F. F. y Sasser, W. E. (1990). Zero defections: Quality comes to services. Harvard Business Review, 68(5), 105–111.",
    "scikit-learn. (2022). churn-prediction [Conjunto de datos; revisión aa09900]. Hugging Face. Recuperado el 25 de octubre de 2026 de https://huggingface.co/datasets/scikit-learn/churn-prediction",
    "Streamlit Inc. (2024). Streamlit documentation. Recuperado el 23 de noviembre de 2026 de https://docs.streamlit.io",
    "The pandas development team. (2024). pandas documentation. Recuperado el 8 de noviembre de 2026 de https://pandas.pydata.org/docs/",
    "Verbeke, W., Dejaeger, K., Martens, D., Hur, J. y Baesens, B. (2012). New insights into churn prediction in the telecommunication sector: A profit driven data mining approach. European Journal of Operational Research, 218(1), 211–229. https://doi.org/10.1016/j.ejor.2011.09.031",
    "Wickham, H. (2014). Tidy data. Journal of Statistical Software, 59(10), 1–23. https://doi.org/10.18637/jss.v059.i10",
]
for r in REFS:
    p = par(r)
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.first_line_indent = Inches(-0.5)

# ======================================================== ANEXO A
for p in d.paragraphs:
    if "gitlab.com" in p.text:
        set_text(p, f"Repositorio: {REPO}")
    if p.text.startswith("El código, los notebooks ejecutados"):
        set_text(p, "El código, los notebooks ejecutados, los datos preparados, las tablas, la aplicación y este "
                    "documento están en el repositorio del proyecto, organizados por etapa (AE2/, AE3/ y AE4/):")
ultimo = [p for p in d.paragraphs if p.style.name == "List Bullet" and p.text.startswith("AE3/documento")][-1]
for texto in reversed([
    "AE4/app_Actividad5.py: aplicación de Streamlit con métricas, gráficos y conclusiones.",
    "AE4/requirements.txt: dependencias de la aplicación (streamlit, pandas, plotly).",
    "AE4/documento/: este informe final en Word y PDF.",
    "AE4/capturas/ y AE4/figuras/: capturas de la aplicación usadas en este informe.",
] + ([f"Aplicación publicada: {URL_APP}"] if URL_APP else [])):
    e = copy.deepcopy(ultimo._p); ultimo._p.addnext(e)
    set_text(Paragraph(e, ultimo._parent), texto)

# quitar nota de "no se incluyen graficas"
for p in d.paragraphs:
    if p.text.startswith("En esta entrega no se incluyen gráficas"):
        p._p.getparent().remove(p._p)

OUT.parent.mkdir(parents=True, exist_ok=True)
d.save(OUT)
print("OK", OUT, CONT)
