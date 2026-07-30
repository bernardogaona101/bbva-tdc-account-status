from datetime import datetime
import pandas as pd
from src.utils import clean_global_date

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
        df_msi_final['Tipo_Movimiento'] = 'MSI'
        
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
def clean_and_categorize(df_total):
    # cleaning  dates
    df_total['Fecha_Operacion'] = df_total['Fecha_Operacion'].apply(clean_global_date)
    df_total['Fecha_Cargo'] = df_total['Fecha_Cargo'].apply(clean_global_date)

    df_total['Fecha_Operacion'] = pd.to_datetime(df_total['Fecha_Operacion'], format='%Y-%m-%d', errors='coerce')
    df_total['Fecha_Cargo'] = pd.to_datetime(df_total['Fecha_Cargo'], format='%Y-%m-%d', errors='coerce')

    df_total = df_total.sort_values(by='Fecha_Operacion').reset_index(drop=True)

    # get only positive values (no payments)
    df_total = df_total.loc[df_total['Monto']>0]

    # drop duplicates of msi records
    drop_condition = (
        (df_total['Tipo_Movimiento'] == 'REGULAR') & 
        (df_total['Descripcion'].str.contains(r'\d{1,2}\s+DE+\s+\d{1,2}\b', regex=True, case=False, na=False))
    )
    df_total = df_total[~drop_condition]

    # categorize MSI, MSI TOTAL & REGULAR
    msi_total_pattern = r'A \d{2} MESES|A\s+MESES|\d{1,2}\s+MESES\s+S/I|A \d{1,2}\s+MSI'

    is_total_charge = (
        (df_total['Tipo_Movimiento'] == 'REGULAR') &
        (df_total['Descripcion'].str.contains(msi_total_pattern, regex=True, case=False, na=False))
    )

    df_total.loc[is_total_charge, 'Tipo_Movimiento'] = 'Compra Total MSI'

    return df_total
