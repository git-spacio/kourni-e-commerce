import requests
from Sincronizacion_Pedidos.src.keys.credentialsLaudus import parametros
from Sincronizacion_Pedidos.src.const.const import headers, headers_laudus, token_info
import json


def post_laudus_token():

    auth_url = 'https://api.laudus.cl/security/login'

    response = requests.post(auth_url, json=parametros, headers=headers)

    if response.status_code == 200:
        token = response.json()
        return token
    else:
        print(f'Error obteniendo token Laudus: {response.text}')


def post_laudus(url, headers_auth, parametros={}):
    # print(f'Error en la busqueda de la url: {url}, respuesta del servidor: {response.text}')
    response = requests.post(url, headers=headers_auth, json=parametros)
    result = {'status': False, 'response': None}
    # if response.status_code == 200:
    #     return True
    # elif response.status_code == 204:
    #     return False
    if response.status_code == 200:
        result['status'] = True

        result['response'] = response.json()
        # try:
        #     response_data = response.json()
        #     if response_data and isinstance(response_data, list) and 'customerId' in response_data[0]:
        #         result['customerId'] = response_data
        # except json.JSONDecodeError:
        #     print("La respuesta no es JSON o está vacía")
    elif response.status_code == 204:
        result['status'] = False
    else:
        print(
            f'Error en la busqueda de la url: {url}, respuesta del servidor: {response.text}')
    return result


def post_laudus_v2(url, headers_auth, parametros={}):
    try:
        response = requests.post(url, headers=headers_auth, json=parametros)
        result = {'status': None, 'response': None}

        if response.status_code == 200:
            result['status'] = True
            result['response'] = response.json()
        elif response.status_code == 204:
            result['status'] == False
        else:
            print(
                f'Error en la busqueda de la url: {url}, respuesta del servidor: {response.text}')
    except json.JSONDecodeError:
        print("La respuesta no es JSON o está vacía")

    return result