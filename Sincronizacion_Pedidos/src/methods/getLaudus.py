import requests
import datetime
import dateutil.parser
import json
import os
from dateutil import tz
from Sincronizacion_Pedidos.src.keys.credentialsLaudus import parametros
from Sincronizacion_Pedidos.src.const.const import headers, headers_laudus, token_info
from Sincronizacion_Pedidos.src.methods.postLaudus import post_laudus_token, post_laudus
from Sincronizacion_Pedidos.src.const.const import headers, headers_laudus, token_info, TOKEN_PATH

def get_laudus(url, headers_auth, parametros={}):
    try:

        response = requests.get(url, headers=headers_auth, json=parametros)
        result = {'status': False, 'response': None}

        if response.status_code == 200:
            result['status'] = True
            result['response'] = response.json()
        elif response.status_code == 204:
            result['status'] = False
        else:
            print(
                f'Error en la busqueda de la url: {url}, respuesta del servidor: {response.text}')
    except json.JSONDecodeError:
        print("La respuesta no es JSON o está vacía")

    return result


def get_current_laudus_token():
    global token_info
    # Si el archivo no existe, obtén un nuevo token
    if not os.path.isfile(TOKEN_PATH):
        print(f"No hay token, hay que pedirlo a Laudus.")
        token_info = post_laudus_token()

        with open(TOKEN_PATH, 'w') as f:
            json.dump(token_info, f)
        print(f"Token solicitado y guardado en {TOKEN_PATH}")
    else:  # Si el archivo existe, carga el token y verifica la expiración
        with open(TOKEN_PATH, 'r') as f:
            token_info = json.load(f)
        # Hacer que el tiempo actual sea consciente de la zona horaria
        current_time = datetime.datetime.now(tz.tzlocal())
        if current_time >= dateutil.parser.parse(token_info['expiration']):
            print(f"El token ha expirado, hay que pedir uno nuevo.")
            token_info = post_laudus_token()
            with open(TOKEN_PATH, 'w') as f:
                json.dump(token_info, f)
            print(f"Nuevo token solicitado y guardado en {TOKEN_PATH}")
        else:
            print(f"El token aún es válido.")

    return token_info['token']


def get_product_id_laudus(clean_carts_rows, headers_auth):
    id_products = []
    url = f'https://api.laudus.cl/production/products/list'
    for row in clean_carts_rows:
        new_dict = {}
        product_id = post_laudus(url,
                                 headers_auth,
                                 {
                                     "options": {
                                         "offset": 0,
                                         "limit": 0
                                     },
                                     "fields": [
                                         "productId",
                                         "unitPrice"
                                     ],
                                     "filterBy": [
                                         {
                                             "field": "sku",
                                             "operator": "=",
                                             "value": f"{row['reference']}"
                                         }
                                     ]
                                 }
                                 )
        # print(product_id)
        new_dict['productId'] = product_id['response'][0]['productId']
        new_dict['unitPrice'] = product_id['response'][0]['unitPrice']
        new_dict['quantity'] = row['quantity']
        id_products.append(new_dict)
    return id_products