import sqlite3
import pandas as pd
import requests

def obtener_top_clientes_por_incidencias(top_x):
    df_clientes = obtener_clientes_por_incidencias()
    return df_clientes.head(top_x)
def obtener_top_tipos_incidencias_por_tiempo_trabajado(top_x):
    df_tipos = obtener_tipos_incidencia_por_tiempo_trabajado()
    return df_tipos.head(top_x)

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

def obtener_tipos_incidencia_por_tiempo_trabajado():
    conn = sqlite3.connect('sistema_etl.db')
    
    query = """
    SELECT ti.nombre AS nombre_tipo_incidencia, 
           AVG(ct.tiempo_trabajado) AS tiempo_trabajado_promedio
    FROM Contactos_Empleados_Tickets ct
    JOIN Tickets t ON ct.id_ticket = t.id_ticket
    JOIN Tipos_Incidentes ti ON t.tipo_incidencia = ti.id_tipo
    GROUP BY ti.nombre
    ORDER BY tiempo_trabajado_promedio DESC;
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df
import requests

def obtener_ultimos_cves(n=10):
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage={n}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        cves = []

        for item in data.get("vulnerabilities", []):
            cve_id = item["cve"]["id"]
            descripcion = item["cve"]["descriptions"][0]["value"]
            cves.append({
                "id": cve_id,
                "descripcion": descripcion
            })

        return cves
    except Exception as e:
        print(f"Error al obtener los CVEs: {e}")
        return []
