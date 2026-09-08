"""Audita límites de texto y renderiza muestras de los PDF con PyMuPDF."""
import json
from pathlib import Path
import pymupdf

ROOT=Path(__file__).resolve().parent.parent

if __name__=="__main__":
    checks=[]
    preview=ROOT/"runtime/pdf-checks"
    preview.mkdir(parents=True,exist_ok=True)
    # Recorre todos los PDF y detecta bloques de texto que exceden los límites físicos de página.
    for file in sorted((ROOT/"deliverables").glob("*.pdf")):
        doc=pymupdf.open(file)
        outside=[]
        for i,page in enumerate(doc):
            for block in page.get_text("blocks"):
                x0,y0,x1,y1=block[:4]
                if x0 < -1 or y0 < -1 or x1 > page.rect.width+1 or y1 > page.rect.height+1:
                    outside.append({"page":i+1,"bounds":[x0,y0,x1,y1]})
        checks.append({"file":file.name,"pages":len(doc),"text_outside_page":outside})
        if file.name=="presentacion_CAT-IA.pdf":
            for index in [0,4,9]:
                doc[index].get_pixmap(matrix=pymupdf.Matrix(1.4,1.4)).save(preview/f"slide-{index+1}.png")
        if file.name=="05_guia_defensa.pdf":
            doc[0].get_pixmap().save(preview/"guia.png")
        doc.close()
    report={"checks":checks,"passed":not any(c["text_outside_page"] for c in checks),
            "scope":"Texto dentro de página; muestras raster para revisión visual, no auditoría semántica."}
    (ROOT/"reports/document_checks.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
    assert report["passed"],"Hay texto fuera de página"
