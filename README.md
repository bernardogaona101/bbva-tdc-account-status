📊 ETL Automático: Estados de Cuenta BBVA

Un pipeline de datos (ETL) construido en Python para extraer, transformar y consolidar movimientos financieros desde estados de cuenta en PDF (BBVA México).

🚀 Características

Extracción Segura: Lee PDFs protegidos con contraseña extrayendo datos con pdfplumber.

Transformación Inteligente: Clasifica Compras a Meses Sin Intereses (MSI), pagos regulares y recategoriza cobros parciales para conocer el gasto real del mes.

Interfaz Gráfica (GUI): Selección de archivos y captura segura del RFC mediante tkinter.

Seguridad: Integración con .env para gestionar contraseñas localmente sin exponer datos sensibles.

🛠️ Tecnologías Usadas

Python 3.x

pandas - Limpieza y estructuración de datos.

pdfplumber - Extracción de texto desde PDFs complejos.

re (RegEx) - Búsqueda de patrones financieros.

python-dotenv - Manejo seguro de variables de entorno.

⚙️ Instalación y Uso

Clonar el repositorio y crear el entorno virtual:

git clone https://github.com/bernardogaona101/account_status.git
cd account_status
python -m venv venv
# Activar entorno: venv\Scripts\activate (Windows) o source venv/bin/activate (Mac/Linux)


Instalar dependencias:

pip install -r requirements.txt


Configurar credenciales (Opcional pero recomendado):
Crea un archivo .env en la raíz del proyecto y agrega tu RFC (contraseña del PDF):

RFC_BBVA=TUPASSWORD123


Ejecutar:

python main.py
