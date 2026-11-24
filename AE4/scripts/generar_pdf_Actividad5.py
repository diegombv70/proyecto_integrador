"""Convierte el informe AE4 (.docx) a PDF con portada, contenido e indices paginados."""
import html
import re
import sys
import tempfile
from pathlib import Path

import docx
import mammoth
from playwright.sync_api import sync_playwright
from pypdf import PdfReader

DOCX = Path(sys.argv[1]); PDF = Path(sys.argv[2])
URL_APP = sys.argv[3] if len(sys.argv) > 3 else ""

# 1) quitar portada/indices del docx (se rehacen en HTML)
d = docx.Document(DOCX)
body = d.element.body
inicio = next(p for p in d.paragraphs if p.style.name == "Heading 1" and p.text.startswith("1. Introducción"))
for el in list(body):
    if el is inicio._p:
        break
    if not el.tag.endswith("sectPr"):
        body.remove(el)
tmp = Path(tempfile.mkdtemp()) / "cuerpo.docx"
d.save(tmp)

style_map = """
p[style-name='Caption'] => p.caption:fresh
p[style-name='caption'] => p.caption:fresh
p[style-name='Descripción'] => p.caption:fresh
p[style-name='List Bullet'] => ul > li:fresh
p[style-name='List Number'] => ol > li:fresh
"""
with open(tmp, "rb") as f:
    cuerpo = mammoth.convert_to_html(f, style_map=style_map).value

# 2) numerar leyendas e identificar titulos
cont = {"Tabla": 0, "Figura": 0}
entradas = {"toc": [], "Tabla": [], "Figura": []}


def num_caption(m):
    txt = re.sub(r"<[^>]+>", "", m.group(1))
    tipo = "Tabla" if txt.startswith("Tabla") else "Figura"
    cont[tipo] += 1
    titulo = re.sub(r"^(Tabla|Figura)\s*\d*\s*\.\s*", "", txt).strip()
    ident = f"{tipo.lower()}{cont[tipo]}"
    entradas[tipo].append((ident, f"{tipo} {cont[tipo]}", titulo))
    return f'<p class="caption" id="{ident}"><b>{tipo} {cont[tipo]}</b><br><i>{titulo}</i></p>'


cuerpo = re.sub(r'<p class="caption">(.*?)</p>', num_caption, cuerpo)


def num_heading(m):
    nivel, txt = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
    ident = f"h{len(entradas['toc']) + 1}"
    entradas["toc"].append((ident, nivel, html.unescape(txt)))
    return f'<h{nivel} id="{ident}">{m.group(2)}</h{nivel}>'


cuerpo = re.sub(r"<h([12])>(.*?)</h\1>", num_heading, cuerpo)
cuerpo = re.sub(r'(https?://[^\s<"]+)', r'<a href="\1">\1</a>', cuerpo)

CSS = """
@page { size: Letter; margin: 2.3cm 2.3cm 2.3cm 2.3cm; }
body { font-family: Calibri, 'Segoe UI', Arial, sans-serif; font-size: 11pt; line-height: 1.45; color: #1d1d1d; }
p { margin: 0 0 8pt 0; text-align: justify; }
h1 { font-size: 16pt; color: #1F3A5F; break-before: page; margin: 0 0 10pt 0; }
h2 { font-size: 13pt; color: #1F3A5F; margin: 14pt 0 6pt 0; break-after: avoid; }
.caption { margin: 12pt 0 4pt 0; break-after: avoid; text-align: left; }
table { border-collapse: collapse; width: 100%; margin: 2pt 0 4pt 0; font-size: 8pt; line-height: 1.2; }
td, th { border: 1px solid #9aa5b1; padding: 2pt 4pt; vertical-align: top; text-align: left; }
thead th, table:not(:has(thead)) tr:first-child td { background: #1F3A5F; color: white; font-weight: bold; }
td p, th p { text-align: left; margin: 0; }
tr { break-inside: avoid; }
img { max-width: 100%; display: block; margin: 0 auto; border: 1px solid #e3e3e3; }
p:has(> img) { text-align: center; break-inside: avoid; }
ul, ol { margin: 0 0 8pt 0; }
a { color: #1F3A5F; text-decoration: none; word-break: break-all; }
.portada { height: 9in; display: flex; flex-direction: column; justify-content: space-between; text-align: center; }
.portada h0 { display:block; font-size: 15pt; font-weight: bold; color:#1F3A5F; }
.portada .titulo { font-size: 20pt; font-weight: bold; color: #1F3A5F; margin: 18pt 0; line-height: 1.3; }
.portada p { text-align: center; margin: 2pt 0; }
.indice { break-before: page; }
.indice h3 { font-size: 15pt; color: #1F3A5F; margin: 0 0 10pt 0; }
.indice .e { display: flex; margin: 0 0 3pt 0; font-size: 10.5pt; }
.indice .e.n2 { padding-left: 18pt; }
.indice .e .t { flex: 0 1 auto; }
.indice .e .dots { flex: 1; border-bottom: 1px dotted #888; margin: 0 4pt 4pt 4pt; }
.indice .e .pg { flex: 0 0 auto; }
"""


def indice(titulo, items, paginas):
    filas = "".join(
        f'<div class="e {"n2" if n == "2" else ""}"><span class="t"><a href="#{i}">{html.escape(t)}</a></span>'
        f'<span class="dots"></span><span class="pg">{paginas.get(i, "00")}</span></div>' for i, n, t in items)
    return f'<div class="indice"><h3>{titulo}</h3>{filas}</div>'


def documento(paginas):
    portada = f"""
<div class="portada">
 <div><p style="font-size:12pt;color:#555">Institución Universitaria Digital de Antioquia</p></div>
 <div>
  <p style="font-size:14pt;font-weight:bold;color:#1F3A5F">Proyecto integrador – Informe final AE4 (Actividad 5)</p>
  <p class="titulo">Caracterización descriptiva de la cancelación de clientes en una empresa de telecomunicaciones a partir del dataset Telco Customer Churn</p>
  <p style="font-size:13pt">Métricas y visualización de datos</p>
 </div>
 <div>
  <p><b>Integrante:</b> Diego Mauricio Bedoya Valencia</p>
  <p><b>Grupo:</b> PREICA2602B020038</p>
  <p><b>Asignatura:</b> Analítica de Datos</p>
  <p><b>Docente:</b> Andrés Felipe Callejas</p>
  <p style="margin-top:12pt"><b>Repositorio:</b> https://github.com/diegombv70/proyecto_integrador</p>
  {f'<p><b>Aplicación:</b> {URL_APP}</p>' if URL_APP else ''}
 </div>
 <div><p>Medellín, 23 de noviembre de 2026</p></div>
</div>"""
    toc = indice("Tabla de contenido", entradas["toc"], paginas)
    tablas = indice("Índice de tablas", [(i, "1", f"{e}. {t}") for i, e, t in entradas["Tabla"]], paginas)
    figuras = indice("Índice de figuras", [(i, "1", f"{e}. {t}") for i, e, t in entradas["Figura"]], paginas)
    return f"<!doctype html><html lang='es'><head><meta charset='utf-8'><style>{CSS}</style></head><body>{portada}{toc}{tablas}{figuras}{cuerpo}</body></html>"


PIE = ('<div style="font-size:8pt;width:100%;text-align:center;color:#666;font-family:Calibri,Arial">'
       '<span class="pageNumber"></span></div>')


def render(html_txt, destino):
    f = destino.with_suffix(".html"); f.write_text(html_txt, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch(channel="msedge")
        pg = b.new_page(); pg.goto(f.as_uri()); pg.wait_for_load_state("networkidle")
        pg.pdf(path=str(destino), format="Letter", print_background=True, display_header_footer=True,
               header_template="<span></span>", footer_template=PIE, prefer_css_page_size=True)
        b.close()
    f.unlink()


import unicodedata
norm = lambda s: re.sub(r"\s+", "", unicodedata.normalize("NFKC", s)).lower()
render(documento({}), PDF)
textos = [norm(pg.extract_text() or "") for pg in PdfReader(PDF).pages]
inicio_cuerpo = next(k for k, t in enumerate(textos) if norm("1. Introducción") in t and k > 3)
paginas = {}
todos = [(i, t) for i, _, t in entradas["toc"]] + [(i, f"{e}{t}") for i, e, t in entradas["Tabla"] + entradas["Figura"]]
for ident, texto in todos:
    clave = norm(texto)[:45]
    for k in range(inicio_cuerpo, len(textos)):
        if clave in textos[k]:
            paginas[ident] = k + 1
            break
faltan = [i for i, _ in todos if i not in paginas]
render(documento(paginas), PDF)
print("paginas:", len(PdfReader(PDF).pages), "| sin pagina:", faltan, "| tablas:", cont["Tabla"], "figuras:", cont["Figura"])
