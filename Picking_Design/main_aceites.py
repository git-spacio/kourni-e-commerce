import pandas as pd
from datetime import datetime

data = pd.read_csv('/home/snparada/Spacionatural/Data/Historical/Finance/historic_sales_with_items.csv', usecols=['items_quantity', 'items_product_description', 'items_product_sku', 'issuedDate'], low_memory=False)

# Definir lista de palabras a filtrar
palabras_filtro = ['aceite', '100']

# Convertir la columna de fecha a datetime
data['issuedDate'] = pd.to_datetime(data['issuedDate'])

# Filtrar fechas posteriores al 31 de diciembre
fecha_corte = pd.to_datetime('2020-12-31')
data = data[data['issuedDate'] > fecha_corte].copy()

# Convertir descripciones a minúsculas
data['items_product_description'] = data['items_product_description'].str.lower()

# Primero identificar los SKUs que corresponden a moldes
sku_moldes = data.copy()
for palabra in palabras_filtro:
    sku_moldes = sku_moldes[
        sku_moldes['items_product_description'].str.contains(palabra, na=False)
    ]
lista_skus_moldes = sku_moldes['items_product_sku'].unique()

# Ahora filtrar el dataset original usando los SKUs identificados
filtered_data = data[data['items_product_sku'].isin(lista_skus_moldes)].copy()

# === ANÁLISIS PRODUCTOS ===
print(f"\n=== ANÁLISIS PRODUCTOS ({', '.join(palabras_filtro).upper()}) ===")

# Convertir fecha y agrupar por mes
filtered_data['issuedDate'] = pd.to_datetime(filtered_data['issuedDate'])
monthly_sales = filtered_data.groupby([
    filtered_data['issuedDate'].dt.to_period('M'),
    'items_product_sku'
])['items_quantity'].sum().reset_index()

# Obtener la descripción única para cada SKU
sku_description = filtered_data[['items_product_sku', 'items_product_description']].drop_duplicates(
    subset=['items_product_sku'],
    keep='first'
)

# Encontrar el máximo, promedio, mediana y total mensual por SKU
result = monthly_sales.groupby('items_product_sku').agg({
    'items_quantity': ['max', 'mean', 'median', 'sum']
}).reset_index()

# Aplanar las columnas multi-índice
result.columns = ['items_product_sku', 'max_quantity_monthly', 'avg_quantity_monthly', 'median_quantity_monthly', 'total_quantity']

# Unir con la descripción
result = result.merge(sku_description, on='items_product_sku', how='left')

# Seleccionar y ordenar las columnas requeridas
final_result = result[['items_product_sku', 'items_product_description', 'max_quantity_monthly', 'avg_quantity_monthly', 'median_quantity_monthly', 'total_quantity']].copy()

# Redondear el promedio y la mediana a 2 decimales
final_result.loc[:, 'avg_quantity_monthly'] = final_result['avg_quantity_monthly'].round(2)
final_result.loc[:, 'median_quantity_monthly'] = final_result['median_quantity_monthly'].round(2)

# Filtrar outliers
final_result = final_result[final_result['max_quantity_monthly'] <= 200].copy()

# Ordenar de mayor a menor por max_quantity_monthly
final_result = final_result.sort_values('max_quantity_monthly', ascending=False).reset_index(drop=True)

print("\nResultado final ordenado (Molde):")
print(final_result)

# Guardar resultados en CSV
nombre_archivo = f"resultados_{'_'.join(palabras_filtro)}.csv"
final_result.to_csv(nombre_archivo, index=False)

