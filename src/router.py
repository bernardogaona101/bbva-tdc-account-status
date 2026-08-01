import pdfplumber as pp
# identify bank

def detect_bank(pdf_path, password):

    bank = "Unknown"

    # check if is 'plata card'

    try:
        with pp.open(pdf_path) as pdf:
            text_pag_1 = pdf.pages[0].extract_text() or ""
            # Buscamos alguna frase distintiva o el inicio de la tabla
            if "Plata" in text_pag_1:
                bank = "PLATA"
                return bank
    except Exception as e:
        # Si da error porque está encriptado, pasamos al Intento 2
        pass

    try:
        with pp.open(pdf_path, password=password) as pdf:
            text_pag_1 = pdf.pages[0].extract_text() or ""
            if "BBVA" in text_pag_1:
                bank = "BBVA"
                return bank
    except Exception as e:
        pass
        
    return bank