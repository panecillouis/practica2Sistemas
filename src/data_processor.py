import sqlite3
import pandas as pd

def obtener_clientes_por_incidencias():
    conn = sqlite3.connect('sistema_etl.db')
    
    query = """
    SELECT c.id_cliente, c.nombre_cliente, COUNT(t.id_ticket) AS num_incidencias
    FROM Clientes c
    JOIN Tickets t ON c.id_cliente = t.cliente_id
    GROUP BY c.id_cliente
    ORDER BY num_incidencias DESC;
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def obtener_tipos_incidencia_por_tiempo_respuesta():
    conn = sqlite3.connect('sistema_etl.db')
    
    query = """
    SELECT t.tipo_incidencia, 
           AVG(JULIANDAY(t.fecha_cierre) - JULIANDAY(t.fecha_apertura)) * 24 AS tiempo_respuesta_promedio
    FROM Tickets t
    GROUP BY t.tipo_incidencia
    ORDER BY tiempo_respuesta_promedio DESC;
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df
