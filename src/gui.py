import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import sys
import os
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
    
        PDF_PASSWORD = os.getenv("RFC_BBVA")
        # PDF_PASSWORD = None

        if not PDF_PASSWORD:
             PDF_PASSWORD = simpledialog.askstring("Security", "Password (RFC sin homoclave)\n dejar vacio si no requiere:", show='*')

        return pdf_path, PDF_PASSWORD

def get_save_preferences():
    """Abre ventanas emergentes para preguntar dónde guardar los datos."""
    # messagebox.askyesno devuelve True si el usuario dice "Si", y False si dice "No"
    save_local = messagebox.askyesno("Guardado Local", "¿Deseas guardar una copia en formato CSV en tu computadora?")
    save_cloud = messagebox.askyesno("Guardado en la Nube", "¿Deseas subir los datos a la nube (Drive)?")
    
    return save_local, save_cloud