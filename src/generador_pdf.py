from fpdf import FPDF
from data_processor  import obtener_ultimos_cves
import os
from io import BytesIO
import tempfile
import shutil
import datetime

def imagen_a_ruta_temporal(path_original):
    """Copia la imagen a un archivo temporal y devuelve su ruta."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    shutil.copy(path_original, temp_file.name)
    return temp_file.name

def imagen_a_bytesio(ruta_imagen):
    """
    Convierte una imagen en disco (ruta_imagen) a un objeto BytesIO para insertarla en PDF.
    """
    try:
        with open(ruta_imagen, 'rb') as f:
            buffer = BytesIO(f.read())
            buffer.seek(0)
            return buffer
    except FileNotFoundError:
        return None
    
def agregar_linea(pdf):
    pdf.set_draw_color(0, 0, 0) 
    pdf.set_line_width(0.5)    
    pdf.line(10, pdf.get_y(), 200, pdf.get_y()) 
    pdf.ln(5)  

def agregar_pie_pagina(pdf):
    pdf.set_y(-15)  # Posición desde el final de la página
    pdf.set_font("Arial", "I", 8)  # Fuente en cursiva y tamaño pequeño
    pdf.cell(0, 10, f"Informe generado el {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", align="C")
    

class PDF(FPDF):
    def tabla_simple(self, headers, rows):
        self.set_fill_color(220, 220, 220)
        self.set_font("Arial", "B", 12)
        col_widths = [90, 90] if len(headers) == 2 else [190 // len(headers)] * len(headers)

        # Encabezados
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, border=1, fill=True)
        self.ln()

        # Filas
        self.set_font("Arial", "", 11)
        for row in rows:
            for i, cell in enumerate(row):
                cell_text = str(cell)
                if len(cell_text) > 60:
                    cell_text = cell_text[:57] + "..."
                self.cell(col_widths[i], 10, cell_text, border=1)
            self.ln()


def generar_pdf_reporte(
    df_clientes,
    top_x_clientes,
    df_incidencias,
    top_x_incidencias,
    top_x_vulnerabilidades,
    df_vulnerabilidades,
    grafico_top_clientes_path,
    grafico_top_incidencias_path
):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- Página 1: Título, Imagen de Fondo y Autores ---
    pdf.add_page()

    # Agregar imagen de fondo
    try:
        pdf.image("src/static/img/favicon.jpg", x=0, y=0, w=210, h=297)  # Tamaño A4
    except Exception as e:
        print(f"Error al agregar la imagen de fondo: {e}")

    # Título principal
    pdf.set_font("Arial", "B", 24)
    pdf.set_text_color(0, 0, 0)  # Texto negro para que contraste con la imagen
    pdf.cell(0, 10, "Informe de Seguridad", ln=True, align="C")
    pdf.ln(20)

    # Autores
    pdf.set_font("Arial", "I", 14)
    pdf.cell(0, 10, "Autores:", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "Nawal Boukarssanna Bouazaoui", ln=True, align="C")
    pdf.cell(0, 10, "Paula Victoria Carrascosa Mancilla", ln=True, align="C")
    pdf.cell(0, 10, "Alejandro Terrazas Vargas", ln=True, align="C")
    pdf.ln(20)

    # --- Página del índice ---
    pdf.add_page()
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 10, "Índice", ln=True, align="C")
    pdf.ln(10)

    # Lista para almacenar los elementos del índice
    indice_items = []

    # --- Sección: Clientes ---
    indice_items.append((f"Top {top_x_clientes} Clientes con más Incidencias", pdf.page_no() + 1))  # +1 porque la siguiente página será la de contenido

    # --- Sección: Tipos de Incidencia ---
    indice_items.append((f"Top {top_x_incidencias} Tipos de Incidencias por Tiempo Promedio", pdf.page_no() + 1))
    
    # --- Sección: Vulnerabilidades ---
    indice_items.append((f"Top {top_x_vulnerabilidades} Vulnerabilidades Más Frecuentes", pdf.page_no() + 1))

    # --- Completar el índice ---
    pdf.set_font("Arial", "", 12)
    for item, page in indice_items:
        pdf.cell(0, 10, f"{item} - Página {page}", ln=True)

    # --- Sección: Clientes ---
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Top {top_x_clientes} Clientes con más Incidencias", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(100, 10, "Cliente", 1, 0, "C")
    pdf.cell(50, 10, "Incidencias", 1, 1, "C")

    pdf.set_font("Arial", "", 12)
    for idx, row in df_clientes.head(top_x_clientes).iterrows():
        pdf.cell(100, 10, row['nombre_cliente'], 1)
        pdf.cell(50, 10, str(row['num_incidencias']), 1, 1)

    # Línea divisoria
    agregar_linea(pdf)

    # Imagen: gráfico de clientes
    try:
        pdf.image(grafico_top_clientes_path, w=180)
    except Exception as e:
        print(f"Error al agregar la imagen de clientes: {e}")

    # --- Sección: Tipos de Incidencia ---
    pdf.add_page()
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Top {top_x_incidencias} Tipos de Incidencias por Tiempo Promedio", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(120, 10, "Tipo de Incidencia", 1, 0, "C")
    pdf.cell(50, 10, "Tiempo Promedio (horas)", 1, 1, "C")

    pdf.set_font("Arial", "", 12)
    for idx, row in df_incidencias.head(top_x_incidencias).iterrows():
        pdf.cell(120, 10, row['nombre_tipo_incidencia'], 1)
        pdf.cell(50, 10, f"{round(row['tiempo_trabajado_promedio'], 2)}", 1, 1)

    # Línea divisoria
    agregar_linea(pdf)

    # Imagen: gráfico de incidencias
    try:
        pdf.image(grafico_top_incidencias_path, w=180)
    except Exception as e:
        print(f"Error al agregar la imagen de incidencias: {e}")

    # --- Sección: Vulnerabilidades ---
    pdf.add_page()
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Top {top_x_vulnerabilidades} Vulnerabilidades Más Frecuentes", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(60, 10, "ID del CVE", 1, 0, "C")
    pdf.cell(120, 10, "Descripción", 1, 1, "C")

    pdf.set_font("Arial", "", 10)
    for idx, row in df_vulnerabilidades.head(top_x_vulnerabilidades).iterrows():
        pdf.cell(60, 10, row['nombre_vulnerabilidad'], 1)
        pdf.multi_cell(120, 10, row['frecuencia'], border=1)

    # Pie de página
    agregar_pie_pagina(pdf)

    # Guardar el PDF
    output_dir = os.path.join("static", "pdf")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, "informe_seguridad.pdf")
    pdf.output(output_path)
    return output_path
