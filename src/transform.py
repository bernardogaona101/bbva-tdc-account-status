from datetime import datetime
import pandas as pd
from src.utils import clean_global_date
import json
import os
from src.utils import obtener_mapeo_propietarios
# asignar una catergoria

def cargar_categorias():
    with open('categories.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def assign_category(desc):
    categorias_dict = cargar_categorias()
    desc = str(desc).lower()
    
    for categoria, palabras_clave in categorias_dict.items():
        if any(keyword in desc for keyword in palabras_clave):
            return categoria
    return 'Otros'

def obtener_propietario(clabe_o_cuenta: str) -> str:
    mapeo = obtener_mapeo_propietarios()
    clabe_buscada = str(clabe_o_cuenta).strip()
    
    # Iteramos sobre el diccionario: propietario (llave) -> cuentas (lista de valores)
    for propietario, cuentas in mapeo.items():
        if isinstance(cuentas, list):
            # Limpiamos espacios por seguridad en la lista de cuentas
            cuentas_limpias = [str(c).strip() for c in cuentas]
            if clabe_buscada in cuentas_limpias:
                return propietario
        # Respaldo por si se configuró una sola cuenta como texto plano en lugar de lista
        elif str(cuentas).strip() == clabe_buscada:
            return propietario
            
    return "Desconocido"

# function to concat tables
def consolidate_movements(df_msi, df_regular):
    # prepare MSI for union
    if df_msi is not None and not df_msi.empty:
        df_msi_final = df_msi.copy()

        df_msi_final['Monto'] = df_msi_final['Pago_Mensual']
        
        # use 'Fecha for both dates to match Regular
        df_msi_final['Fecha_Operacion'] = df_msi_final['Fecha']
        df_msi_final['Fecha_Cargo'] = df_msi_final['Fecha']
        
        # add label to descriptions to identify MSI
        df_msi_final['Descripcion'] = df_msi_final['Descripcion'] + " [MSI " + df_msi_final['Num_Pago'] + "]"
        
        # label type
        df_msi_final['Tipo_Movimiento'] = 'MSI Actual'
        
        # select columns
        df_msi_final = df_msi_final[['Fecha_Operacion', 'Fecha_Cargo', 'Descripcion', 'Monto', 'Tipo_Movimiento']]
    else:
        # create empty df if there's no records
        df_msi_final = pd.DataFrame(columns=['Fecha_Operacion', 'Fecha_Cargo', 'Descripcion', 'Monto', 'Tipo_Movimiento'])

    # prepare regular for union
    if df_regular is not None and not df_regular.empty:
        df_regulares_final = df_regular.copy()
        
        # label type
        df_regulares_final['Tipo_Movimiento'] = 'REGULAR'
        
        # select columns
        df_regulares_final = df_regulares_final[['Fecha_Operacion', 'Fecha_Cargo', 'Descripcion', 'Monto', 'Tipo_Movimiento']]
    else:
        df_regulares_final = pd.DataFrame(columns=['Fecha_Operacion', 'Fecha_Cargo', 'Descripcion', 'Monto', 'Tipo_Movimiento'])

    # Concat
    df_consolidate = pd.concat([df_msi_final, df_regulares_final], ignore_index=True)
    
    return df_consolidate

# function to clean and validate records
def clean_and_categorize(bank, df_total, fecha_corte,clabe):
    # cleaning  dates
    df_total['Fecha_Operacion'] = df_total['Fecha_Operacion'].apply(clean_global_date)
    df_total['Fecha_Cargo'] = df_total['Fecha_Cargo'].apply(clean_global_date)

    df_total['Fecha_Operacion'] = pd.to_datetime(df_total['Fecha_Operacion'], format='%Y-%m-%d', errors='coerce')
    df_total['Fecha_Cargo'] = pd.to_datetime(df_total['Fecha_Cargo'], format='%Y-%m-%d', errors='coerce')

    df_total = df_total.sort_values(by='Fecha_Operacion').reset_index(drop=True)

    # get only positive values (no payments)
    df_total = df_total.loc[df_total['Monto']>0]

    # drop duplicates of msi records
    msi_condition = (
        (df_total['Tipo_Movimiento'] == 'REGULAR') & 
        (df_total['Descripcion'].str.contains(r'\d{1,2}\s+DE\s+\d{1,2}\b', regex=True, case=False, na=False))
    )
    # df_total = df_total[~msi_condition]
    df_total.loc[msi_condition,'Tipo_Movimiento'] = 'MSI'

    # categorize MSI, MSI TOTAL & REGULAR
    msi_total_pattern = r'A \d{2} MESES|A\s+MESES|\d{1,2}\s+MESES\s+S/I|A \d{1,2}\s+MSI'

    is_total_charge = (
        (df_total['Tipo_Movimiento'] == 'REGULAR') &
        (df_total['Descripcion'].str.contains(msi_total_pattern, regex=True, case=False, na=False))
    )

    df_total.loc[is_total_charge, 'Tipo_Movimiento'] = 'Compra Total MSI'

    df_total['Fecha_Corte'] = fecha_corte
    
    df_total['bank'] = bank

    df_total['Categoria'] = df_total['Descripcion'].apply(assign_category)

    df_total['Propietario'] = obtener_propietario(clabe)

    return df_total
