'''
-   -   -   -   -   -   -   Funcion del programa    -   -   -   -   -   -   -
1.  Pedir el file: obtener el archivo para ver de que banco es = router-> detect_bank()
2.  Al ver el banco

'''
# import function from modules
from src.gui import get_user_data, get_save_preferences
from src.router import detect_bank_and_extract
from src.transform import consolidate_movements, clean_and_categorize
from src.load import load_data
from src.config import DEFAULT_GOOGLE_SHEET_NAME

def execute_etl():
    # get the input to start working: file_path and password (if necessary)
    pdf_path, PDF_PASSWORD = get_user_data()    

    # Extract using router
    print("\n[1/3] extract data...")
    bank,clabe, fecha, df_msi, df_regular = detect_bank_and_extract(pdf_path, PDF_PASSWORD)
    
    # TRANSFORM
    print("\n[2/3] transform and clean data...")

    # concat both tables
    df_raw = consolidate_movements(df_msi, df_regular)
    
    # categorize and clean
    df_clean = clean_and_categorize(bank,df_raw, fecha)
    
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
         google_sheet=DEFAULT_GOOGLE_SHEET_NAME,
         save_local=save_local,
         save_cloud=save_cloud
    )
    
    print("\n--- ETL PROCESS COMPLETE ---")

# this line ensures that the code only runs if you execute this file directly
if __name__ == "__main__":
    execute_etl()