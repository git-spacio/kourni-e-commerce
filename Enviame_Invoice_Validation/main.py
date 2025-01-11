import pandas as pd

# Cargar el archivo CSV en un DataFrame
file_path = '/home/snparada/Spacionatural/Data/Historical/historic_orders_shopify.csv'
df = pd.read_csv(file_path)

# Convertir la columna `date` a datetime
df['date'] = pd.to_datetime(df['date'], utc=True)

# Definir el intervalo de fechas
start_date = pd.to_datetime('2024-05-01', utc=True)
end_date = pd.to_datetime('2024-05-31', utc=True)

# Filtrar el DataFrame por el intervalo de fechas
filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

# Reemplazar 'N/A' y otros valores no numéricos en `delivery_amout` con 0
filtered_df['delivery_amout'] = filtered_df['delivery_amout'].replace('N/A', 0).astype(float)

# Calcular la cantidad de cada tipo de `delivery_name` y el total de `delivery_amout` por tipo de entrega
result = filtered_df.groupby('delivery_name').agg(
    delivery_amount=('delivery_amout', 'sum'),
    deliveries_count=('delivery_name', 'count')
).reset_index()

# Calcular el total de deliveries_count y delivery_amount
total_delivery_amount = result['delivery_amount'].sum()
total_deliveries_count = result['deliveries_count'].sum()

# Añadir la fila de totales al DataFrame de resultados
total_row = pd.DataFrame({'delivery_name': ['Total'], 
                          'delivery_amount': [total_delivery_amount], 
                          'deliveries_count': [total_deliveries_count]})

result = pd.concat([result, total_row], ignore_index=True)

# Mostrar el resultado
print(result)
