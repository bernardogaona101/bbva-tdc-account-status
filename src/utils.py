from datetime import datetime
import os
from dotenv import load_dotenv
import json
import streamlit as st

# Clean dates format
Months = {
    'ene': '01',
    'feb': '02',
    'mar': '03',
    'abr': '04',
    'may': '05',
    'jun': '06',
    'jul': '07',
    'ago': '08',
    'sep': '09',
    'oct': '10',
    'nov': '11',
    'dic': '12'
}

def clean_global_date(date_str):
    # validate if there's a date:
    if not date_str:
        return None
    
    try:
        p = str(date_str).strip().split('-')

        # get the actual year
        current_year = datetime.now().year

        if len(p) == 3: return f"{p[2]}-{Months.get(p[1].lower(),'00')}-{p[0]}"
        # if len(p) == 2: return f"{current_year}-{Months.get(p[1].lower(),'00')}-{p[0]}"

        return None
    
    except Exception as e:
        print(f"Error with date: '{date_str}': {e}")

        return None

load_dotenv()
def obtener_mapeo_propietarios() -> dict:
    try:
        # st.secrets siempre tiene el atributo, pero buscar la clave "in st.secrets"
        # lanzará un error si el archivo .toml no existe en local.
        # Al envolverlo en try-except, si falla, saltará directo al bloque de .env.
        if hasattr(st, "secrets") and "MAPEO_PROPIETARIOS" in st.secrets:
            secret_val = st.secrets["MAPEO_PROPIETARIOS"]
            
            # Si Streamlit (en la nube) ya lo parseó como diccionario/TOML automáticamente
            if isinstance(secret_val, dict) or hasattr(secret_val, "keys"):
                return {str(k).strip(): str(v).strip() for k, v in secret_val.items()}
            
            # Por si acaso se configuró como un string JSON en los secretos
            elif isinstance(secret_val, str):
                try:
                    return json.loads(secret_val)
                except Exception:
                    pass
    except Exception:
        # Ignoramos el error si no hay archivo de secretos de Streamlit local (estamos usando .env)
        pass

    # 2. Si no está en la nube o falló/no existe el archivo de secretos, buscar en el .env local
    env_val = os.getenv("MAPEO_PROPIETARIOS", "")
    if env_val:
        try:
            return json.loads(env_val)
        except Exception as e:
            print(f"Error al parsear MAPEO_PROPIETARIOS desde el .env: {e}")

    return {}