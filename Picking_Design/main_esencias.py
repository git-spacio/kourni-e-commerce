import pandas as pd
from datetime import datetime

# Definir variables de clasificación
NIVEL_ALTO = 16
NIVEL_MEDIO_ALTO = 7
NIVEL_MEDIO = 0
NIVEL_BAJO = 3

data = pd.read_csv('/home/snparada/Spacionatural/Data/Historical/Finance/historic_sales_with_items.csv', usecols=['items_quantity', 'items_product_description', 'items_product_sku', 'issuedDate', 'sales_channel'], low_memory=False)
data = data[data['sales_channel'] == 'E-Commerce']

# Convertir la columna de fecha a datetime
data['issuedDate'] = pd.to_datetime(data['issuedDate'])

# Filtrar fechas posteriores al 31 de diciembre
fecha_corte = pd.to_datetime('2021-12-31')
data = data[data['issuedDate'] > fecha_corte].copy()

# Convertir descripciones a minúsculas
data['items_product_description'] = data['items_product_description'].str.lower()

# Primero filtramos todos los productos que contienen 'esencia' y '100'
filtered_data = data[
    data['items_product_description'].str.contains('esencia', na=False) &
    data['items_product_description'].str.contains('100', na=False)
].copy()

# === ANÁLISIS ESENCIAS (sin velas) ===
print("\n=== ANÁLISIS ESENCIAS (sin velas) ===")
filtered_data_esencias = filtered_data[
    ~filtered_data['items_product_description'].str.contains('velas', na=False)
].copy()

# Convertir fecha y agrupar por mes
filtered_data_esencias['issuedDate'] = pd.to_datetime(filtered_data_esencias['issuedDate'])
monthly_sales_esencias = filtered_data_esencias.groupby([
    filtered_data_esencias['issuedDate'].dt.to_period('M'),
    'items_product_sku'
])['items_quantity'].sum().reset_index()

# Obtener la descripción única para cada SKU
sku_description_esencias = filtered_data_esencias[['items_product_sku', 'items_product_description']].drop_duplicates()

# Encontrar el máximo, promedio y mediana mensual por SKU
result_esencias = monthly_sales_esencias.groupby('items_product_sku').agg({
    'items_quantity': ['max', 'mean', 'median']
}).reset_index()

# Aplanar las columnas multi-índice
result_esencias.columns = ['items_product_sku', 'max_quantity_monthly', 'avg_quantity_monthly', 'median_quantity_monthly']

# Unir con la descripción
result_esencias = result_esencias.merge(sku_description_esencias, on='items_product_sku', how='left')

# Calcular total vendido por SKU
total_sales_esencias = filtered_data_esencias.groupby('items_product_sku')['items_quantity'].sum().reset_index()
total_sales_esencias.columns = ['items_product_sku', 'total_quantity_sold']

# Unir con la descripción y resultados mensuales
final_result_esencias = result_esencias.merge(total_sales_esencias, on='items_product_sku', how='left')

# Seleccionar y ordenar las columnas requeridas, incluyendo el SKU y total vendido
final_result_esencias = final_result_esencias[['items_product_sku', 'items_product_description', 'max_quantity_monthly', 
                                             'avg_quantity_monthly', 'median_quantity_monthly', 'total_quantity_sold']].copy()

# Redondear el promedio y la mediana a 2 decimales
final_result_esencias.loc[:, 'avg_quantity_monthly'] = final_result_esencias['avg_quantity_monthly'].round(2)
final_result_esencias.loc[:, 'median_quantity_monthly'] = final_result_esencias['median_quantity_monthly'].round(2)

# Ordenar de mayor a menor por max_quantity_monthly
final_result_esencias = final_result_esencias.sort_values('max_quantity_monthly', ascending=False).reset_index(drop=True)

# Modificar la función de clasificación para considerar múltiples métricas
def clasificar_producto(row):
    max_qty = row['max_quantity_monthly']
    avg_qty = row['avg_quantity_monthly']
    median_qty = row['median_quantity_monthly']
    
    # Sistema de puntos
    puntos = 0
    
    # Criterios para máximo
    if max_qty >= NIVEL_ALTO:
        puntos += 3
    elif max_qty >= NIVEL_MEDIO_ALTO:
        puntos += 2
    elif max_qty >= NIVEL_MEDIO:
        puntos += 1
        
    # Criterios para promedio
    if avg_qty >= NIVEL_ALTO:
        puntos += 3
    elif avg_qty >= NIVEL_MEDIO_ALTO:
        puntos += 2
    elif avg_qty >= NIVEL_MEDIO:
        puntos += 1
        
    # Criterios para mediana
    if median_qty >= NIVEL_ALTO:
        puntos += 3
    elif median_qty >= NIVEL_MEDIO_ALTO:
        puntos += 2
    elif median_qty >= NIVEL_MEDIO:
        puntos += 1
    
    # Clasificación final basada en puntos
    if puntos >= 7:
        return 'Alto volumen'
    elif puntos >= 4:
        return 'Volumen medio-alto'
    elif puntos >= 2:
        return 'Volumen medio'
    else:
        return 'Bajo volumen'

# Aplicar la nueva clasificación
final_result_esencias['clasificacion'] = final_result_esencias.apply(clasificar_producto, axis=1)

# Generar resumen
resumen_esencias = final_result_esencias['clasificacion'].value_counts()

print("\nResultado final ordenado (Esencias):")
print(final_result_esencias)

print("\nResumen por grupos (Esencias):")
print(f"Productos de alto volumen (>= {NIVEL_ALTO}): {resumen_esencias.get('Alto volumen', 0)}")
print(f"Productos de volumen medio-alto (entre {NIVEL_ALTO} y {NIVEL_MEDIO_ALTO}): {resumen_esencias.get('Volumen medio-alto', 0)}")
print(f"Productos de volumen medio (entre {NIVEL_MEDIO_ALTO} y {NIVEL_MEDIO}): {resumen_esencias.get('Volumen medio', 0)}")
print(f"Productos de bajo volumen (<= {NIVEL_MEDIO}): {resumen_esencias.get('Bajo volumen', 0)}")

# === ANÁLISIS ESENCIAS CON VELAS ===
print("\n=== ANÁLISIS ESENCIAS CON VELAS ===")
filtered_data_velas = filtered_data[
    filtered_data['items_product_description'].str.contains('velas', na=False)
].copy()

# Convertir fecha y agrupar por mes
filtered_data_velas['issuedDate'] = pd.to_datetime(filtered_data_velas['issuedDate'])
monthly_sales_velas = filtered_data_velas.groupby([
    filtered_data_velas['issuedDate'].dt.to_period('M'),
    'items_product_sku'
])['items_quantity'].sum().reset_index()

# Obtener la descripción única para cada SKU
sku_description_velas = filtered_data_velas[['items_product_sku', 'items_product_description']].drop_duplicates()

# Encontrar el máximo, promedio y mediana mensual por SKU
result_velas = monthly_sales_velas.groupby('items_product_sku').agg({
    'items_quantity': ['max', 'mean', 'median']
}).reset_index()

# Aplanar las columnas multi-índice
result_velas.columns = ['items_product_sku', 'max_quantity_monthly', 'avg_quantity_monthly', 'median_quantity_monthly']

# Unir con la descripción
result_velas = result_velas.merge(sku_description_velas, on='items_product_sku', how='left')

# Calcular total vendido por SKU
total_sales_velas = filtered_data_velas.groupby('items_product_sku')['items_quantity'].sum().reset_index()
total_sales_velas.columns = ['items_product_sku', 'total_quantity_sold']

# Unir con la descripción y resultados mensuales
final_result_velas = result_velas.merge(total_sales_velas, on='items_product_sku', how='left')

# Seleccionar y ordenar las columnas requeridas, incluyendo el SKU y total vendido
final_result_velas = final_result_velas[['items_product_sku', 'items_product_description', 'max_quantity_monthly', 
                                        'avg_quantity_monthly', 'median_quantity_monthly', 'total_quantity_sold']].copy()

# Redondear el promedio y la mediana a 2 decimales
final_result_velas.loc[:, 'avg_quantity_monthly'] = final_result_velas['avg_quantity_monthly'].round(2)
final_result_velas.loc[:, 'median_quantity_monthly'] = final_result_velas['median_quantity_monthly'].round(2)

# Ordenar de mayor a menor por max_quantity_monthly
final_result_velas = final_result_velas.sort_values('max_quantity_monthly', ascending=False).reset_index(drop=True)

# Aplicar la nueva clasificación
final_result_velas['clasificacion'] = final_result_velas.apply(clasificar_producto, axis=1)

# Generar resumen
resumen_velas = final_result_velas['clasificacion'].value_counts()

print("\nResultado final ordenado (Velas):")
print(final_result_velas)

print("\nResumen por grupos (Velas):")
print(f"Productos de alto volumen (>= {NIVEL_ALTO}): {resumen_velas.get('Alto volumen', 0)}")
print(f"Productos de volumen medio-alto (entre {NIVEL_ALTO} y {NIVEL_MEDIO_ALTO}): {resumen_velas.get('Volumen medio-alto', 0)}")
print(f"Productos de volumen medio (entre {NIVEL_MEDIO_ALTO} y {NIVEL_MEDIO}): {resumen_velas.get('Volumen medio', 0)}")
print(f"Productos de bajo volumen (<= {NIVEL_MEDIO}): {resumen_velas.get('Bajo volumen', 0)}")

# Guardar resultados de esencias en CSV
final_result_esencias.to_csv('resultados_esencias.csv', index=False)

# Guardar resultados de velas en CSV
final_result_velas.to_csv('resultados_velas.csv', index=False)

