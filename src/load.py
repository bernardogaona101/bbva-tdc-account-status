import os

# save data
def save_csv(df, nombre_archivo='consolidate_movements.csv'):
    # root
    BASE_ROOT_FILES = os.path.join(os.path.expanduser("~"), "Estados_Cuenta_Analizados")
    
    # Crear la carpeta si no existe
    if not os.path.exists(BASE_ROOT_FILES):
        os.makedirs(BASE_ROOT_FILES)
        print(f"Carpeta creada en: {BASE_ROOT_FILES}")
        
    # 3. Construir la ruta completa del archivo
    ruta_completa = os.path.join(BASE_ROOT_FILES, nombre_archivo)
    
    # 4. Guardar el DataFrame
    try:
        # index=False evita que Pandas guarde la columna de números de fila
        # encoding='utf-8-sig' asegura que los acentos se lean bien en Excel
        df.to_csv(ruta_completa, index=False, encoding='utf-8-sig')
        print(f"¡Éxito! Datos guardados en: {ruta_completa}")
    except Exception as e:
        print(f"Error al guardar el CSV: {e}")