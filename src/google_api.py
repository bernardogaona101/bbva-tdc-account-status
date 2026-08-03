import gspread
import os
import streamlit as st
import json

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
            # Si estamos en tu computadora local, usamos el archivo fisico
            from src.config import GOOGLE_CREDENTIALS_PATH
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
