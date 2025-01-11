import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

# Definir las columnas necesarias
columns_needed = ['salesInvoiceId', 'items_product_sku', 'items_quantity']

# Cargar los datos desde el archivo CSV
file_path = '/home/snparada/Spacionatural/Data/Historical/historic_orders_laudus_with_items.csv'
df = pd.read_csv(file_path, usecols=columns_needed, low_memory=False)

# Crear una tabla de productos por orden
basket = df.groupby(['salesInvoiceId', 'items_product_sku'])['items_quantity'].sum().unstack().reset_index().fillna(0).set_index('salesInvoiceId')
basket = basket.applymap(lambda x: 1 if x > 0 else 0)

# Aplicar el algoritmo Apriori
frequent_itemsets = apriori(basket, min_support=0.01, use_colnames=True)

# Generar las reglas de asociación
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)

# Filtrar las reglas con un mínimo de confianza y lift
rules = rules[(rules['lift'] >= 1) & (rules['confidence'] >= 0.5)]

# Función para obtener los productos complementarios
def get_complementary_products(product_sku, rules, top_n=10):
    complementary = rules[rules['antecedents'] == {product_sku}]
    complementary = complementary.sort_values(by='lift', ascending=False).head(top_n)
    return [list(conseq)[0] for conseq in complementary['consequents']]

# Obtener todos los productos SKU únicos
all_products = df['items_product_sku'].unique()

# Crear un diccionario para almacenar los productos complementarios
complementary_products_dict = {product: get_complementary_products(product, rules) for product in all_products}

# Crear un DataFrame con el resultado
result_df = pd.DataFrame(list(complementary_products_dict.items()), columns=['sku', 'complementary_products'])

# Guardar el resultado en un archivo CSV
output_path = '/home/snparada/Spacionatural/Data/Processed_Data/complementary_products.csv'
result_df.to_csv(output_path, index=False)

print(f"Archivo guardado en: {output_path}")
