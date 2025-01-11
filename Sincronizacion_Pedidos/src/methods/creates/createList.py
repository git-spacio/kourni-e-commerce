from Sincronizacion_Pedidos.src.methods.getPrestashop import get_prestashop_data


def create_list_id_products_prestashop(carts_rows):
    id_products = []
    # Iterar sobre los elementos en 'cart_rows'
    for row in carts_rows['cart_rows']:
        # Crear un nuevo diccionario vacío
        new_dict = {}
        # Si el id_product_attribute es '0', añadir el id_product a la lista
        if row['id_product_attribute'] == '0':
            url = f'https://spacionatural.cl/api/products?filter[id]=[{row["id_product"]}]&display=[reference]&output_format=JSON'
            json_product = get_prestashop_data(url)
            # print(json_product)
            new_dict['reference'] = json_product['products'][0]['reference']
            # new_dict['id_producto'] = row['id_product']
            # new_dict['id_producto'] = row['id_product']

        # Si el id_product_attribute es distinto de '0', añadir el id_product_attribute a la lista
        else:
            url = f'https://spacionatural.cl/api/combinations?filter[id]=[{row["id_product_attribute"]}]&display=[reference]&output_format=JSON'
            json_product = get_prestashop_data(url)
            # print(json_product)
            new_dict['reference'] = json_product['combinations'][0]['reference']
            # new_dict['id_product_attribute'] = row['id_product_attribute']

        # Añadir quantity a new_dict
        new_dict['quantity'] = row['quantity']
        # Añadir new_dict a la lista resultado
        id_products.append(new_dict)
    return id_products

def clean_list_id_products_prestashop(carts_rows):
    # Recorre la lista de diccionarios
    for i in carts_rows:
        # Si la clave 'reference' en un diccionario contiene un guion ("-")
        if '-' in i['reference']:
            # Divide el string por el guion, toma el valor del medio (índice 1)
            # multiplica por 'quantity' y actualiza la clave 'quantity'
            middle_value = int(i['reference'].split('-')[1])
            i['quantity'] = str(int(i['quantity']) * middle_value)
            # Actualizar el valor de 'reference' para quitar los números y guiones después del primer guión
            i['reference'] = i['reference'].split('-')[0]
    return carts_rows


def create_order_data(customerId, payment, reference, addressId, clean_carts_rows, total_shipping_tax_incl):
    order_data = {
        'order': {
            'customerId': customerId,
            'payment': payment,
            'reference': reference,
            'addressId': addressId,
            'carts_rows': clean_carts_rows,
            'total_shipping_tax_incl': total_shipping_tax_incl
        }
    }

    return order_data