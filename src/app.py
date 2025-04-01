from flask import Flask, render_template
import base64
import io
import matplotlib.pyplot as plt
from db import *
from json_loader import cargar_datos_json
from data_processor import *
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/inicializar')
def inicializar_db():
    # Crear tablas si no existen
    crear_tablas()
    
    # Cargar los datos del archivo JSON
    data = cargar_datos_json()
    
    # Insertar datos en la base de datos
    for ticket in data['tickets_emitidos']:
        id_ticket = insertar_ticket(ticket['cliente'], ticket['fecha_apertura'], 
                                ticket['fecha_cierre'], ticket['es_mantenimiento'], 
                                ticket['satisfaccion_cliente'], ticket['tipo_incidencia'])
    
        if 'contactos_con_empleados' in ticket:
            for contacto in ticket['contactos_con_empleados']:
                insertar_contacto_empleado(id_ticket, contacto['id_emp'], contacto['fecha'], contacto['tiempo'])
    
    for cliente in data["clientes"]:
        insertar_cliente(cliente["id_cli"], cliente["nombre"], cliente["telefono"], cliente["provincia"])

    for tipo in data["tipos_incidentes"]:
        insertar_tipo_incidente(tipo["id_cli"], tipo["nombre"])
        
    for empleado in data["empleados"]:
        insertar_empleado(empleado["id_emp"], empleado["nombre"], empleado["nivel"], empleado["fecha_contrato"])
    
    mensaje = "Base de datos inicializada correctamente."
    return render_template("inicializacion.html", mensaje=mensaje)

  
if __name__ == '__main__':
    app.run(debug=False)