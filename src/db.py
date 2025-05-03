import sqlite3
import os
def crear_tablas():
    # Eliminar el archivo si ya existe
    if os.path.exists('sistema_etl.db'):
        os.remove('sistema_etl.db')

    # Crear conexión y continuar con la creación de tablas
    conn = sqlite3.connect('sistema_etl.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Clientes (
        id_cliente INTEGER PRIMARY KEY,
        nombre_cliente TEXT,
        telefono TEXT,
        provincia TEXT
    )
    ''')
    
    # Tabla de Tipos de Incidentes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Tipos_Incidentes (
        id_tipo INTEGER PRIMARY KEY,
        nombre TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Empleados (
        id_empleado INTEGER PRIMARY KEY,
        nombre TEXT,
        nivel INTEGER,
        fecha_contrato TEXT
    )
    ''')
    # Tabla de Tickets
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Tickets (
        id_ticket INTEGER PRIMARY KEY,
        fecha_apertura TEXT,
        fecha_cierre TEXT,
        es_mantenimiento BOOLEAN,
        satisfaccion_cliente INTEGER,
        tipo_incidencia INTEGER,
        es_critico BOOLEAN,
        cliente_id INTEGER,
        FOREIGN KEY (tipo_incidencia) REFERENCES Tipos_Incidentes(id_tipo),
        FOREIGN KEY (cliente_id) REFERENCES Clientes(id_cliente)
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Contactos_Empleados_Tickets (
        id_contacto INTEGER PRIMARY KEY AUTOINCREMENT,
        id_ticket INTEGER,
        id_empleado INTEGER,
        fecha_contacto TEXT,
        tiempo_trabajado REAL,
        FOREIGN KEY (id_ticket) REFERENCES Tickets(id_ticket),
        FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
    )
    ''')


    conn.commit()
    conn.close()
def insertar_datos_iniciales(data):
    for ticket in data['tickets_emitidos']:
        id_ticket = insertar_ticket(ticket['cliente'], ticket['fecha_apertura'], 
                                ticket['fecha_cierre'], ticket['es_mantenimiento'],
                                ticket['satisfaccion_cliente'], ticket['tipo_incidencia'],ticket['es_critico'])
    
        if 'contactos_con_empleados' in ticket:
            for contacto in ticket['contactos_con_empleados']:
                insertar_contacto_empleado(id_ticket, contacto['id_emp'], contacto['fecha'], contacto['tiempo'])
    
    for cliente in data["clientes"]:
        insertar_cliente(cliente["id_cli"], cliente["nombre"], cliente["telefono"], cliente["provincia"])

    for tipo in data["tipos_incidentes"]:
        insertar_tipo_incidente(tipo["id_cli"], tipo["nombre"])
        
    for empleado in data["empleados"]:
        insertar_empleado(empleado["id_emp"], empleado["nombre"], empleado["nivel"], empleado["fecha_contrato"])
    

def insertar_cliente(id_cliente, nombre, telefono, provincia):
    conn = sqlite3.connect('sistema_etl.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR IGNORE INTO Clientes (id_cliente, nombre_cliente, telefono, provincia)
    VALUES (?, ?, ?, ?)
    ''', (id_cliente, nombre, telefono, provincia))
    conn.commit()
    conn.close()


def insertar_tipo_incidente(id_tipo, nombre):
    conn = sqlite3.connect('sistema_etl.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR IGNORE INTO Tipos_Incidentes (id_tipo, nombre)
    VALUES (?, ?)
    ''', (id_tipo, nombre))
    conn.commit()
    conn.close()
    
def insertar_ticket(cliente_id, fecha_apertura, fecha_cierre, es_mantenimiento, satisfaccion_cliente, tipo_incidencia, es_critico=False):
    conn = sqlite3.connect('sistema_etl.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO Tickets (cliente_id, fecha_apertura, fecha_cierre, es_mantenimiento, satisfaccion_cliente, tipo_incidencia, es_critico)
    VALUES (?, ?, ?, ?, ?, ?,?)
    ''', (cliente_id, fecha_apertura, fecha_cierre, es_mantenimiento, satisfaccion_cliente, tipo_incidencia, es_critico))
    id_ticket = cursor.lastrowid  # Obtener el ID del ticket recién insertado
    conn.commit()
    conn.close()
    return id_ticket
def insertar_empleado(id_empleado, nombre, nivel, fecha_contrato):
    conn = sqlite3.connect('sistema_etl.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR IGNORE INTO Empleados (id_empleado, nombre, nivel, fecha_contrato)
    VALUES (?, ?, ?, ?)
    ''', (id_empleado, nombre, nivel, fecha_contrato))
    conn.commit()
    conn.close()
def insertar_contacto_empleado(id_ticket, id_empleado, fecha_contacto, tiempo_trabajado):
    conn = sqlite3.connect('sistema_etl.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO Contactos_Empleados_Tickets (id_ticket, id_empleado, fecha_contacto, tiempo_trabajado)
    VALUES (?, ?, ?, ?)
    ''', (id_ticket, id_empleado, fecha_contacto, tiempo_trabajado))
    conn.commit()
    conn.close()

