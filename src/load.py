import os
from src.google_api import save_to_google_sheets
# save data
def save_csv(df, clabe, fecha_corte):
    # root
    BASE_ROOT_FILES = os.path.join(os.path.expanduser("~"), "Estados_Cuenta_Analizados")
    
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

def load_data(df, clabe,fecha_corte, google_sheet="Master"):
    """
    Función orquestadora de carga: Guarda localmente Y en la nube.
    Esta es la función que deberás llamar desde main.py
    """
    #   Guardado Local
    save_csv(df, clabe,fecha_corte)

    #   Guardado en Nube
    df_cloud = df.copy()
    df_cloud['Fecha_Operacion'] = df_cloud['Fecha_Operacion'].astype(str)
    df_cloud['Fecha_Cargo'] = df_cloud['Fecha_Cargo'].astype(str)
    df_cloud['Fecha_Corte'] = df_cloud['Fecha_Corte'].astype(str)
    df_cloud = df_cloud.fillna("")
    
   
    save_to_google_sheets(df_cloud, google_sheet)