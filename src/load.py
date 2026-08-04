import os
import gspread
import streamlit as st
import json
from src.config import BASE_ROOT_FILES, GOOGLE_CREDENTIALS_PATH

# save data
def save_csv(df, clabe, fecha_corte):
    # root
    # BASE_ROOT_FILES = os.path.join(os.path.expanduser("~"), "Estados_Cuenta_Analizados")
    
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
    Se conecta a Google Sheets usando el archivo JSON de credenciales
    y agrega las nuevas filas del DataFrame al final del documento.
    """
    print("\nIniciando conexión con Google Sheets...")
    
    # Definir la ruta de tus credenciales
       
    try:
        if "GOOGLE_CREDENTIALS" in st.secrets:
            # Si estamos en Streamlit Cloud, cargamos el JSON desde los secretos
            cred_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
            cuenta_servicio = gspread.service_account_from_dict(cred_dict)
        else:
            if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
                # Si estamos en tu computadora local, usamos el archivo fisico
                print("No se encontraron credenciales")
                return
            cuenta_servicio = gspread.service_account(filename=GOOGLE_CREDENTIALS_PATH)
        
        # Abrir el documento por su nombre (el que compartiste con el robot)
        hoja_maestra = cuenta_servicio.open(nombre_documento)
        pestana_activa = hoja_maestra.sheet1 # Selecciona la primera pestaña
        
        # Preparar los datos (Gspread necesita una lista de listas, no un DataFrame)
        # Convertimos NaN a strings vacíos
        df_limpio = df.fillna('') 
        # Convertimos los datos a una lista de listas
        valores_a_subir = df_limpio.values.tolist()
        
        # 5. Agregar los datos al final de la hoja (Append)
        # Esto es clave para Looker Studio: ir apilando meses sin borrar lo anterior
        pestana_activa.append_rows(valores_a_subir)
        
        print(f"¡Éxito! Se agregaron {len(valores_a_subir)} filas a '{nombre_documento}' en la nube.")
        
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Error: No se encontró el Google Sheet llamado '{nombre_documento}'. ¿Lo compartiste con el correo de servicio?")
    except Exception as e:
        print(f"Error al subir a Google Sheets: {e}")

def load_data(df, clabe,fecha_corte, google_sheet="Master", save_local=True, save_cloud=True):
    """
    Función orquestadora de carga: Guarda localmente Y en la nube.
    Esta es la función que deberás llamar desde main.py
    """
    if save_local:
        #   Guardado Local
        save_csv(df, clabe,fecha_corte)
    else:
        print("No saved to local")

    if save_cloud:
        #   Guardado en Nube
        df_cloud = df.copy()
        df_cloud['Fecha_Operacion'] = df_cloud['Fecha_Operacion'].astype(str)
        df_cloud['Fecha_Cargo'] = df_cloud['Fecha_Cargo'].astype(str)
        df_cloud['Fecha_Corte'] = df_cloud['Fecha_Corte'].astype(str)
        df_cloud = df_cloud.fillna("")
        save_to_google_sheets(df_cloud, google_sheet)
    else:
        print("No saved to cloud")