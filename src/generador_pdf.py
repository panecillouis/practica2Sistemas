from fpdf import FPDF
from data_processor  import obtener_ultimos_cves
import os
from io import BytesIO
import tempfile
import shutil

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
    grafico_top_clientes_path,
    grafico_top_incidencias_path
):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Informe de Seguridad", ln=True)

    # --- Sección: Clientes ---
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Top {top_x_clientes} Clientes con más Incidencias", ln=True)

    # Usamos df_clientes directamente
    for idx, row in df_clientes.head(top_x_clientes).iterrows():
        pdf.cell(0, 10, f"{row['nombre_cliente']} - {row['num_incidencias']} incidencias", ln=True)

    # Imagen: gráfico de clientes
    try:
        grafico_clientes_temp = imagen_a_ruta_temporal(grafico_top_clientes_path)
        pdf.image(grafico_clientes_temp, w=180)
    finally:
        if os.path.exists(grafico_clientes_temp):
            os.unlink(grafico_clientes_temp)
    
    # --- Sección: Tipos de Incidencia ---
    pdf.ln(10)
    pdf.cell(0, 10, f"Top {top_x_incidencias} Tipos de Incidencias por Tiempo Promedio", ln=True)

    # Usamos df_incidencias directamente
    for idx, row in df_incidencias.head(top_x_incidencias).iterrows():
        pdf.cell(0, 10, f"{row['nombre_tipo_incidencia']} - {round(row['tiempo_trabajado_promedio'], 2)} horas", ln=True)

    # Imagen: gráfico de incidencias
    try:
        grafico_incidencias_temp = imagen_a_ruta_temporal(grafico_top_incidencias_path)
        pdf.image(grafico_incidencias_temp, w=180)
    finally:
        if os.path.exists(grafico_incidencias_temp):
            os.unlink(grafico_incidencias_temp)

    # --- Sección: Vulnerabilidades ---
    pdf.ln(10)
    pdf.cell(0, 10, f"Top {top_x_vulnerabilidades} Vulnerabilidades Más Frecuentes", ln=True)
    
    # Aquí puedes incluir la lógica para mostrar las vulnerabilidades si tienes los datos disponibles

    # Guardar PDF
    output_path = "src/static/pdf/informe_seguridad.pdf"
    pdf.output(output_path)
    return output_path

