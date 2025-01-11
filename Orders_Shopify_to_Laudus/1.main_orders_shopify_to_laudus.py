import pandas as pd
import json
import os
import re
from itertools import cycle
import sys
sys.path.append('/home/snparada/Spacionatural/Libraries/')
from laudus_lib.orders import LaudusOrders
from laudus_lib.customers import LaudusCustomers

SALES_ORDERS = 'https://api.laudus.cl/sales/orders'
ORDERS_LIST = 'https://api.laudus.cl/sales/orders/list'


def format_rut(rut):
    print(rut)
    print(type(rut))
    rut = str(rut)
    cleaned_rut = re.sub(r'[^0-9Kk]', '', rut).upper()
    if len(cleaned_rut) != 9 and len(cleaned_rut) != 8:  # Asumiendo RUTs de 8 o 9 dígitos
        return "Formato de RUT incorrecto"
    if len(cleaned_rut) == 9:
        formatted_rut = f'{cleaned_rut[:-7]}.{cleaned_rut[-7:-4]}.{cleaned_rut[-4:-1]}-{cleaned_rut[-1]}'
    else:
        formatted_rut = f'{cleaned_rut[:-6]}.{cleaned_rut[-6:-3]}.{cleaned_rut[-3:-1]}-{cleaned_rut[-1]}'
    return formatted_rut

def check_rut(rut):
    # Asegurarse de que el RUT está en formato adecuado (sin puntos ni guiones)
    rut_cleaned = re.sub(r'[\.\-]', '', rut)
    # Extraer el número y el dígito verificador (último carácter)
    rut_number = rut_cleaned[:-1]
    dv = rut_cleaned[-1].upper()  # El DV puede ser un número o 'K'

    # Preparar para calcular el dígito verificador
    reversed_digits = map(int, reversed(rut_number))  # Esto convertirá cada carácter en un entero
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    check_digit = (-s) % 11

    if check_digit == 10:
        check_digit = 'K'
    else:
        check_digit = str(check_digit)

    return check_digit == dv

def read_orders_uploaded():
    path = "/home/snparada/Spacionatural/E-Commerce/orders_connections/0.last_order_uploaded_to_laudus.json"

    if os.path.exists(path):
        # Abrir el archivo JSON
        with open(path, 'r') as file:
            # Leer el contenido del archivo
            contenido = file.read()

            try:
                # Parsear el contenido JSON
                data = json.loads(contenido)
                
                # Obtener el valor asociado a la clave '55995'
                valor = data['55995']
                
                return valor
            except json.JSONDecodeError:
                print("Error: El formato del archivo JSON no es válido.")
                return None
            except KeyError:
                print("Error: La clave '55995' no existe en el archivo JSON.")
                return None
    else:
        print("El archivo JSON no existe en la ruta especificada.")
        return None

def sub_main_1_extract_orders():
    
    # Variables
    orders_uploaded_to_laudus = read_orders_uploaded()
    shopify_historic_orders = pd.read_csv('/home/snparada/Spacionatural/Data/Recent/recent_orders_shopify.csv')
    
    # Verificar si orders_uploaded_to_laudus es None (lo que indica un error al leer el archivo)
    if orders_uploaded_to_laudus is None:
        print("No se pudieron leer las órdenes subidas a Laudus.")
        return shopify_historic_orders

    # Filtrar las órdenes de Shopify, excluyendo aquellas que ya han sido subidas a Laudus
    orders_to_process = shopify_historic_orders[~shopify_historic_orders['orders'].isin(orders_uploaded_to_laudus)]

    print("Órdenes de Shopify filtradas para procesar:", len(orders_to_process))
    return orders_to_process

def sub_main_2_formating_data(order_to_process):
    Laudus_customers = LaudusCustomers()
    rut_formateado = format_rut(order_to_process['rut'])
    
    if check_rut(rut_formateado):
        print(f"El rut {rut_formateado} es valido")
        check_user = Laudus_customers.check_customer_exists(rut_formateado)
        print (f"El check user es: {check_user}")

        region = order_to_process['region']
        if len(region) > 15:
            region = region[:15]

        if check_user == False:
            customer_data = {
                'customer': {
                    'firstname': order_to_process['name'],
                    'lastname': order_to_process['lastname'],
                    'dni': format_rut(order_to_process['rut']),
                    'payment': order_to_process['payment'],
                    'address': order_to_process['address'],
                    'region': region,
                    'comuna': order_to_process['city'],
                    'email': order_to_process['email'],
                    'phone': order_to_process['phone_mobile']
                }
            }
            json_customer = Laudus_customers.create_json_customer(customer_data)
            create_user = Laudus_customers.create_new_user(json_customer)

            if create_user['status'] == True:
                print(f"El usuario creado con exito")
                address_data = {
                    'address': {
                        'direccion': order_to_process['address'],
                        'comuna': order_to_process['city'],
                        'region': region
                    }
                }
                customer_id = create_user["response"]["customerId"]
                check_user_address = Laudus_customers.create_address_for_customer(customer_id, address_data)
                
                # CREATE ORDER ON LAUDUS
                if check_user_address['status'] == True:

                    if (create_order['status'] == True):
                        print(f'pedido creado con exito')
                    else:
                        print(
                            f'Hubo un error al crear el pedido: {json_order_data}')
                
                elif check_user_address['status'] == False:
                    address_data = {
                        'address': {
                            'direccion': order_to_process['address'],
                            'comuna': order_to_process['city'],
                            'region': region
                        }
                    }
                    customer_id = create_user["response"]["customerId"]
                    check_user_address = Laudus_customers.create_address_for_customer(customer_id, address_data)

                    if (create_order['status'] == True):
                        print(f'pedido creado con exito')
                    else:
                        print(
                            f'Hubo un error al crear el pedido: {json_order_data}')
    else:
        print(f"No se puedo crear el pedido porque el rut no es valido")
    
    return print(':)')

def main():
    orders_to_process = sub_main_1_extract_orders()
    for index, order_to_process in orders_to_process.iterrows():
        print(order_to_process['rut'])
        print(':)')
        sub_main_2_formating_data(order_to_process.to_dict())
        exit()

main()