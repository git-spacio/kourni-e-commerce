import sys
sys.path.append('/home/snparada/Spacionatural/Libraries/shopify_lib')
from products import ShopifyProducts
sys.path.append('/home/snparada/Spacionatural/Libraries/')
from openai_lib.gpt import GPT
import pandas as pd
import json
from tqdm import tqdm
import time

"""
Generamos la relación de los productos usando IA para los productos faltantes.
"""

def analyze_product(product_id, title, all_products, gpt):
    products_list = ", ".join([f"{id}: {title}" for id, title in all_products])
    prompt = f"""
    Analiza el siguiente producto con ID {product_id} y título: "{title}"
    1. Identifica qué producto es y para qué sirve.
    2. De la siguiente lista de productos disponibles en la tienda (formato ID: Título): 
       {products_list}
       Sugiere hasta 10 productos complementarios que se usen junto con "{title}".
       Ordénalos desde el más probable de vender de manera complementaria hasta el menos probable.
    """
    response = gpt.generate_by_text(prompt, max_tokens=1000, temperature=0.7, model='gpt-4o')
    prompt = f"""Entrega esta {response} en un formato JSON con campos 'product_type', 'complementary_products'
       Donde 'complementary_products' es una lista ordenada de IDs de productos. 
       Entregalo sin ```json, sólo escribelo como si estuvieses escribiendo el archivo."""
    time.sleep(3)
    response = gpt.generate_by_text(prompt, max_tokens=1000, temperature=0, model='gpt-4o-mini')

    return json.loads(response)

def main():
    products = ShopifyProducts()
    df = products.read_all_products_in_dataframe()
    gpt = GPT()

    # Filter only active products (not in draft)
    df = df[df['status'] == 'active']
    # Obtener lista de todos los productos con ID y título
    all_products = list(zip(df['id'], df['title']))

    update_option = 'faltantes'
    
    results = []
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Procesando productos"):
        time.sleep(1)
        product_id = row['id']
        title = row['title']

        actual_complementary_products = products.read_actual_complementary_products(product_id)

        if actual_complementary_products is not None and len(actual_complementary_products) > 0:
            if update_option == 'faltantes':
                continue
            elif update_option == 'todos':
                # Remover productos complementarios existentes
                exit()
        

        analysis = analyze_product(product_id, title, all_products, gpt)
        complementary_products = analysis['complementary_products']

        # Verificar que los IDs existen en el DataFrame
        valid_complementary = [str(id) for id in complementary_products if str(id) in df['id'].astype(str).values]
        valid_complementary = valid_complementary[:10]  # Limitar a 10 productos

        # Añadir productos complementarios usando el método de ShopifyProducts
        for comp_product_id in valid_complementary:
            products.update_complementary_products(product_id, comp_product_id)

        results.append({
            'id': product_id,
            'complementary_products': valid_complementary
        })

        print(f"Se agregaron {len(valid_complementary)} productos complementarios a {title} (ID: {product_id})")

    print("Proceso completado. Se han actualizado los productos complementarios.")

if __name__ == "__main__":
    main()
