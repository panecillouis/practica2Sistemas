import matplotlib.pyplot as plt
import numpy as np
import os
import textwrap


def carpeta_graficos_existe():
    """
    Verifica si la carpeta de gráficos existe y la crea si no es así.
    """
    base_dir = os.path.dirname(__file__)  # Esto apunta a la carpeta donde está app.py
    graficos_dir = os.path.join(base_dir, 'static/graficos')
    
    if not os.path.exists(graficos_dir):
        os.makedirs(graficos_dir)
    
    return graficos_dir
    


def grafico_top_clientes(df_clientes, top_x):
    """
    Genera un gráfico de barras para los clientes con más incidencias.
    """
    print(df_clientes)
    nombres = df_clientes['nombre_cliente'].to_numpy()
    nombres_divididos = [textwrap.fill(nombre, width=20) for nombre in nombres]
    incidencias = df_clientes['num_incidencias'].to_numpy()
    plt.figure(figsize=(16, 8))
    plt.bar(nombres_divididos, incidencias, color='skyblue', width=0.6)
    plt.xlabel('Cliente', fontsize=16, labelpad=20)
    plt.ylabel('Número de Incidencias', fontsize=16, labelpad=20)
    plt.title(f'Top {top_x} Clientes con Más Incidencias', fontsize=18)
    plt.xticks(rotation=45, ha='center', fontsize=14)
    plt.yticks(fontsize=14)
    
    # Asegúrate de que la carpeta 'graficos' exista
    base_dir = os.path.dirname(__file__)  # Esto apunta a la carpeta donde está app.py
    
    graficos_dir = carpeta_graficos_existe()
    ruta_graficos = os.path.join(graficos_dir, 'top_clientes.png')
    print(ruta_graficos)
    os.makedirs(graficos_dir, exist_ok=True)



    plt.tight_layout()
    plt.savefig(ruta_graficos)
    plt.close()
    return ruta_graficos

def grafico_top_incidencias(df_incidencias, top_x):
    """
    Genera un gráfico de barras para los tipos de incidencias con mayor tiempo de resolución.
    """
    print(df_incidencias)
    tipos = df_incidencias['nombre_tipo_incidencia'].to_numpy()
    tiempos = df_incidencias['tiempo_trabajado_promedio'].to_numpy()
    nombres_divididos = [textwrap.fill(tipo, width=20) for tipo in tipos]
    plt.figure(figsize=(16, 8))
    plt.bar(nombres_divididos, tiempos, color='lightpink', width=0.6)
    plt.xlabel('Tipo de Incidencia', fontsize=16, labelpad=20)
    plt.ylabel('Tiempo de Resolución Promedio (horas)', fontsize=16, labelpad=20)
    plt.title(f'Top {top_x} Tipos de Incidencias con Mayor Tiempo de Resolución', fontsize=18)
    plt.xticks(rotation=0, ha='center', fontsize=14)
    plt.yticks(fontsize=14)
    plt.tight_layout()
    
    # Asegúrate de que la carpeta 'graficos' exista
    base_dir = os.path.dirname(__file__)  # Esto apunta a la carpeta donde está app.py
    
    graficos_dir = os.path.join(base_dir, 'static\graficos')
        
    ruta_graficos = os.path.join(base_dir, 'static/graficos/top_incidencias.png')

    plt.savefig(ruta_graficos)
    plt.close()
    return ruta_graficos