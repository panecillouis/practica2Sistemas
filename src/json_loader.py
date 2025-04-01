import json
#se carga los datos del archivo json
def cargar_datos_json():
    with open('datos.json', 'r', encoding="utf-8") as file:
        data = json.load(file)
    return data
