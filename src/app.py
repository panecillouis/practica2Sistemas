from flask import Flask, render_template, request ,redirect, url_for, send_file, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import Usuario, usuarios, cargar_usuarios_registrados, guardar_usuarios_registrados, cifrar_contraseña, verificar_contraseña, obtener_usuario_por_nombre
import base64
import io
import matplotlib
matplotlib.use('Agg') # Usar Agg para evitar problemas con el backend de la GUI
import matplotlib.pyplot as plt
from db import *
from json_loader import cargar_datos_json
from data_processor import *
from generar_graficos import *
from generador_pdf import *
from ticket_classifier import predecir_ticket 
import json

app = Flask(__name__)
app.secret_key = "clave_secreta"
app.config['SESSION_PERMANENT'] = False

@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "-1"
    return response

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def cargar_usuario(user_id):
    return usuarios.get(user_id)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirmar_password = request.form.get('confirmar_password')
        avatar_url = request.form.get('avatar_url')

        # Validar que las contraseñas coincidan
        if password != confirmar_password:
            flash("Las contraseñas no coinciden", "danger")
            return redirect(url_for('registro'))

        # Buscar empleado por nombre
        usuario = obtener_usuario_por_nombre(username)
        if usuario:
            # Cargar usuarios registrados
            usuarios_registrados = cargar_usuarios_registrados()

            # Verificar si el usuario ya está registrado
            if str(usuario.id) in usuarios_registrados:
                flash("El usuario ya está registrado", "warning")
            else:
                # Usar la URL proporcionada o asignar una predeterminada
                avatar = avatar_url if avatar_url else "https://globalsymbols.com/uploads/production/image/imagefile/17674/17_17675_41ec0485-a97d-467f-80e3-9eb573ded0da.png"

                # Cifrar la contraseña y guardar el usuario
                usuarios_registrados[usuario.id] = {
                    "username": usuario.username,
                    "password": cifrar_contraseña(password),
                    "nivel": usuario.nivel,
                    "fecha_contrato": usuario.fecha_contrato,
                    "avatar": avatar
                }
                guardar_usuarios_registrados(usuarios_registrados)
                flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
                return redirect(url_for('login'))
        else:
            flash("Usuario no encontrado en el sistema", "danger")
    
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Buscar empleado por nombre
        usuario = obtener_usuario_por_nombre(username)
        if usuario:
            # Cargar usuarios registrados
            usuarios_registrados = cargar_usuarios_registrados()

            # Verificar si el usuario está registrado
            usuario_registrado = usuarios_registrados.get(str(usuario.id))
            if usuario_registrado:
                if verificar_contraseña(password, usuario_registrado["password"]):
                    login_user(usuario)
                    flash("Inicio de sesión exitoso", "success")
                    return redirect(url_for('perfil'))
                else:
                    flash("Usuario o contraseña incorrectos", "danger")
            else:
                flash("Usuario no registrado. Por favor, regístrate primero.", "warning")
                return redirect(url_for('registro'))

        else:
            flash("Usuario no encontrado en el sistema", "danger")
    
    return render_template('login.html')

@app.route('/perfil')
@login_required
def perfil():
    return render_template("perfil.html", usuario=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada exitosamente", "info")
    return redirect(url_for('login'))

@app.route('/')
def inicializar_db():
    # Crear tablas si no existen
    crear_tablas()    
    # Cargar los datos del archivo JSON
    data = cargar_datos_json()
    # Insertar datos en la base de datos
    insertar_datos_iniciales(data)
    return render_template("index.html", usuario=current_user)

@app.route('/top_clientes', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
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
                           usuario=current_user)

@app.route('/ejercicio_libre', methods=['GET', 'POST'])
@login_required
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
@login_required
def generar_pdf():
    top_x_clientes = int(request.args.get('top_x_clientes', 5))  
    top_x_incidencias = int(request.args.get('top_x_incidencias', 5))
    top_x_vulnerabilidades = int(request.args.get('top_x_vulnerabilidades', 10))

    # Obtener los datos y gráficas
    df_clientes = obtener_top_clientes_por_incidencias(top_x_clientes)
    grafico_top_clientes_path = grafico_top_clientes(df_clientes, top_x_clientes)
    
    df_incidencias = obtener_top_tipos_incidencias_por_tiempo_trabajado(top_x_incidencias)
    grafico_top_incidencias_path = grafico_top_incidencias(df_incidencias, top_x_incidencias)

    # Obtener los datos de vulnerabilidades usando obtener_ultimos_cves
    vulnerabilidades = obtener_ultimos_cves(top_x_vulnerabilidades)
    df_vulnerabilidades = pd.DataFrame(vulnerabilidades)  # Convertir la lista en un DataFrame

    # Renombrar las columnas para que coincidan con las esperadas
    df_vulnerabilidades.rename(columns={"id": "nombre_vulnerabilidad", "descripcion": "frecuencia"}, inplace=True)

    # Verificar las columnas del DataFrame
    if 'nombre_vulnerabilidad' not in df_vulnerabilidades.columns or 'frecuencia' not in df_vulnerabilidades.columns:
        print("Error: Las columnas esperadas no están presentes en df_vulnerabilidades.")
        return "Error: No se pudieron procesar las vulnerabilidades", 500

    # Pasar los DataFrame y los paths a la función de generación de PDF
    pdf_file = generar_pdf_reporte(
        df_clientes, 
        top_x_clientes, 
        df_incidencias, 
        top_x_incidencias, 
        top_x_vulnerabilidades, 
        df_vulnerabilidades,  
        grafico_top_clientes_path, 
        grafico_top_incidencias_path
    )

    # Devolver el PDF como archivo adjunto para su descarga
    return send_file(pdf_file, as_attachment=True, download_name="reporte.pdf", mimetype="application/pdf")

@app.route("/prediccion_cliente", methods=["GET", "POST"])
def prediccion_cliente():
    if request.method == "GET":
        # Cargar datos de clientes e incidentes desde la base de datos
        clientes = obtener_clientes()
        incidentes = obtener_tipos_incidencias()
        return render_template("ticket_form.html", clientes=clientes, incidentes=incidentes)
    elif request.method == "POST":
        try:
            # Recoge el formulario y envía a la función de predicción
            resultado, grafico = predecir_ticket(request.form)
            return render_template("ticket_result.html", resultado=resultado, plot_data=grafico)
        except Exception as e:
            return render_template("ticket_result.html", resultado=f"Error en la predicción: {e}", plot_data=None)

if __name__ == '__main__':
    app.run(debug=False)