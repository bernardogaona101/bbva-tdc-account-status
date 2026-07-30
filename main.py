# main.py

# import function from modules
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import sys
from src.extract import extract_msi_rec, extract_regular_rec, get_metadata_pdf
from src.transform import consolidate_movements, clean_and_categorize
from src.load import save_csv
from dotenv import load_dotenv

load_dotenv()
def get_user_data():
        # configure dialogue card
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
    
        # Select the pdf_path and enter password
        messagebox.showinfo("Automatic Analizer", "Select PDF to analize")
        pdf_path = filedialog.askopenfilename(title="Select PDF", filetypes=[("PDF", "*.pdf")])
        if not pdf_path: sys.exit()
    
        PDF_PASSWORD = os.getenv("RFC_BBVA")
        if not PDF_PASSWORD:
             PDF_PASSWORD = simpledialog.askstring("Security", "Password (RFC sin homoclave):", show='*')
             if PDF_PASSWORD is None: sys.exit()

        return pdf_path, PDF_PASSWORD

def execute_etl():
    # input user
    pdf_path, PDF_PASSWORD = get_user_data()    
    # EXTRACT
    print("\n[1/3] extract data...")
    clabe, fecha, anio = get_metadata_pdf(pdf_path, PDF_PASSWORD)
    df_msi = extract_msi_rec(pdf_path, PDF_PASSWORD)
    df_regular = extract_regular_rec(pdf_path, PDF_PASSWORD)
    
    # TRANSFORM
    print("\n[2/3] transform and clean data...")

    # concat both tables
    df_raw = consolidate_movements(df_msi, df_regular)
    
    # categorize and clean
    df_clean = clean_and_categorize(df_raw)
    
    # LOAD
    print("\n[3/3] Load data...")
    # fecha de corte to file
    # file_name = f'movimientos_bbva_{fecha}.csv'
    save_csv(df_clean)
    
    print("\n--- ETL PROCESS COMPLETE ---")

# this line ensures that the code only runs if you execute this file directly
if __name__ == "__main__":
    execute_etl()