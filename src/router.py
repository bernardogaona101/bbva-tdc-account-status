import pdfplumber as pp
import sys
# identify bank

def detect_bank_and_extract(pdf_path, pdf_password):

    bank = "Unknown"

    # check if is 'plata card'

    try:
        with pp.open(pdf_path) as pdf:
            text_pag_1 = pdf.pages[1].extract_text() or ""
            # Buscamos alguna frase distintiva o el inicio de la tabla
            if "Plata Card" in text_pag_1 or "plata" in text_pag_1 or "Plata" in text_pag_1:
                bank = "PLATA"
                #return bank
    except Exception:
        pass

    if bank == "Unknown":
        try:
            with pp.open(pdf_path, password=pdf_password) as pdf:
                text_pag_1 = pdf.pages[0].extract_text() or ""
                if "BBVA" in text_pag_1 or "bbva" in text_pag_1:
                    bank = "BBVA"
        except Exception as e:
            print(f"error: {e}")


    if bank == "BBVA":
        from src.extractors.bbva import extract_bbva
        clabe, fecha, df_msi, df_regular = extract_bbva(pdf_path, pdf_password)
        return bank, clabe, fecha, df_msi, df_regular

    elif bank == "PLATA":
        from src.extractors.plata import extract_plata
        clabe, fecha, df_msi, df_regular = extract_plata(pdf_path)
        return bank, clabe, fecha, df_msi, df_regular

    else:
        print("Bank no detected")
        return None