import pandas as pd
from itertools import combinations
from collections import defaultdict

# Definir las columnas necesarias
columns_needed = ['salesInvoiceId', 'items_product_sku']

# Definir la lista de SKU a excluir
excluded_skus = ['6128', '6518', '5851', '5833', '6782', '609240', '6012', '7043', '7075', '5816', '6149', '6150', '6313', '6151','6889', 'ajuste redondeo', '6912','6918','6965','6029','6516','6835','6253','6917','6028','16084']

# Cargar los datos desde el archivo CSV
file_path = '/home/snparada/Spacionatural/Data/Historical/historic_orders_laudus_with_items.csv'
df = pd.read_csv(file_path, usecols=columns_needed, low_memory=False)

# Filtrar los SKU excluidos
df = df[~df['items_product_sku'].isin(excluded_skus)]

# Crear una lista de productos por cada orden
orders = df.groupby('salesInvoiceId')['items_product_sku'].apply(list)

# Crear una matriz de co-ocurrencias
co_occurrence = defaultdict(lambda: defaultdict(int))

for order in orders:
    for product_a, product_b in combinations(order, 2):
        co_occurrence[product_a][product_b] += 1
        co_occurrence[product_b][product_a] += 1

# Convertir a DataFrame para facilidad de manejo
co_occurrence_df = pd.DataFrame(co_occurrence).fillna(0)

# Función para obtener los 10 productos más comprados junto con cada producto
def top_complementary_products(product_id, top_n=10):
    if product_id in co_occurrence_df:
        top_products = co_occurrence_df[product_id].sort_values(ascending=False).head(top_n)
        return top_products.index.tolist()
    else:
        return []

# Obtener todos los productos SKU únicos
all_products = df['items_product_sku'].unique()

# Crear un diccionario para almacenar los productos complementarios
complementary_products_dict = {product: top_complementary_products(product) for product in all_products}

# Crear un DataFrame con el resultado
result_df = pd.DataFrame(list(complementary_products_dict.items()), columns=['sku', 'complementary_products'])

# Guardar el resultado en un archivo CSV
output_path = '/home/snparada/Spacionatural/Data/Processed_Data/complementary_products.csv'
result_df.to_csv(output_path, index=False)

print(f"Archivo guardado en: {output_path}")
