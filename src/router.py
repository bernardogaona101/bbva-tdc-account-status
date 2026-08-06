import pdfplumber as pp
from src.extractors.bbva import extract_bbva
from src.extractors.plata import extract_plata
# extractors

Extractors = {
    'BBVA': extract_bbva,
    'PLATA': extract_plata
}

# extract pdf text
def extract_pdf_text(pdf_path, pdf_password):
    pages_text = []
    
    # Intentamos primero sin contraseña
    try:
        with pp.open(pdf_path) as pdf:
            pages_text = [page.extract_text() or "" for page in pdf.pages]
            return pages_text
    except:
        pass
        
    # Si falla, intentamos con contraseña
    try:
        with pp.open(pdf_path, password=pdf_password) as pdf:
            pages_text = [page.extract_text() or "" for page in pdf.pages]
            return pages_text
    except Exception as e:
        print(f"Error al abrir el PDF: {e}")
        return None

# identify bank
def detect_bank_and_extract(pdf_path, pdf_password):

    pages_text = extract_pdf_text(pdf_path, pdf_password)
    
    if not pages_text:
        return None, None, None, None, None

    bank = "Unknown"

    # check if is 'plata card'
    text_pag_1 = pages_text[1].lower()
    try:
        if "plata Card" in text_pag_1 or "plata" in text_pag_1:
            bank = "PLATA"
                #return bank
    except Exception:
        pass

    if bank == "Unknown":
        try:              
            text_pag_1 = pages_text[0].lower()
            if "bbva" in text_pag_1:
                bank = "BBVA"
        except Exception as e:
            print(f"error: {e}")

    if bank in Extractors:
        return bank,*Extractors[bank](pages_text)
    else:
        import logging
        logging.error(f"Bank no detected.")
        return None, None, None, None, None 
