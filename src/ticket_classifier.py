import matplotlib
matplotlib.use('Agg')  # Utilizamos un backend no interactivo para evitar problemas con hilos
import matplotlib.pyplot as plt

import json
import datetime
import io
import base64

import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA

from data_processor import obtener_datos_tickets

features = ["duracion", "es_mantenimiento", "satisfaccion_cliente", "tipo_incidencia", "contacto_total"]

# Cargar datos de tickets desde la base de datos
df = obtener_datos_tickets()
# Procesar datos y crear DataFrame
rows = []
for d in df.to_dict(orient='records'):
    try:
        # Validar que las claves necesarias estén presentes
        if not all(k in d for k in ["fecha_apertura", "fecha_cierre", "es_mantenimiento", "satisfaccion_cliente", "tipo_incidencia", "es_critico"]):
            print(f"Registro ignorado por claves faltantes: {d}")
            continue
        fecha_apertura = datetime.datetime.strptime(d["fecha_apertura"], "%Y-%m-%d")
        fecha_cierre = datetime.datetime.strptime(d["fecha_cierre"], "%Y-%m-%d")
        duracion = (fecha_cierre - fecha_apertura).days
        mantenimiento = 1 if d.get("es_mantenimiento", False) else 0
        satisfaccion = d.get("satisfaccion_cliente", 0)
        incidencia = d.get("tipo_incidencia", 0)
        contactos = d.get("contactos_con_empleados", [])
        contacto_total = sum([c.get("tiempo", 0) for c in contactos])
        es_critico = 1 if d.get("es_critico", False) else 0
        rows.append({
            "duracion": duracion,
            "es_mantenimiento": mantenimiento,
            "satisfaccion_cliente": satisfaccion,
            "tipo_incidencia": incidencia,
            "contacto_total": contacto_total,
            "es_critico": es_critico
        })
    except Exception as ex:
        print(f"Error procesando registro: {d}, Error: {ex}")
        continue
df = pd.DataFrame(rows)

missing_features = [f for f in features if f not in df.columns]
if missing_features:
    print(f"Faltan las siguientes características en el DataFrame: {missing_features}")
    print("Columnas del DataFrame:", df.columns)
    print("Primeros registros del DataFrame:")
    print(df.head())
    raise ValueError("El DataFrame no contiene todas las características necesarias para el entrenamiento.")
else:
    X = df[features]
    y = df["es_critico"]

# Entrenamiento de modelos
linear_model = LinearRegression().fit(X, y)
decision_tree = DecisionTreeClassifier(max_depth=4, random_state=42).fit(X, y)
random_forest = RandomForestClassifier(n_estimators=50, random_state=42).fit(X, y)


def plot_linear_regression_pca(X, y, feature_label="Componente Principal"):

    # Proyecta a 1 dimensión:
    pca = PCA(n_components=1)
    X_pca = pca.fit_transform(X)
    
    # Verificamos la cantidad de registros en la proyección
    print("X_pca.shape =", X_pca.shape)  # Debería ser (50, 1)
    
    # Entrena un modelo de regresión lineal sobre la componente principal:
    model_uni = LinearRegression().fit(X_pca, y)
    
    # Predice con el modelo:
    y_pred = model_uni.predict(X_pca)
    
    # Ordenar los datos para trazar la línea suavemente:
    orden = np.argsort(X_pca.ravel())
    X_pca_sorted = X_pca.ravel()[orden]
    y_pred_sorted = y_pred[orden]
    
    # Crear el gráfico:
    fig, ax = plt.subplots(figsize=(8, 6))
    # Agregamos transparencia, borde blanco y tamaño de marcador para visualizar sobrepositions
    ax.scatter(X_pca, y, color="blue", label="Datos", alpha=0.7, edgecolors='w', s=50)
    ax.plot(X_pca_sorted, y_pred_sorted, color="red", linewidth=2, label="Línea de regresión")
    ax.set_xlabel(feature_label)
    ax.set_ylabel("Objetivo (es_crítico)")
    ax.set_title("Regresión Lineal (Proyección PCA)")
    ax.legend()
    
    # Guardar la imagen en un buffer y codificarla en base64:
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    plt.close(fig)
    
    return plot_data


def plot_decision_tree(model):
    # Nombres "bonitos" para las variables
    nice_features = ["Duración", "Mantenimiento", "Satisfacción", "Tipo Incidencia", "Tiempo Contacto"]
    class_names = ["No Crítico", "Crítico"]
    
    fig, ax = plt.subplots(figsize=(16,12))  # Aumenta el tamaño para mayor claridad
    from sklearn.tree import plot_tree
    plot_tree(model, 
              feature_names=nice_features, 
              class_names=class_names,
              filled=True, 
              rounded=True,
              fontsize=12,       # Tamaño de fuente más grande para facilitar la lectura
              impurity=False)    # Omitimos información de la impureza
    ax.set_title("Árbol de Decisión")
    
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    plt.close(fig)
    return plot_data



def plot_random_forest_tree(model, tree_index=0):
    # Extraer el árbol individual
    tree = model.estimators_[tree_index]

    # Nombres "bonitos" para las variables
    nice_features = ["Duración", "Mantenimiento", "Satisfacción", "Tipo Incidencia", "Tiempo Contacto"]
    class_names = ["No Crítico", "Crítico"]

    # Crear el gráfico
    fig, ax = plt.subplots(figsize=(16, 12))  # Tamaño del gráfico
    plot_tree(tree, 
              feature_names=nice_features, 
              class_names=class_names,
              filled=True, 
              rounded=True,
              fontsize=10)
    ax.set_title(f"Árbol {tree_index + 1} del Random Forest")

    # Guardar la imagen en un buffer y codificarla en base64
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    plt.close(fig)
    return plot_data

# Función que se llamará desde la ruta /predict_ticket
def predecir_ticket(form):
    try:
        # Extraer datos del formulario
        fecha_apertura = datetime.datetime.strptime(form.get("fecha_apertura"), "%Y-%m-%d")
        fecha_cierre = datetime.datetime.strptime(form.get("fecha_cierre"), "%Y-%m-%d")
        duracion = (fecha_cierre - fecha_apertura).days
        mantenimiento = 1 if form.get("mantenimiento") == "on" else 0
        satisfaccion = int(form.get("satisfaccion"))
        incidencia = int(form.get("incidencia"))
        contacto_total = 0  # En el nuevo ticket no hay contactos previos
        
        # Construcción del vector para la predicción
        nuevo_ticket = pd.DataFrame([[duracion, mantenimiento, satisfaccion, incidencia, contacto_total]], columns=features)
        metodo = form.get("metodo")
        
        if metodo == "lr":
            # Predicción con Regresión Lineal
            pred = linear_model.predict(nuevo_ticket)[0]
            critico = 1 if pred >= 0.5 else 0
            plot_data = plot_linear_regression_pca(X, y, feature_label="Componente Principal")
        elif metodo == "dt":
            # Predicción con Árbol de Decisión
            critico = decision_tree.predict(nuevo_ticket)[0]
            plot_data = plot_decision_tree(decision_tree)
        elif metodo == "rf":
            # Predicción con Random Forest
            critico = random_forest.predict(nuevo_ticket)[0]
            # Graficar un árbol individual del Random Forest (por ejemplo, el primero)
            plot_data = plot_random_forest_tree(random_forest, tree_index=0)
        else:
            return "Método no reconocido", ""
        
        resultado = "El ticket es CRÍTICO" if critico == 1 else "El ticket NO es crítico"
        return resultado, plot_data
    except Exception as e:
        return f"Error en la predicción: {e}", ""
