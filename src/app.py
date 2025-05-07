from flask import Flask, render_template, request ,redirect, url_for, send_file
import base64
import io
import matplotlib.pyplot as plt
from db import *
from json_loader import cargar_datos_json
from data_processor import *
import matplotlib.pyplot as plt
from generar_graficos import *
from generador_pdf import *
app = Flask(__name__)


@app.route('/')
def inicializar_db():
    # Crear tablas si no existen
    crear_tablas()    
    # Cargar los datos del archivo JSON
    data = cargar_datos_json()
    # Insertar datos en la base de datos
    insertar_datos_iniciales(data)
    return render_template("index.html")

@app.route('/top_clientes', methods=['GET', 'POST'])
def top_clientes_con_mas_incidencias():
    top_x = 5  
    if request.method == 'POST':
        top_x = int(request.form.get('top_x', 5))
    df_clientes = obtener_top_clientes_por_incidencias(top_x)
    # Generar gráfico
    grafico_top_clientes(df_clientes, top_x)
    clientes=df_clientes.to_dict(orient='records')
    return render_template('top_clientes.html',
                           top_x=top_x,
                           clientes=clientes,
                    )
    
@app.route('/top_incidencias', methods=['GET', 'POST'])
def top_tipos_de_incidencias_con_mayor_resolucion():
    top_x = 5  
    if request.method == 'POST':
        top_x = int(request.form.get('top_x', 5))
    df_incidencias = obtener_top_tipos_incidencias_por_tiempo_trabajado(top_x)
    # Generar gráfico
    grafico_top_incidencias(df_incidencias, top_x)
    incidencias=df_incidencias.to_dict(orient='records')
    return render_template('top_incidencias.html',
                           top_x=top_x,
                           incidencias=incidencias,
                           )
@app.route('/vulnerabilidades')
def ultimas_vulnerabilidades():
    ultimos_cves = obtener_ultimos_cves(10)
    return render_template('vulnerabilidades.html', cves=ultimos_cves)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Filtros para cada top
    top_x_clientes = 5  
    top_x_incidencias = 5
    
    if request.method == 'POST':
        top_x_clientes = int(request.form.get('top_x_clientes', 5))
        top_x_incidencias = int(request.form.get('top_x_incidencias', 5))
    
    # Obtener los datos para los top de clientes y incidencias
    df_clientes = obtener_top_clientes_por_incidencias(top_x_clientes)
    grafico_top_clientes(df_clientes, top_x_clientes)
    
    df_incidencias = obtener_top_tipos_incidencias_por_tiempo_trabajado(top_x_incidencias)
    grafico_top_incidencias(df_incidencias, top_x_incidencias)
    ultimos_cves = obtener_ultimos_cves(10)
    
    return render_template('dashboard.html',
                           top_x_clientes=top_x_clientes,
                           top_x_incidencias=top_x_incidencias, cves=ultimos_cves,
                           )

@app.route('/ejercicio_libre', methods=['GET', 'POST'])
def ejercicio_libre():
    # Valores predeterminados
    top_x_clientes = 5
    top_x_incidencias = 5
    top_x_vulnerabilidades = 10

    if request.method == 'POST':
        # Recibir los datos del formulario y actualizar los valores
        top_x_clientes = int(request.form.get('top_x_clientes', top_x_clientes))
        top_x_incidencias = int(request.form.get('top_x_incidencias', top_x_incidencias))
        top_x_vulnerabilidades = int(request.form.get('top_x_vulnerabilidades', top_x_vulnerabilidades))

    # Obtener los datos actualizados para los tres parámetros
    df_clientes = obtener_top_clientes_por_incidencias(top_x_clientes)
    grafico_top_clientes(df_clientes, top_x_clientes)

    df_incidencias = obtener_top_tipos_incidencias_por_tiempo_trabajado(top_x_incidencias)
    grafico_top_incidencias(df_incidencias, top_x_incidencias)

    ultimos_cves = obtener_ultimos_cves(top_x_vulnerabilidades)

    # Retornar el renderizado de la página con los nuevos valores
    return render_template('ejercicio_libre.html',
                           top_x_clientes=top_x_clientes,
                           top_x_incidencias=top_x_incidencias,
                           top_x_vulnerabilidades=top_x_vulnerabilidades,
                           cves=ultimos_cves)
@app.route('/generar_pdf')
def generar_pdf():
    top_x_clientes = int(request.args.get('top_x_clientes', 5))  
    top_x_incidencias = int(request.args.get('top_x_incidencias', 5))
    top_x_vulnerabilidades = int(request.args.get('top_x_vulnerabilidades', 10))

    # Obtener los datos y gráficas
    df_clientes = obtener_top_clientes_por_incidencias(top_x_clientes)
    grafico_top_clientes_path = grafico_top_clientes(df_clientes, top_x_clientes)
    
    df_incidencias = obtener_top_tipos_incidencias_por_tiempo_trabajado(top_x_incidencias)
    grafico_top_incidencias_path = grafico_top_incidencias(df_incidencias, top_x_incidencias)

    # Pasar los DataFrame y los paths a la función de generación de PDF
    pdf_file = generar_pdf_reporte(
        df_clientes, 
        top_x_clientes, 
        df_clientes.to_dict(orient='records'),  # Pasamos la versión en diccionario de df_clientes
        top_x_incidencias, 
        df_incidencias.to_dict(orient='records'),  # Pasamos la versión en diccionario de df_incidencias
        top_x_vulnerabilidades, 
        grafico_top_clientes_path,  # Asegúrate de que estás pasando esta variable
        grafico_top_incidencias_path  # Asegúrate de que estás pasando esta variable
    )

    # Devolver el PDF como archivo adjunto para su descarga
    return send_file(pdf_file, as_attachment=True, download_name="reporte.pdf", mimetype="application/pdf")


if __name__ == '__main__':
    app.run(debug=False)