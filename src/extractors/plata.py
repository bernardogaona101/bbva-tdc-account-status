import pdfplumber as pp
import re
import pandas as pd
from src.utils import clean_global_date

# function to obtain metadata
def get_metadata_pdf(pages_text):
    clabe = "CLABE_Unknown"
    fecha_corte = "Date_Unknown"
    
    # print("Analizing metadata...")

    for text in pages_text[:2]:
        match_clabe = re.search(r'Número de cuenta:[:\s]*(\d{10})', text)
        if match_clabe and clabe == "CLABE_Unknown":
            clabe = match_clabe.group(1)
            # print(f"Client detected (CLABE): {clabe}")
        match_fecha = re.search(r'Fecha de corte[:\s]*(\d{2}-[a-z]{3}-\d{4})', text, re.IGNORECASE)

        if match_fecha and fecha_corte == "Date_Unknown":
            fecha_corte = match_fecha.group(1)
            fecha_corte = clean_global_date(fecha_corte)
            # if fecha_corte:
            #     print(f"Fecha de corte: {fecha_corte}")
        
        if clabe != "CLABE_Unknown" and fecha_corte != "Date_Unknown":
            break
    return clabe, fecha_corte

# function to extract msi records
def extract_msi_rec(pages_text):
    # keywords to delimit search field
    start_key = 'Compras y cargos diferidos a meses'
    end_key = 'Cargos, abonos y compras regulares'
    

    msi_record_pattern = re.compile(
        r'(\d{2}-[a-z]{3}-\d{4})\s+'        # Fecha operación
        r'(.*?)\s+'                         # Descripción
        r'\$([\d,]+\.\d{2})\s+'             # Monto original
        r'\$([\d,]+\.\d{2})\s+'             # Saldo pendiente
        r'\$([\d,]+\.\d{2})\s+'             # Pago requerido
        r'(\d+\s+de\s+\d+)\s+'              # Num. de pago
        r'([\d\.]+%)',                      # Tasa de interes
        re.DOTALL | re.IGNORECASE
    )
    
    records_found = []
    
    all_text = "\n".join(pages_text)
            
    # delimit area
    clean_block = ""
    in_table = False
    
    for line in all_text.split('\n'):
        clean_line = line.strip()
        
        # trigger delimiter
        if start_key in clean_line and not in_table:
            in_table = True
            continue # skpi title line
            
        # end delimiter
        if end_key in clean_line and in_table:
            in_table = False
            break 
            
        # filter by clean not necesary text
        if in_table:
            if not clean_line.startswith("Notas: Ver notas") and \
               not clean_line.startswith("Número de cuenta:") and \
               start_key not in clean_line and \
               "Tarjeta titular:" not in clean_line and \
               "Tasa de Fecha de la" not in clean_line and \
               "interés operación" not in clean_line:
                
                clean_block += clean_line + "\n"

    # look for the records
    for match in msi_record_pattern.finditer(clean_block):
        date = match.group(1)
        
        # clean description
        description = match.group(2).replace('\n', ' ').strip()
        description = re.sub(r'\s+', ' ', description) 
        
        # clean amounts
        original_amount = match.group(3).replace(',', '') 
        pending_balance = match.group(4).replace(',', '')
        payment_required = match.group(5).replace(',', '')
        
        num_pay = match.group(6)
        interest_rate = match.group(7)
        
        records_found.append({
            'Fecha': date,
            'Descripcion': description,
            'Monto_Original': float(original_amount),
            'Saldo_Pendiente': float(pending_balance),
            'Pago_Mensual': float(payment_required),
            'Num_Pago': num_pay,
            'Tasa_Interes': interest_rate
        })
            
    if records_found:
        df_msi = pd.DataFrame(records_found)
        return df_msi
    else:
        # print("No msi records detected.")
        return None

# function to extract regular records
def extract_regular_rec(pages_text):
    # keywords to delimit search field
    start_key = 'abonos y compras regulares (no a meses)'
    end_key = 'Total cargos'
    
    pattern_plata = re.compile(
        r'(\d{2}-[a-z]{3}-\d{4})\s+'     # 1. Fecha operación
        r'(\d{2}-[a-z]{3}-\d{4})\s+'     # 2. Fecha cargo
        r'(\d{6}[X\*]+\d{4}|\d{4})\s+'         # 3. Tarjeta
        r'(.*?)\s+'                      # 4. Descripción
        r'([+\-−]\s*[\d,]+\.\d{2})\s+'     # 5. Monto original
        r'([A-Z]{3})\s+'                 # 6. Moneda
        r'([\d\.]+)\s+'                  # 7. Tipo de cambio
        r'([+\-−]\s*\$[\d,]+\.\d{2})',     # 8. Monto MXN final
        re.IGNORECASE | re.DOTALL
    )
    
    records_found = []
    
    all_text = "\n".join(pages_text)
            
    # print(all_text)

    clean_block = ""
    in_table = False
    
    # start to read pdf
    for line in all_text.split('\n'):
        clean_line = line.strip()
        
        # trigger delimiter if we found start key
        if start_key in clean_line and not in_table:
            in_table = True
            continue # skip to the next line to not include title
            
        # end delimiter if we found end key
        if end_key in clean_line and in_table:
            in_table = False
            break 
            
        # collect text
        if in_table:
            # clean and discard text
            if not clean_line.startswith("Notas: Ver notas") and \
               not clean_line.startswith("Número de cuenta:") and \
               start_key not in clean_line and \
               "Fecha de la Fecha de cargo" not in clean_line and \
               "operación" not in clean_line:
                
                clean_block += clean_line + "\n"

    # process clean block
    for match in pattern_plata.finditer(clean_block):
        fecha_operacion = match.group(1)
        fecha_cargo = match.group(2)
        descripcion = match.group(4).replace('\n', ' ').strip()
        descripcion = re.sub(r'\s+', ' ', descripcion)
        
        # Tomamos el grupo 8 (Monto MXN final) limpiando símbolos y espacios
        raw_amount = match.group(8).replace(' ', '').replace('$', '').replace(',', '').replace('−', '-')
        amount = float(raw_amount)
        
        records_found.append({
            'Fecha_Operacion': fecha_operacion,
            'Fecha_Cargo': fecha_cargo,
            'Descripcion': descripcion,
            'Monto': amount,
            'Tipo_Movimiento': 'REGULAR'
        })
            
    if records_found:
        return pd.DataFrame(records_found)
    else:
        # print("Regular records were not detected.")
        return None

# apply the function into one
def extract_plata(pages_text):
    clabe, fecha = get_metadata_pdf(pages_text)
    df_msi = extract_msi_rec(pages_text)
    df_regular = extract_regular_rec(pages_text)
    return clabe, fecha, df_msi, df_regular
