import pandas as pd
import datetime
from dateutil import relativedelta
import requests
from bs4 import BeautifulSoup
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
start_date = end_date - relativedelta.relativedelta(months=3)

# Obtener la entrada de categoría de dispositivo
device_category = input('Enter device category: MOBILE, DESKTOP or TABLET (leave it blank for all devices): ').strip()

# Obtener los datos de Search Console
df = sc.get_search_data(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), device_category=device_category)

# Limpiar el DataFrame y ordenarlo por consulta
SERP_results = 8  # inserta aquí tu valor preferido para los resultados de SERP
branded_queries = 'spacionatural|spacio natural|espacionatural|espacio natural'  # inserta aquí tus consultas de marca

df_canibalized = df[df['position'] > SERP_results]
df_canibalized = df_canibalized[~df_canibalized['query'].str.contains(branded_queries, regex=True)]
df_canibalized = df_canibalized[df_canibalized.duplicated(subset=['query'], keep=False)]
df_canibalized.set_index(['query'], inplace=True)
df_canibalized.sort_index(inplace=True)
df_canibalized.reset_index(inplace=True)

# Raspando URLs y añadiendo títulos y meta descripciones al DataFrame
def get_meta(url):
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        title = soup.find('title').get_text() if soup.find('title') else 'No title'
        meta_tag = soup.select('meta[name="description"]')
        meta = meta_tag[0].attrs["content"] if meta_tag else 'No meta description'
        return title, meta
    except Exception as e:
        return 'No title', 'No meta description'

df_canibalized['title'], df_canibalized['meta'] = zip(*df_canibalized['page'].apply(get_meta))

# Guardar el DataFrame resultante en un archivo CSV
df_canibalized.to_csv('canibalized_keywords.csv', index=False)

print("The data has been saved to canibalized_keywords.csv")
