import pandas as pd
import numpy as np
from datetime import datetime

def analizar_recompras(sku):
    # Leer solo las columnas necesarias del CSV
    columnas = ['customer_customerid', 'customer_name', 'items_product_sku', 'issuedDate']
    df = pd.read_csv('/home/snparada/Spacionatural/Data/Historical/Finance/historic_sales_with_items.csv', 
                     usecols=columnas, 
                     low_memory=False)
    
    # Convertir la columna de fecha a datetime
    df['issuedDate'] = pd.to_datetime(df['issuedDate'])
    
    # Excluir CLIENTE BOLETA y filtrar por SKU
    df = df[df['customer_name'] != 'CLIENTE BOLETA']
    df_sku = df[df['items_product_sku'] == sku]
    
    # Agrupar por cliente y contar compras
    clientes_frecuentes = df_sku.groupby('customer_customerid')['issuedDate'].agg(['count', list]).reset_index()
    
    # Filtrar clientes con más de una compra
    clientes_frecuentes = clientes_frecuentes[clientes_frecuentes['count'] > 1]
    
    if len(clientes_frecuentes) == 0:
        print(f"No hay clientes con recompras para el SKU {sku}")
        return
    
    # Calcular días entre compras para cada cliente
    dias_entre_compras = []
    
    for _, row in clientes_frecuentes.iterrows():
        fechas = sorted(row['list'])
        diferencias = [(fechas[i+1] - fechas[i]).days for i in range(len(fechas)-1)]
        dias_entre_compras.extend(diferencias)
    
    # Calcular estadísticas
    promedio = np.mean(dias_entre_compras)
    mediana = np.median(dias_entre_compras)
    desviacion = np.std(dias_entre_compras)
    minimo = np.min(dias_entre_compras)
    maximo = np.max(dias_entre_compras)
    
    # Imprimir resultados
    print(f"\nResultados para el SKU: {sku}")
    print(f"Número de clientes con recompras: {len(clientes_frecuentes)}")
    print(f"\nEstadísticas de días entre compras:")
    print(f"Promedio: {promedio:.2f} días")
    print(f"Mediana: {mediana:.2f} días")
    print(f"Desviación estándar: {desviacion:.2f} días")
    print(f"Mínimo: {minimo} días")
    print(f"Máximo: {maximo} días")

if __name__ == "__main__":
    sku_input = input("Ingrese el SKU a analizar: ")
    analizar_recompras(sku_input)
