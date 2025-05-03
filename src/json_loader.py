import json
#se carga los datos del archivo json
def cargar_datos_json():
    with open('datos.json', 'r', encoding="utf-8") as file:
        data1 = json.load(file)
    with open('data_clasified.json', 'r', encoding="utf-8") as file:
        data2 = json.load(file)
    # Combinar ambos diccionarios
    data = {**data1, **data2}
    return data
