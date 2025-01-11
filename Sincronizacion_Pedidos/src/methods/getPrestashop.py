import requests
from Sincronizacion_Pedidos.src.keys.credentialsPrestashop import prestashop_key
from Sincronizacion_Pedidos.src.const.const import headers
from Sincronizacion_Pedidos.src.urls.urlApiPrestashop import prestashop_url


def get_prestashop_data(url):
    response = requests.get(url, auth=(prestashop_key, ''), headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        return None


def get_orders():

    url = f"{prestashop_url}/orders?output_format=JSON&filter[current_state]=[2 | 10 ]"
    data = get_prestashop_data(url)
    if data is not None:
        return data['orders']
    else:
        return None


def get_cart(id_cart):
    url = f"https://spacionatural.cl/api/carts/{id_cart}?output_format=JSON"
    # print (url)
    data = get_prestashop_data(url)
    if data is not None:
        return data['cart']
    else:
        return None