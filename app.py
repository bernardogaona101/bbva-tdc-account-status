import streamlit as st
import os
from dotenv import load_dotenv

# Importamos tus módulos de la carpeta src/
from src.router import detect_bank_and_extract
from src.transform import consolidate_movements, clean_and_categorize
from src.load import load_data
from src.config import DEFAULT_GOOGLE_SHEET_NAME

# Cargar contraseña oculta desde el archivo .env

load_dotenv()
try:
    # Intenta leerlo de la nube (Streamlit Cloud)
    env_password = st.secrets["RFC_BBVA"]
except:
    # Si falla, intenta leerlo de tu computadora local (.env)
    env_password = os.getenv("RFC_BBVA", "")

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Analizador Financiero", page_icon="📊", layout="centered")

st.title("📊 Analizador de Estados de Cuenta")
st.write("Sube tu estado de cuenta en formato PDF para extraer y analizar tus movimientos de BBVA o Plata Card.")

# 2. INTERFAZ DE USUARIO (Reemplaza a tkinter)
# Subida de archivo
pdf_file = st.file_uploader("Selecciona tu PDF", type=["pdf"])

# Contraseña (con valor por defecto del .env)
user_password = st.text_input("Contraseña (RFC) - Déjalo en blanco si No se necesita:", 
                              type="password")

# Preferencias de guardado
st.subheader("Opciones de Guardado")
col1, col2 = st.columns(2)
with col1:
    save_local = st.checkbox("Guardar copia local (CSV)", value=False)
with col2:
    save_cloud = st.checkbox("Subir a Nube", value=False)


# 3. ORQUESTADOR ETL (Se ejecuta al presionar el botón)
if st.button("Procesar Estado de Cuenta", type="primary"):
    if pdf_file is None:
        st.warning("⚠️ Por favor, sube un archivo PDF primero.")
    else:
        with st.spinner("Analizando y extrayendo datos..."):


            password_final = user_password if user_password != "" else env_password
            # --- FASE 1: EXTRACT ---
            # Nota: Streamlit entrega un objeto en memoria, pdfplumber lo lee sin problema
            bank,clabe, fecha, df_msi, df_regular = detect_bank_and_extract(pdf_file, password_final)
            
            if df_regular is not None or df_msi is not None:
                # --- FASE 2: TRANSFORM ---
                df_raw = consolidate_movements(df_msi, df_regular)
                # categorize and clean
                df_clean = clean_and_categorize(bank,df_raw, fecha)
            
                # --- FASE 3: LOAD ---
                cuenta_autorizada = ""
                try:
                    cuenta_autorizada = st.secrets.get("MI_CLABE", [])
                except:
                    pass
                if save_cloud and len(cuenta_autorizada) > 0:
                    if clabe not in cuenta_autorizada:
                        st.warning("🛡️ Por seguridad, la subida a Google Sheets ha sido desactivada porque el PDF no pertenece a la cuenta administradora. Solo podrás descargar el CSV.")
                        save_cloud = False
                if not save_local and not save_cloud:
                    st.info("ℹ️ Datos extraídos correctamente, pero elegiste no guardarlos.")
                else:
                    load_data(
                        df_clean,
                        clabe,
                        fecha,
                        google_sheet=DEFAULT_GOOGLE_SHEET_NAME,
                        save_local=save_local,
                        save_cloud=save_cloud
                    )
                    st.success("✅ ¡Proceso completado exitosamente!")               
                # Mostrar las tablas limpias en la pantalla
                if not df_clean.empty:
                    st.subheader("Movimientos del Periodo")
                    st.dataframe(df_clean)
                    # Convertimos el DataFrame a CSV en la memoria
                    csv = df_clean.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                    
                    st.download_button(
                        label="⬇️ Descargar copia en Excel (CSV)",
                        data=csv,
                        file_name=f"{bank}_{clabe}_{fecha}_movimientos.csv",
                        mime="text/csv"
                    )
            else:
                st.error("❌ No se detectó un banco válido o no se encontraron movimientos.")
