from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

def generar_guia_pdf(output_path="Guia_Usuario_Catalogo.pdf"):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Título
    titulo = Paragraph("Guía de Usuario - Catálogo de Productos", ParagraphStyle(
        name="Titulo", fontSize=16, alignment=1, spaceAfter=12, textColor="#2E4053"))
    story.append(titulo)
    story.append(Spacer(1, 0.5*cm))

    pasos = [
        "1️⃣ Abrir la aplicación Streamlit y subir el archivo de credenciales JSON proporcionado por Google.",
        "2️⃣ Seleccionar la hoja (pestaña) de Google Sheets que contiene los datos del catálogo.",
        "3️⃣ Revisar que los datos se carguen correctamente en la tabla mostrada en pantalla.",
        "4️⃣ Para diseñadores: hacer clic en 'Generar PDF Mockup Visual' para ver las zonas de edición.",
        "5️⃣ Para obtener el catálogo real: hacer clic en 'Generar Catálogo Real'.",
        "6️⃣ Descargar el PDF generado directamente desde los botones de descarga.",
        "7️⃣ Verificar que las imágenes, nombres, precios y stock se visualicen correctamente en el PDF."
    ]

    for paso in pasos:
        story.append(Paragraph(paso, styles["Normal"]))
        story.append(Spacer(1, 0.4*cm))

    # Nota final
    nota = Paragraph("🔹 Asegúrate de tener las imágenes accesibles mediante URL y que el mini logo esté en la carpeta de la aplicación si se va a usar.",
                     ParagraphStyle(name="Nota", fontSize=10, textColor="#7F8C8D"))
    story.append(nota)

    doc.build(story)
    print(f"Guía PDF generada correctamente en: {output_path}")

# Ejecutar la función
generar_guia_pdf()
