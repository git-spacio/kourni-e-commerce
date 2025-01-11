import pandas as pd
import sys
from tqdm import tqdm
sys.path.append('/home/snparada/Spacionatural/Libraries/shopify_lib')
from products import ShopifyProducts
import time

# Cargar el archivo de productos complementarios
complementary_file_path = '/home/snparada/Spacionatural/Data/Processed_Data/complementary_products.csv'
complementary_df = pd.read_csv(complementary_file_path)

# Inicializar la clase ShopifyProducts
shopify_products = ShopifyProducts()

# Iterar sobre el DataFrame y subir los productos complementarios uno por uno
for index, row in tqdm(complementary_df.iterrows(), total=len(complementary_df), desc="Updating complementary products"):
    sku = row['sku']
    product_id = shopify_products.sku_to_product_id.get(str(sku))
    if product_id:
        # Primero eliminar los productos complementarios existentes
        shopify_products.delete_complementary_products(int(product_id))
        
        # Luego agregar los nuevos productos complementarios
        complementary_skus = eval(row['complementary_products'])
        for complementary_sku in complementary_skus:
            complementary_product_id = shopify_products.sku_to_product_id.get(str(complementary_sku))
            if complementary_product_id:
                shopify_products.update_complementary_products(int(product_id), int(complementary_product_id))
            else:
                print(f"Complementary product ID not found for SKU {complementary_sku}")
        time.sleep(0.1)
    else:
        print(f"Product ID not found for SKU {sku}")

print("Completed updating complementary products.")
