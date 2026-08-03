import os

# --- RUTAS LOCALES ---
# Detecta automáticamente la carpeta raíz del usuario (ej. C:/Users/tu_usuario)
HOME_DIR = os.path.expanduser("~")

# Carpeta principal donde se guardarán todos los CSV extraídos
BASE_ROOT_FILES = os.path.join(HOME_DIR, "Estados_Cuenta_Analizados")


# --- RUTAS Y VARIABLES DE LA NUBE ---
# Nombre del archivo JSON que contiene tus credenciales de Google
GOOGLE_CREDENTIALS_PATH = 'google_credentials.json'

# Nombre de tu archivo principal en Google Sheets
DEFAULT_GOOGLE_SHEET_NAME = "Master"