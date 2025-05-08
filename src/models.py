import json
import unicodedata
import bcrypt
from flask_login import UserMixin

class Usuario(UserMixin):
    def __init__(self, id, username, password, nivel, fecha_contrato, avatar):
        self.id = id
        self.username = username
        self.password = password
        self.nivel = nivel
        self.fecha_contrato = fecha_contrato
        self.avatar = avatar  

# Ruta del archivo JSON para persistir los usuarios registrados
RUTA_USUARIOS_REGISTRADOS = 'usuarios_registrados.json'

contraseñas = {}

# Leer usuarios registrados desde el archivo JSON
def cargar_usuarios_registrados():
    try:
        with open(RUTA_USUARIOS_REGISTRADOS, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}  # Si el archivo no existe, retorna un diccionario vacío

# Guardar usuarios registrados en el archivo JSON
def guardar_usuarios_registrados(usuarios):
    with open(RUTA_USUARIOS_REGISTRADOS, 'w', encoding='utf-8') as file:
        json.dump(usuarios, file, indent=4, ensure_ascii=False)

# Cifrar una contraseña
def cifrar_contraseña(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Verificar una contraseña
def verificar_contraseña(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def normalizar_cadena(cadena):
    return ''.join(
        c for c in unicodedata.normalize('NFD', cadena)
        if unicodedata.category(c) != 'Mn'
    ).lower()

# Cargar empleados desde el JSON
def cargar_empleados():
    with open('datos.json', 'r', encoding='utf-8') as file:  # Especificar codificación UTF-8
        data = json.load(file)
        empleados = data.get("empleados", [])
        return empleados

# Crear usuarios a partir de empleados
def cargar_usuarios():
    empleados = cargar_empleados()
    usuarios_registrados = cargar_usuarios_registrados()
    usuarios = {
        emp["id_emp"]: Usuario(
            id=emp["id_emp"],
            username=emp["nombre"],
            password=usuarios_registrados.get(emp["id_emp"], {}).get("password"),
            nivel=emp["nivel"],
            fecha_contrato=emp["fecha_contrato"],
            avatar=usuarios_registrados.get(emp["id_emp"], {}).get("avatar", "https://globalsymbols.com/uploads/production/image/imagefile/17674/17_17675_41ec0485-a97d-467f-80e3-9eb573ded0da.png")  # Avatar predeterminado si no está definido
        )
        for emp in empleados
    }
    return usuarios

usuarios = cargar_usuarios()

def obtener_usuario_por_nombre(username):
    username_normalizado = normalizar_cadena(username)
    for usuario in usuarios.values():
        if normalizar_cadena(usuario.username) == username_normalizado:
            return usuario
    return None