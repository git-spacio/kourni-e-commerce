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
        precio_regular = producto['normal_price']
        precio_comparacion = producto['comparison_price']
        variant_id = shopify_product.read_variant_id_by_sku(sku)
        
        if variant_id:
            shopify_product.update_price(variant_id, precio_regular, sku)
            shopify_product.update_price_comparison(variant_id, precio_comparacion, sku)
        else:
            print(f"No se encontró la variante para el SKU: {sku}")


# Leer datos
products_to_update = pd.read_csv('/home/snparada/Spacionatural/E-Commerce/Cyber_Days/1.begin_products_to_update.csv')
products_to_update['comparison_price'] = 0
products_to_update['sku'] = products_to_update['sku'].astype(str)

# Filtrar productos con errores
products_with_errors = products_to_update[
    products_to_update['normal_price'].isnull() |
    np.isinf(products_to_update['normal_price'])
][['sku', 'id', 'normal_price']]

# Eliminar productos con errores
products_to_update = products_to_update.dropna(subset=['normal_price'])
products_to_update = products_to_update[~np.isinf(products_to_update['normal_price'])]

# Redondear precios
products_to_update['comparison_price'] = products_to_update['comparison_price'].round().astype(int)
products_to_update['normal_price'] = products_to_update['normal_price'].round().astype(int)
products_to_update['id'] = products_to_update['id'].round().astype(int)
products_to_update['sku'] = products_to_update['sku'].astype(str)

# Update collection and prices
update_prices_by_dataframe(products_to_update)

# Subir productos con errores a Google Sheets
sheet.update_all_data_by_dataframe(products_with_errors, 'products_with_errors')
