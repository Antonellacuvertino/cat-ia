"""Genera PDF legibles desde las fuentes Markdown y resultados efectivamente guardados."""
import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

from catia.config import ROOT

OUT = ROOT / "deliverables"
GREEN = colors.HexColor("#173f32")
MUTED = colors.HexColor("#687769")
LIME = colors.HexColor("#d9eea6")
PAPER = colors.HexColor("#f6f8f4")


def register_fonts():
    # Deja fuentes estándar como alternativa portable en otros sistemas.
    """Registra fuentes disponibles para renderizar los PDF con tipografía consistente."""
    regular = Path("C:/Windows/Fonts/arial.ttf")
    bold = Path("C:/Windows/Fonts/arialbd.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("Catia", str(regular)))
        pdfmetrics.registerFont(TTFont("Catia-Bold", str(bold)))
        pdfmetrics.registerFontFamily("Catia", normal="Catia", bold="Catia-Bold", italic="Catia", boldItalic="Catia-Bold")
        return "Catia", "Catia-Bold"
    return "Helvetica", "Helvetica-Bold"


FONT, BOLD = register_fonts()
STYLES = getSampleStyleSheet()
STYLES.add(ParagraphStyle(name="BodyCAT", fontName=FONT, fontSize=10, leading=15,
                         textColor=GREEN, spaceAfter=9, wordWrap="LTR"))
STYLES.add(ParagraphStyle(name="TitleCAT", fontName=BOLD, fontSize=25, leading=31, textColor=GREEN, spaceAfter=22))
STYLES.add(ParagraphStyle(name="HeadingCAT", fontName=BOLD, fontSize=14, leading=19, textColor=GREEN, spaceBefore=14, spaceAfter=9, keepWithNext=True))
STYLES.add(ParagraphStyle(name="BulletCAT", parent=STYLES["BodyCAT"], leftIndent=11, firstLineIndent=-8))


def rich(text):
    """Escapa texto para ReportLab y traduce el marcado de énfasis admitido por el generador."""
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = text.replace("`", "")
    return text


def footer(c, doc):
    """Dibuja el pie de página usado por los documentos técnicos."""
    c.setStrokeColor(colors.HexColor("#dce4d9"))
    c.line(20*mm, 17*mm, 190*mm, 17*mm)
    c.setFont(FONT, 8); c.setFillColor(MUTED)
    c.drawString(20*mm, 12*mm, "CAT-IA | Proyecto académico | Fuentes y resultados trazables")
    c.drawRightString(190*mm, 12*mm, str(doc.page))


def markdown_pdf(source, target):
    """Convierte el subconjunto de Markdown del proyecto en un documento PDF paginado."""
    flow = []
    for block in source.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        if block.startswith("# "):
            flow.append(Paragraph(rich(block[2:]), STYLES["TitleCAT"]))
        elif block.startswith("## "):
            flow.append(Paragraph(rich(block[3:]), STYLES["HeadingCAT"]))
        elif block.startswith("- "):
            for line in block.splitlines():
                flow.append(Paragraph("• " + rich(line.removeprefix("- ")), STYLES["BulletCAT"]))
        else:
            flow.append(Paragraph(rich(block).replace("\n", "<br/>"), STYLES["BodyCAT"]))
    SimpleDocTemplate(str(target), pagesize=A4, rightMargin=20*mm, leftMargin=20*mm,
                      topMargin=22*mm, bottomMargin=24*mm, title=target.stem, author="Equipo CAT-IA").build(flow, onFirstPage=footer, onLaterPages=footer)


def arrow(c, x1, y1, x2, y2):
    """Dibuja una conexión dirigida entre componentes del diagrama."""
    import math
    c.setStrokeColor(colors.HexColor("#68947a")); c.setLineWidth(1.4)
    c.line(x1, y1, x2, y2)
    angle = math.atan2(y2-y1, x2-x1)
    for offset in [-.45, .45]:
        c.line(x2, y2, x2-7*math.cos(angle+offset), y2-7*math.sin(angle+offset))


def box(c, x, y, width, height, title, subtitle="", dark=False):
    """Dibuja un componente de arquitectura con título, subtítulo y estilo."""
    c.setFillColor(GREEN if dark else colors.white)
    c.setStrokeColor(colors.HexColor("#ccdacb"))
    c.roundRect(x, y, width, height, 9, fill=1, stroke=not dark)
    style = ParagraphStyle("box", fontName=BOLD, fontSize=12, leading=15, textColor=colors.white if dark else GREEN, alignment=1)
    p = Paragraph(rich(title), style); _, h = p.wrap(width-20, height)
    p.drawOn(c, x+10, y+height-14-h)
    if subtitle:
        style = ParagraphStyle("smallbox", fontName=FONT, fontSize=9, leading=12, textColor=LIME if dark else MUTED, alignment=1)
        p = Paragraph(rich(subtitle), style); _, h = p.wrap(width-20, height)
        p.drawOn(c, x+10, y+10)


def architecture(c, x=35, y=75, scale=1):
    """Ubica los componentes y sus conexiones para visualizar el flujo de la solución."""
    c.saveState(); c.translate(x,y); c.scale(scale,scale)
    box(c, 0, 290, 180, 65, "Fuentes internas", "7 políticas simuladas")
    box(c, 215, 290, 180, 65, "Fuentes externas", "2 síntesis de Mozilla")
    box(c, 445, 290, 200, 65, "Ingesta y fragmentación", "Manifiesto + hashes + offsets")
    c.setStrokeColor(colors.HexColor("#68947a"));c.setLineWidth(1.4)
    c.line(90,355,90,372);c.line(90,372,545,372)
    arrow(c,545,372,545,355); arrow(c,395,322,445,322)
    box(c,445,180,200,65,"Índice en memoria","TF-IDF / dense opcional")
    arrow(c,545,290,545,245)
    box(c,0,180,180,65,"Operador + API","Ticket validado e impacto")
    box(c,215,180,180,65,"Agente acotado","Recupera + consulta política",True)
    arrow(c,180,212,215,212); arrow(c,445,212,395,212)
    box(c,215,70,180,65,"Contexto y LLM","Prompt versionado + JSON")
    arrow(c,305,180,305,135)
    box(c,445,70,200,65,"Validación y traza","Citas / fallos / abstención")
    arrow(c,395,102,445,102)
    box(c,0,70,180,65,"Revisión humana","Borrador y evidencia",True)
    c.line(545,70,545,49);c.line(545,49,90,49)
    arrow(c,90,49,90,70)
    c.setFont(FONT,9);c.setFillColor(MUTED)
    c.drawString(0,24,"Sin evidencia o salida inválida: abstenerse y derivar. La prioridad se aplica con política interna.")
    c.drawString(0,8,"El diagrama editable Mermaid contiene todas las conexiones; dense es opcional y requiere modelo.")
    c.restoreState()


def build_architecture():
    """Exporta el diagrama de arquitectura como un PDF independiente."""
    path=OUT/"arquitectura.pdf"
    c=canvas.Canvas(str(path),pagesize=(760,520));c.setTitle("Arquitectura CAT-IA")
    c.setFillColor(PAPER);c.rect(0,0,760,520,fill=1,stroke=0)
    c.setFont(BOLD,25);c.setFillColor(GREEN);c.drawString(35,475,"Arquitectura de CAT-IA")
    architecture(c,35,50);c.save()


def result_summary():
    """Lee evidencias guardadas y compone el resumen; no ejecuta nuevas inferencias."""
    report_path = ROOT / "reports/evaluation_demo_test_v2_k4.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else None
    xml = ROOT / "reports/tests.xml"
    suites = ET.parse(xml).getroot().findall("testsuite") if xml.exists() else []
    count = sum(int(s.get("tests",0)) for s in suites)
    failed = sum(int(s.get("failures",0)) + int(s.get("errors",0)) for s in suites)
    coverage_path = ROOT/"reports/coverage.json"
    coverage = json.loads(coverage_path.read_text(encoding="utf-8"))["totals"]["percent_covered"] if coverage_path.exists() else None
    lines = ["# Resultados ejecutados de CAT-IA", "## Evidencia de software",
             f"Pruebas registradas: {count}. Fallos y errores: {failed}. Cobertura de líneas: {coverage:.1f} %." if coverage is not None else "No hay reporte de cobertura.",
             "JUnit: reports/tests.xml. Cobertura: reports/coverage.json. Estos resultados validan software y contratos; los mocks no ejecutan un LLM."]
    browser_path=ROOT/"reports/browser_checks.json"
    if browser_path.exists():
        browser=json.loads(browser_path.read_text(encoding="utf-8"))
        lines += ["## Interfaz en navegador", f"{browser['browser']}. Modo: {browser['mode']}. Comprobaciones completadas: " + "; ".join(browser["checks"]) + ". Capturas incluidas en reports/."]
    if report:
        m=report["metrics"]
        lines += ["## Evaluación del simulador y recuperación lexical",
                  f"Fecha: {report['created_at']}. Casos test: {report['n']}. Proveedor: {report['provider']}. Modelo: {report['model']}.",
                  f"Accuracy categoría: {m['category_accuracy']:.3f}. Macro-F1: {m['category_macro_f1']:.3f}. Accuracy prioridad: {m['priority_accuracy']:.3f}.",
                  f"Precisión documental: {m['context_precision_doc_level']:.3f}. Recall documental: {m['context_recall_doc_level']:.3f}. MRR: {m['mrr']:.3f}.",
                  f"Accuracy abstención: {m['abstention_accuracy']:.3f}. Latencia interna p50: {m['latency_p50_ms']:.2f} ms; p95: {m['latency_p95_ms']:.2f} ms.",
                  "No se atribuyen estas cifras a un LLM. Dataset pequeño y sintético creado junto a la implementación; requiere etiquetas independientes y casos más difíciles.",
                  "## Evaluación semántica",
                  "Fidelidad y relevancia humanas: pendientes de completar en evaluation/revision_humana.csv. El código verifica identificadores y extractos exactos, no que una recomendación esté lógicamente respaldada."]
    dev2=ROOT/"reports/evaluation_demo_dev_v2_k2.json"
    dev4=ROOT/"reports/evaluation_demo_dev_v2_k4.json"
    if dev2.exists() and dev4.exists():
        m2=json.loads(dev2.read_text(encoding="utf-8"))["metrics"]
        m4=json.loads(dev4.read_text(encoding="utf-8"))["metrics"]
        lines += ["## Experimento de recuperación en desarrollo",
                  f"k=2: precisión {m2['context_precision_doc_level']:.3f}, recall {m2['context_recall_doc_level']:.3f}. k=4: precisión {m4['context_precision_doc_level']:.3f}, recall {m4['context_recall_doc_level']:.3f}.",
                  "En los ocho casos dev, k=2 reduce ruido y pierde parte de la cobertura; k=4 conserva más evidencia. Esta comparación respalda priorizar recall en la configuración por defecto, sin declarar que k=4 sea óptimo para otros corpus."]
    real_report_path=ROOT/"reports/evaluation_ollama_test_v3_k4.json"
    if not real_report_path.exists():
        real_report_path=ROOT/"reports/evaluation_ollama_test_v2_k4.json"
    if real_report_path.exists():
        real_report=json.loads(real_report_path.read_text(encoding="utf-8"))
        rm=real_report["metrics"]
        from collections import Counter
        states=Counter(row["result"]["status"] for row in real_report["rows"])
        lines += ["## Evaluación del LLM real",
                  f"Modelo: {real_report['model']}. Prompt: {real_report['config']['prompt_version']}. Casos: {real_report['n']}. Fecha: {real_report['created_at']}.",
                  f"Accuracy categoría: {rm['category_accuracy']:.3f}; macro-F1: {rm['category_macro_f1']:.3f}. Estados: {dict(states)}.",
                  f"Latencia interna p50: {rm['latency_p50_ms']/1000:.2f} s; p95: {rm['latency_p95_ms']/1000:.2f} s. Prueba en CPU; no extrapolar a otros equipos.",
                  "La clasificación incluye abstenciones y fallos como No determinado. La integridad de las citas se impone por contrato; la revisión semántica por los estudiantes sigue pendiente."]
        previous_path=ROOT/"reports/evaluation_ollama_test_v2_k4.json"
        if real_report["config"]["prompt_version"]=="v3" and previous_path.exists():
            previous=json.loads(previous_path.read_text(encoding="utf-8"))["metrics"]
            lines += ["## Comparación de prompts",
                      f"Macro-F1 v2: {previous['category_macro_f1']:.3f}; v3: {rm['category_macro_f1']:.3f}. Se ajustó la taxonomía por intención del ticket.",
                      "El test se inspeccionó para diseñar v3: esta reevaluación es una regresión sobre casos conocidos, no prueba independiente de generalización. Ver reports/OPTIMIZACION_PROMPT.md."]
    smoke = ROOT/"reports/llm_smoke.json"
    if smoke.exists():
        real=json.loads(smoke.read_text(encoding="utf-8"))
        lines += ["## Prueba real de inferencia", f"Modelo: {real['model']}. Estado: {real['status']}. Duración: {real['timings']['total_ms']} ms. Evidencia completa en reports/llm_smoke.json.",
                  "Una consulta real es una prueba de integración; no sustituye evaluación completa del conjunto test ni revisión humana."]
    else:
        lines += ["## Inferencia real", "No hay evidencia guardada de una prueba real en este informe. Instalar/configurar Ollama y ejecutar antes de la defensa."]
    text="\n\n".join(lines)+"\n"
    (ROOT/"reports/RESUMEN_RESULTADOS.md").write_text(text,encoding="utf-8")
    markdown_pdf(text,OUT/"resultados_pruebas.pdf")
    return count,failed,coverage,report


def presentation(summary):
    """Genera las diapositivas desde su fuente Markdown y los resultados disponibles."""
    source=(ROOT/"docs/07_presentacion.md").read_text(encoding="utf-8")
    sections=re.split(r"\n(?=## )",source)
    c=canvas.Canvas(str(OUT/"presentacion_CAT-IA.pdf"),pagesize=(960,540));c.setTitle("CAT-IA · Soporte con evidencia")
    for i,section in enumerate(sections):
        c.setFillColor(GREEN if i==0 else PAPER);c.rect(0,0,960,540,fill=1,stroke=0)
        c.setFillColor(LIME if i==0 else GREEN);c.setFont(BOLD,13);c.drawString(48,490,"CAT-IA / NEXO TI")
        c.setFont(FONT,10);c.drawRightString(912,490,"ISY0101 · LLM + RAG")
        lines=section.strip().splitlines();title=lines[0].lstrip("# ")
        style=ParagraphStyle("slideTitle",fontName=BOLD,fontSize=40 if i==0 else 31,leading=38,textColor=colors.white if i==0 else GREEN)
        p=Paragraph(rich(title),style);_,height=p.wrap(865,100);p.drawOn(c,48,430-height)
        if i==0:
            y=310
            for line in lines[1:]:
                if not line.strip():continue
                style=ParagraphStyle("cover",fontName=FONT,fontSize=20 if y==310 else 14,leading=23,textColor=LIME if y==310 else colors.white)
                p=Paragraph(rich(line),style);_,h=p.wrap(800,100);p.drawOn(c,48,y-h);y-=h+23
        elif "Arquitectura de" in title:
            architecture(c,185,45,0.88)
        else:
            y=340
            content=[line[2:] for line in lines[1:] if line.startswith("- ")]
            if "Pruebas y resultados" in title and summary[3]:
                m=summary[3]["metrics"]
                content=[f"Software: {summary[0]} pruebas, {summary[1]} fallos; cobertura {summary[2]:.1f} %.",
                         f"Recuperación lexical: precisión {m['context_precision_doc_level']:.1%}; recall {m['context_recall_doc_level']:.1%} en 20 casos sintéticos.",
                         "Clasificación demo: simulador por reglas. Sus resultados no miden un LLM.",
                         "Fidelidad y relevancia: revisión humana pendiente; no inferirlas de las citas."]
                real_path=ROOT/"reports/evaluation_ollama_test_v3_k4.json"
                if not real_path.exists():
                    real_path=ROOT/"reports/evaluation_ollama_test_v2_k4.json"
                if real_path.exists():
                    rm=json.loads(real_path.read_text(encoding="utf-8"))["metrics"]
                    content[2]=f"Regresión sintética con Qwen 2.5 1.5B: macro-F1 {rm['category_macro_f1']:.3f}; p50 {rm['latency_p50_ms']/1000:.1f} s en CPU."
            for j,line in enumerate(content):
                c.setFillColor(colors.HexColor("#e0eacb"));c.roundRect(48,y-33,30,30,7,fill=1,stroke=0)
                c.setFillColor(GREEN);c.setFont(BOLD,11);c.drawString(58,y-22,str(j+1))
                style=ParagraphStyle("slideBody",fontName=FONT,fontSize=18,leading=26,textColor=GREEN)
                p=Paragraph(rich(line),style);_,h=p.wrap(790,120);p.drawOn(c,95,y-h);y-=max(h+26,65)
        c.setFont(FONT,9);c.setFillColor(LIME if i==0 else MUTED)
        c.drawString(48,26,"Proyecto académico · Organización y fuentes internas simuladas")
        c.drawRightString(912,26,f"{i+1:02d} / {len(sections):02d}")
        c.showPage()
    c.save()


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for file in sorted((ROOT/"docs").glob("0*.md")):
        if file.name.startswith("07_"):
            continue
        markdown_pdf(file.read_text(encoding="utf-8"),OUT/(file.stem+".pdf"))
    build_architecture()
    summary=result_summary()
    presentation(summary)
    dossier=["# CAT-IA · Dossier del proyecto", "Este documento reúne la propuesta, informe de aplicación, plan de pruebas, manual, preparación de defensa y matriz de evaluación. La presentación y el diagrama PDF se entregan como archivos independientes."]
    for file in sorted((ROOT/"docs").glob("0*.md")):
        if not file.name.startswith("07_"):
            dossier.append(file.read_text(encoding="utf-8"))
    dossier.append((ROOT/"reports/RESUMEN_RESULTADOS.md").read_text(encoding="utf-8"))
    dossier.append((ROOT/"reports/ANALISIS_CUALITATIVO_LLM.md").read_text(encoding="utf-8"))
    markdown_pdf("\n\n".join(dossier),OUT/"dossier_completo_CAT-IA.pdf")
    print("Generados PDF en",OUT)
