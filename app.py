import streamlit as st
import os
from dotenv import load_dotenv

# Importamos módulos
from src.router import detect_bank_and_extract
from src.transform import consolidate_movements, clean_and_categorize
from src.load import load_data
from src.config import DEFAULT_GOOGLE_SHEET_NAME

# Cargar contraseña oculta desde el archivo .env

load_dotenv()
try:
    # Intenta leerlo de la nube (Streamlit Cloud)
    env_password = st.secrets["RFC"]
except:
    # Si falla, intenta leerlo local (.env)
    env_password = os.getenv("RFC", "")

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Analizador Financiero TDC", page_icon="📠", layout="centered")

st.title("Analizador de Estados de Cuenta",text_alignment="center")
st.write(" Subir Estado de cuenta en formato PDF para extraer los movimientos.")
st.write("Por el momento solo Usar bancos BBVA y Plata.")

# --- INICIALIZAR MEMORIA DE SESIÓN ---
if "datos_procesados" not in st.session_state:
    st.session_state["datos_procesados"] = None

# INTERFAZ DE USUARIO
# Subida de archivo
pdf_file = st.file_uploader("Seleccionar PDF", type=["pdf"])

# Contraseña (con valor por defecto del .env)
user_password = st.text_input("Contraseña (RFC) - Dejar en blanco si el Estado de Cuenta no lo requiere:", 
                              type="password")

# Preferencias de guardado
st.subheader("Opciones de Guardado")
col1, col2 = st.columns(2)
with col1:
    save_local = st.checkbox("Guardar copia local (CSV)", value=False)
with col2:
    save_cloud = st.checkbox("Subir a Nube\n (Acceso limitado)", value=False)


# ORQUESTADOR ETL (Se ejecuta al presionar el botón)
if st.button("Procesar Estado de Cuenta", type="primary"):
    if pdf_file is None:
        st.warning("⚠️ Por favor, sube un archivo PDF primero.")
    else:
        with st.spinner("Analizando y extrayendo datos..."):


            password_final = user_password if user_password != "" else env_password

            # --- FASE 1: EXTRACT ---
            st.toast("Leyendo el PDF y detectando el banco...", icon="📄")
            bank,clabe, fecha, df_msi, df_regular = detect_bank_and_extract(pdf_file, password_final)
            
            if df_regular is not None or df_msi is not None:
                st.toast(f"✅ ¡Datos extraídos de {bank}!", icon="✨")
                # --- FASE 2: TRANSFORM ---
                st.toast("🧹 Limpiando y categorizando movimientos...", icon="⚙️")
                df_raw = consolidate_movements(df_msi, df_regular)
                # categorize and clean
                df_clean = clean_and_categorize(bank,df_raw, fecha)

                #   Guardar en la memoria
                st.session_state["datos_procesados"] = {
                    "df_clean": df_clean,
                    "bank": bank,
                    "clabe": clabe,
                    "fecha": fecha
                }
            
                # --- FASE 3: LOAD ---
                cuentas_autorizadas = ""
                try:
                    cuentas_autorizadas = st.secrets.get("MIS_CLABES", [])
                except:
                    pass
                if save_cloud and len(cuentas_autorizadas) > 0:
                    if clabe not in cuentas_autorizadas:
                        st.warning("🛡️ Por seguridad, la subida a Google Sheets ha sido desactivada porque el PDF no pertenece a la cuenta administradora. Solo podrás descargar el CSV.")
                        save_cloud = False

                st.toast("💾 Preparando para guardar...", icon="📦")
                
                if save_local or save_cloud:
                    load_data(
                        df_clean,
                        clabe,
                        fecha,
                        google_sheet=DEFAULT_GOOGLE_SHEET_NAME,
                        save_local=save_local,
                        save_cloud=save_cloud
                    )
                    st.toast("🚀 ¡Datos guardados exitosamente!", icon="🎉")
                    st.success("✅ ¡Proceso completado exitosamente!")
                else:
                    st.info("ℹ️ Datos extraídos correctamente. Puedes revisarlos en la tabla de abajo antes de decidir guardarlos.")
            else:
                st.session_state["datos_procesados"] = None
                st.error("❌ No se detectó un banco válido o no se encontraron movimientos.")

if st.session_state["datos_procesados"] is not None:
    datos = st.session_state["datos_procesados"]
    df_clean = datos["df_clean"]
    bank = datos["bank"]
    clabe = datos["clabe"]
    fecha = datos["fecha"]

    pago_periodo = round(df_clean['Monto'].loc[df_clean['Tipo_Movimiento'].isin(['MSI','REGULAR'])].sum(),2)

    resumen_monto = df_clean.loc[df_clean['Tipo_Movimiento'].isin(['MSI','REGULAR'])].groupby("Categoria")['Monto'].sum().sort_values(ascending=False)
    summary = resumen_monto.reset_index()
    summary['Porcentaje (%)'] = round((summary['Monto'] / summary['Monto'].sum()) * 100,2)



    st.markdown("---")
    st.subheader(f"📋 Movimientos Extraidos - {bank} ({fecha})")
    st.text(f"Cuota a pagar en periodo: ${pago_periodo}")
    st.subheader("📊 Gastos por Categoría")
    # Streamlit toma automáticamente la columna 'Categoria' para el eje X y 'Monto' para el eje Y
    st.bar_chart(data=summary, x="Categoria", y="Monto", horizontal=True, sort='-Monto')
    st.subheader("📊 Gastos en el periodo")
    # Streamlit toma automáticamente la columna 'Categoria' para el eje X y 'Monto' para el eje Y
    st.bar_chart(data=df_clean.loc[df_clean["Tipo_Movimiento"].isin(["MSI","REGULAR"])], x="Fecha_Operacion", y="Monto")
    st.dataframe(df_clean)

    
    # Botón para descargar archivo CSV
    csv = df_clean.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label="⬇️ Descargar copia en Excel (CSV)",
        data=csv,
        file_name=f"{bank}_{clabe}_{fecha}_movimientos.csv",
        mime="text/csv"
    )

    # Botón para decidir subir a Google Sheets DESPUÉS de haber visto los datos
    if st.button("☁️ Subir esta información a Drive ahora (Limitado)"):
        cuenta_autorizada = ""
        try:
            cuenta_autorizada = st.secrets.get("MIS_CLABES", [])
        except:
            pass

        permitir_subida = True
        if len(cuenta_autorizada) > 0 and clabe not in cuenta_autorizada:
            st.warning("Por seguridad, la subida a Google Sheets no está autorizada para esta cuenta.")
            permitir_subida = False

        if permitir_subida:
            load_data(
                df_clean,
                clabe,
                fecha,
                google_sheet=DEFAULT_GOOGLE_SHEET_NAME,
                save_local=False,
                save_cloud=True
            )
            st.success("¡Datos subidos exitosamente a la nube!")
