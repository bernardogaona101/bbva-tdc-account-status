# main.py
'''
-   -   -   -   -   -   -   Funcion del programa    -   -   -   -   -   -   -
1.  Pedir el file: obtener el archivo para ver de que banco es = router-> detect_bank()
2.  Al ver el banco

'''

# import function from modules
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import sys
from src.router import detect_bank_and_extract
from src.transform import consolidate_movements, clean_and_categorize
from src.load import load_data
from dotenv import load_dotenv

def get_user_data():

        load_dotenv()
        # configure dialogue card
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
    
        # Select the pdf_path and enter password
        messagebox.showinfo("Automatic Analizer", "Select PDF to analize")
        pdf_path = filedialog.askopenfilename(title="Select PDF", filetypes=[("PDF", "*.pdf")])
        if not pdf_path: sys.exit()
    
        # PDF_PASSWORD = os.getenv("RFC_BBVA")
        PDF_PASSWORD = None

        if not PDF_PASSWORD:
             PDF_PASSWORD = simpledialog.askstring("Security", "Password (RFC sin homoclave)\n dejar vacio si no requiere:", show='*')

        return pdf_path, PDF_PASSWORD

def get_save_preferences():
    """Abre ventanas emergentes para preguntar dónde guardar los datos."""
    # messagebox.askyesno devuelve True si el usuario dice "Si", y False si dice "No"
    save_local = messagebox.askyesno("Guardado Local", "¿Deseas guardar una copia en formato CSV en tu computadora?")
    save_cloud = messagebox.askyesno("Guardado en la Nube", "¿Deseas subir los datos a la nube (Drive)?")
    
    return save_local, save_cloud

def execute_etl():
    # input user
    pdf_path, PDF_PASSWORD = get_user_data()    
    # Extract using router
    print("\n[1/3] extract data...")
    clabe, fecha, df_msi, df_regular = detect_bank_and_extract(pdf_path, PDF_PASSWORD)
    
    # TRANSFORM
    print("\n[2/3] transform and clean data...")

    # concat both tables
    df_raw = consolidate_movements(df_msi, df_regular)
    
    # categorize and clean
    df_clean = clean_and_categorize(df_raw, fecha)
    
    # LOAD
    print("\n[3/3] Load data...")
    # fecha de corte to file
    # file_name = f'movimientos_bbva_{fecha}.csv'
    save_local, save_cloud = get_save_preferences()

    if not save_local and not save_cloud:
        print("\nProceso finalizado: Los datos fueron extraídos pero no se guardaron por elección del usuario.")
        return
    
    load_data(
         df_clean,
         clabe,
         fecha,
         google_sheet="Master",
         save_local=save_local,
         save_cloud=save_cloud
    )
    
    print("\n--- ETL PROCESS COMPLETE ---")

# this line ensures that the code only runs if you execute this file directly
if __name__ == "__main__":
    execute_etl()