import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import tempfile
import requests
from io import BytesIO
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

st.set_page_config(page_title="Catálogo Template", page_icon="📦")
st.title("📊 Catálogo Corporativo Editable (Template)")

uploaded_file = st.file_uploader("Sube tu archivo de credenciales (.json)", type="json")

# --- Cargar datos desde Google Sheets ---
def cargar_datos(credenciales):
    try:
        scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp:
            temp.write(credenciales.read())
            temp_path = temp.name
        creds = ServiceAccountCredentials.from_json_keyfile_name(temp_path, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Catalogo").sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # Garantizar columna 'categoria'
        if "categoria" in df.columns:
            df["categoria"] = df["categoria"].fillna(df.get("Categoria","Sin categoría"))
        elif "Categoria" in df.columns:
            df["categoria"] = df["Categoria"].fillna("Sin categoría")
        else:
            df["categoria"] = "Sin categoría"
        return df
    except Exception as e:
        st.error(f"🚫 Error al conectar con Google Sheets: {e}")
        return None

# --- Cargar datos ---
if uploaded_file is not None:
    if st.button("Cargar datos"):
        df = cargar_datos(uploaded_file)
        if df is not None and not df.empty:
            st.success("✅ Datos cargados correctamente.")
            st.dataframe(df)
            st.session_state["df"] = df
        else:
            st.warning("No se encontraron datos o la hoja está vacía.")
else:
    st.info("🔹 Sube tu archivo de credenciales JSON para comenzar.")

# --- Función para numerar páginas ---
def add_page_number(canvas, doc):
    page_num = canvas.getPageNumber()
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(A4[0]-2*cm, 1*cm, f"Página {page_num} - {datetime.today().strftime('%d/%m/%Y')}")

# --- Función para generar catálogo template ---
def generar_catalogo_template(df, logo_path="logo.png", fondo_portada_path="fondo_portada.jpg", mini_logo_path=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TituloPrincipal", fontSize=24, leading=28, alignment=1, spaceAfter=20, textColor=colors.HexColor("#1F618D")))
    styles.add(ParagraphStyle(name="ProductoTitulo", fontSize=12, leading=14, alignment=1, textColor=colors.HexColor("#2C3E50")))
    styles.add(ParagraphStyle(name="ProductoTexto", fontSize=10, leading=12, alignment=1))

    # --- Portada con fondo y logo ---
    try:
        fondo = Image(fondo_portada_path, width=A4[0], height=A4[1])
        story.append(fondo)
    except:
        pass
    try:
        logo = Image(logo_path, width=6*cm, height=6*cm)
        logo.hAlign = "CENTER"
        story.append(Spacer(1,5*cm))
        story.append(logo)
    except:
        story.append(Spacer(1,10*cm))

    story.append(Paragraph("📦 Catálogo Corporativo Editable", styles["TituloPrincipal"]))
    story.append(PageBreak())

    # --- Productos por categoría ---
    categorias = df['categoria'].unique()
    for cat in categorias:
        cat_data = df[df['categoria']==cat]
        story.append(Paragraph(f"Categoría: {cat}", ParagraphStyle(
            name="CategoriaTitulo", fontSize=16, leading=20, textColor=colors.white,
            backColor=colors.HexColor("#2E86C1"), alignment=0, spaceAfter=12, spaceBefore=12
        )))

        productos_por_fila = 2
        filas_por_pagina = 3
        productos_por_pagina = productos_por_fila * filas_por_pagina

        for i in range(0, len(cat_data), productos_por_pagina):
            page_data = cat_data.iloc[i:i+productos_por_pagina]
            celdas = []
            fila = []

            for _, row in page_data.iterrows():
                nombre = str(row.get("nombre", row.get("Nombre",""))) or "N/A"
                precio = str(row.get("precio", row.get("Precio",""))) or "N/A"
                stock = str(row.get("stock", row.get("Stock",""))) or "N/A"
                imagen_url = str(row.get("imagen", row.get("Imagen",""))) or ""

                # --- Imagen o placeholder ---
                if imagen_url.lower() in ["", "nan"]:
                    img = Table([[Paragraph("Imagen no disponible", styles["ProductoTexto"])]], colWidths=[5*cm], rowHeights=[5*cm])
                    img.setStyle(TableStyle([
                        ("BACKGROUND",(0,0),(-1,-1),colors.lightgrey),
                        ("ALIGN",(0,0),(-1,-1),"CENTER"),
                        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                        ("BOX",(0,0),(-1,-1),0.25,colors.grey)
                    ]))
                else:
                    try:
                        if "drive.google.com" in imagen_url:
                            if "/d/" in imagen_url:
                                file_id = imagen_url.split("/d/")[1].split("/")[0]
                            elif "id=" in imagen_url:
                                file_id = imagen_url.split("id=")[1].split("&")[0]
                            else:
                                file_id = ""
                            if file_id:
                                imagen_url = f"https://drive.google.com/uc?export=view&id={file_id}"
                        response = requests.get(imagen_url, timeout=10)
                        if response.status_code==200:
                            img_data = BytesIO(response.content)
                            img = Image(img_data, width=5*cm, height=5*cm)
                        else:
                            raise ValueError("No se pudo descargar imagen")
                    except:
                        img = Table([[Paragraph("Imagen no disponible", styles["ProductoTexto"])]], colWidths=[5*cm], rowHeights=[5*cm])
                        img.setStyle(TableStyle([
                            ("BACKGROUND",(0,0),(-1,-1),colors.lightgrey),
                            ("ALIGN",(0,0),(-1,-1),"CENTER"),
                            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                            ("BOX",(0,0),(-1,-1),0.25,colors.grey)
                        ]))

                # --- Mini logo opcional ---
                mini_logo = None
                if mini_logo_path:
                    try:
                        mini_logo_img = Image(mini_logo_path, width=1.5*cm, height=1.5*cm)
                        mini_logo_img.hAlign = "RIGHT"
                        mini_logo = mini_logo_img
                    except:
                        mini_logo = None

                # --- Ficha de producto editable ---
                ficha = [img, Paragraph(f"<b>{nombre}</b>", styles["ProductoTitulo"])]
                if mini_logo: ficha.append(mini_logo)
                ficha.extend([Paragraph(f"Precio: ${precio}", styles["ProductoTexto"]),
                              Paragraph(f"Stock: {stock}", styles["ProductoTexto"])])

                ficha_table = Table([[ficha[0]],[ficha[1]] + ([ficha[2]] if mini_logo else []), [ficha[-2]],[ficha[-1]]])
                ficha_table.setStyle(TableStyle([
                    ("ALIGN",(0,0),(-1,-1),"CENTER"),
                    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                    ("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#2980B9")),
                    ("BACKGROUND",(0,0),(-1,0),colors.whitesmoke),
                    ("TOPPADDING",(0,0),(-1,-1),5),
                    ("BOTTOMPADDING",(0,0),(-1,-1),5)
                ]))

                fila.append(ficha_table)
                if len(fila)==productos_por_fila:
                    celdas.append(fila)
                    fila = []

            if fila:
                celdas.append(fila)

            tabla = Table(celdas, colWidths=[9*cm]*productos_por_fila)
            tabla.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),
                                       ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                                       ("TOPPADDING",(0,0),(-1,-1),10),
                                       ("BOTTOMPADDING",(0,0),(-1,-1),10)]))
            story.append(tabla)
            story.append(Spacer(1,1*cm))

        story.append(PageBreak())

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    buffer.seek(0)
    return buffer

# --- Botón para generar PDF template ---
if "df" in st.session_state:
    df = st.session_state["df"]
    st.subheader("📄 Generar catálogo Template PDF")
    if st.button("📘 Generar PDF Template"):
        pdf_buffer = generar_catalogo_template(df, logo_path="logo.png", fondo_portada_path="fondo_portada.jpg", mini_logo_path="mini_logo.png")
        st.success("Catálogo template generado ✅")
        st.download_button(
            label="⬇️ Descargar PDF Template",
            data=pdf_buffer,
            file_name="catalogo_template.pdf",
            mime="application/pdf"
        )
