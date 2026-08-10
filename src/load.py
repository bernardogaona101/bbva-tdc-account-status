import os
import gspread
import json
import streamlit as st
from src.config import BASE_ROOT_FILES, GOOGLE_CREDENTIALS_PATH

# save data
def save_csv(df, clabe, fecha_corte):
    # Crear la carpeta si no existe
    if not os.path.exists(BASE_ROOT_FILES):
        os.makedirs(BASE_ROOT_FILES)
        print(f"Carpeta creada en: {BASE_ROOT_FILES}")

    nombre_archivo = f"{clabe}_{fecha_corte}.csv"
    # Construir la ruta completa del archivo
    ruta_completa = os.path.join(BASE_ROOT_FILES, nombre_archivo)

    # Guardar el DataFrame
    try:
        # encoding='utf-8-sig' asegura que los acentos se lean bien en Excel
        df.to_csv(ruta_completa, index=False, encoding='utf-8-sig')
        print(f"¡Éxito! Datos guardados en: {ruta_completa}")
    except Exception as e:
        print(f"Error al guardar el CSV: {e}")

def save_to_google_sheets(df, nombre_documento="Master"):
    """
    Se conecta a Google Sheets resolviendo de forma segura formatos TOML y JSON.
    """
    print("\nIniciando conexión con Google Sheets...")
    cuenta_servicio = None

    # 1. Intentar autenticar usando los Secrets de Streamlit Cloud (Nube)
    try:
        if hasattr(st, "secrets") and "GOOGLE_CREDENTIALS" in st.secrets:
            raw_creds = st.secrets["GOOGLE_CREDENTIALS"]
            
            # Si Streamlit ya lo parseó como un diccionario (TOML) automáticamente
            if isinstance(raw_creds, dict) or hasattr(raw_creds, "keys"):
                cred_dict = {k: v for k, v in raw_creds.items()}
            # Si viene como un string JSON largo
            elif isinstance(raw_creds, str):
                cred_dict = json.loads(raw_creds)
            else:
                cred_dict = raw_creds
                
            # Limpieza crítica de saltos de línea para la llave privada de Google
            if "private_key" in cred_dict and isinstance(cred_dict["private_key"], str):
                cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
                
            cuenta_servicio = gspread.service_account_from_dict(cred_dict)
            print("Autenticación exitosa con los Secrets de la nube.")
    except Exception as e:
        print(f"Advertencia al procesar secrets de Streamlit: {e}")

    # 2. Si no estamos en la nube, intentar con el archivo local
    if cuenta_servicio is None:
        if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
            st.error(f"❌ Error: No se encontraron credenciales en '{GOOGLE_CREDENTIALS_PATH}' ni en los Secrets de la nube.")
            return False
        try:
            cuenta_servicio = gspread.service_account(filename=GOOGLE_CREDENTIALS_PATH)
        except Exception as e:
            st.error(f"❌ Error al autenticar localmente con Google: {e}")
            return False

    # 3. Proceder con el guardado
    try:
        hoja_maestra = cuenta_servicio.open(nombre_documento)
        pestana_activa = hoja_maestra.sheet1  # Selecciona la primera pestaña

        # Preparar los datos (Gspread necesita una lista de listas, no un DataFrame)
        df_limpio = df.fillna('')
        valores_a_subir = df_limpio.values.tolist()

        # Agregar los datos al final de la hoja (Append)
        pestana_activa.append_rows(valores_a_subir)
        print(f"¡Éxito! Se agregaron {len(valores_a_subir)} filas a '{nombre_documento}'.")
        return True
        
    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"❌ Error: No se encontró el Google Sheet '{nombre_documento}'. ¿Lo compartiste con el correo de servicio?")
        return False
    except Exception as e:
        st.error(f"❌ Error crítico al subir a Google Sheets: {e}")
        return False

def load_data(df, clabe, fecha_corte, google_sheet="Master", save_local=True, save_cloud=True):
    """
    Función orquestadora de carga: Guarda localmente Y en la nube.
    """
    if save_local:
        save_csv(df, clabe, fecha_corte)
    else:
        print("No saved to local")

    if save_cloud:
        df_cloud = df.copy()
        df_cloud['Fecha_Operacion'] = df_cloud['Fecha_Operacion'].astype(str)
        df_cloud['Fecha_Cargo'] = df_cloud['Fecha_Cargo'].astype(str)
        df_cloud['Fecha_Corte'] = df_cloud['Fecha_Corte'].astype(str)
        df_cloud = df_cloud.fillna("")
        save_to_google_sheets(df_cloud, google_sheet)
    else:
        print("No saved to cloud")
