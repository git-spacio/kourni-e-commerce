import pandas as pd
import datetime
from dateutil import relativedelta
import sys

# Añadiendo la ruta de la librería a sys.path
sys.path.append('/home/snparada/Spacionatural/Libraries')

# Importando la clase SearchConsole desde la librería
from search_console_lib.main_gsc import SearchConsole

# Insert your Search Console SITE PROPERTY.
site = 'https://spacionatural.cl'

# Instanciar el objeto SearchConsole
sc = SearchConsole(site)

# Insertar el rango de fechas (últimos 3 meses de datos de SC por defecto)
end_date = datetime.date.today()
start_date = end_date - relativedelta.relativedelta(months=1)

# Obtener la entrada de categoría de dispositivo
device_category = input('Enter device category: MOBILE, DESKTOP or TABLET (leave it blank for all devices): ').strip()

# Obtener los datos de Search Console
df = sc.get_search_data(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), device_category=device_category)

# Limpiar el DataFrame y ordenarlo por consulta
SERP_results = 5  # inserta aquí tu valor preferido para los resultados de SERP
branded_queries = 'spacionatural|spacio natural|espacionatural|espacio natural'  # inserta aquí tus consultas de marca

df_canibalized = df[df['position'] > SERP_results]
df_canibalized = df_canibalized[~df_canibalized['query'].str.contains(branded_queries, regex=True)]
df_canibalized = df_canibalized[df_canibalized.duplicated(subset=['query'], keep=False)]
df_canibalized.set_index(['query'], inplace=True)
df_canibalized.sort_index(inplace=True)
df_canibalized.reset_index(inplace=True)

# Formatear el CTR y la posición
df_canibalized['ctr'] = df_canibalized['ctr'].round(1)
df_canibalized['position'] = df_canibalized['position'].astype(int)

# Guardar el DataFrame resultante en un archivo CSV sin hacer crawling
df_canibalized.to_csv('/home/snparada/Spacionatural/E-Commerce/SEO/Canibalization/canibalized_keywords.csv', index=False)

print("The data has been saved to canibalized_keywords.csv")
