import sys
import pandas as pd
import numpy as np
sys.path.append('/home/snparada/Spacionatural/Libraries')
from shopify_lib.products import ShopifyProducts
from shopify_lib.collections import ShopifyCollections
sys.path.append('/home/snparada/Spacionatural/Libraries')
from sheets_lib.main_sheets import GoogleSheets

# Inicializar Google Sheets y ShopifyProducts
sheet = GoogleSheets('1vuUyrii21VxdOIGtwD76DMwnbnCBENJk-qUzYknlR40')
shopify_product = ShopifyProducts()
shopify_collection = ShopifyCollections()

# Función principal para actualizar precios
def update_prices_by_dataframe(productos):
    for index, producto in productos.iterrows():
        sku = producto['sku']
        precio_regular = producto['discount_price']
        precio_comparacion = producto['normal_price']
        variant_id = shopify_product.read_variant_id_by_sku(sku)
        
        if variant_id:
            shopify_product.update_price(variant_id, precio_regular, sku)
            shopify_product.update_price_comparison(variant_id, precio_comparacion, sku)
        else:
            print(f"No se encontró la variante para el SKU: {sku}")


# Leer datos
products_to_update = sheet.read_dataframe('to_upload')
actual_prices = pd.read_csv('/home/snparada/Spacionatural/Data/Dim/Shopify/products_shopify.csv', usecols=['variant_sku', 'id', 'variant_price', 'variant_compare_at_price'])
actual_prices['variant_compare_at_price'] = actual_prices['variant_compare_at_price'].fillna(0)
actual_prices['variant_compare_at_price'] = pd.to_numeric(actual_prices['variant_compare_at_price'], errors='coerce')
actual_prices['variant_price'] = pd.to_numeric(actual_prices['variant_price'], errors='coerce')
actual_prices['variant_price'] = actual_prices[['variant_price', 'variant_compare_at_price']].max(axis=1)
actual_prices['variant_sku'] = actual_prices['variant_sku'].astype(str)
products_to_update['sku'] = products_to_update['sku'].astype(str)


# Renombrar y hacer merge
actual_prices = actual_prices.rename(columns={'variant_price': 'normal_price'})
products_to_update = products_to_update.merge(actual_prices, left_on='sku', right_on='variant_sku', how='left')

# Calcular precios
products_to_update['discount_price'] = products_to_update['normal_price'] * (1 - products_to_update['discount'] / 100)
# Filtrar productos con errores
products_with_errors = products_to_update[
    products_to_update['discount_price'].isnull() | 
    np.isinf(products_to_update['discount_price']) |
    products_to_update['normal_price'].isnull() |
    np.isinf(products_to_update['normal_price'])
][['sku', 'id', 'normal_price']]

# Subir productos con errores a Google Sheets
sheet.update_all_data_by_dataframe(products_with_errors, 'products_with_errors')

# Eliminar productos con errores
products_to_update = products_to_update.dropna(subset=['discount_price', 'normal_price'])
products_to_update = products_to_update[~np.isinf(products_to_update['discount_price']) & ~np.isinf(products_to_update['normal_price'])]

# Redondear precios
products_to_update['discount_price'] = products_to_update['discount_price'].round().astype(int)
products_to_update['normal_price'] = products_to_update['normal_price'].round().astype(int)
products_to_update['id'] = products_to_update['id'].round().astype(int)
products_to_update['sku'] = products_to_update['sku'].astype(str)

# Seleccionar columnas relevantes
products_to_update = products_to_update[['sku', 'id', 'discount_price', 'normal_price']]

# Update collection and prices
shopify_collection.update_collection_products('ofertas-cyber', products_to_update['id'].tolist())
update_prices_by_dataframe(products_to_update)

# Guardar CSV
products_to_update.to_csv('/home/snparada/Spacionatural/E-Commerce/Cyber_Days/1.begin_products_to_update.csv', index=False)
