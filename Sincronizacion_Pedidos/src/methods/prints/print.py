

from Sincronizacion_Pedidos.src.urls.urlLaudus import SALES_ORDERS, ORDERS_LIST, CUSTOMERS_LIST, SALES_CUSTOMERS
from Sincronizacion_Pedidos.src.methods.creates.createList import create_list_id_products_prestashop, clean_list_id_products_prestashop, create_order_data
from Sincronizacion_Pedidos.src.urls.urlApiPrestashop import prestashop_url
from Sincronizacion_Pedidos.src.token.Laudus.headerAutorization import headers_authorization
from Sincronizacion_Pedidos.src.methods.postLaudus import post_laudus, post_laudus_v2
from Sincronizacion_Pedidos.src.methods.getLaudus import get_laudus, get_current_laudus_token, get_product_id_laudus
from Sincronizacion_Pedidos.src.methods.getPrestashop import get_prestashop_data, get_cart
from Sincronizacion_Pedidos.src.methods.creates.createJson import create_json_customer, create_json_order, create_json_address
from Sincronizacion_Pedidos.src.helpers.rut import format_rut, check_rut
from Sincronizacion_Pedidos.src.helpers.DataBase.query import execute_query

def print_order_info(order):

    if order['current_state'] == '2' or order['current_state'] == '10':
        customer_id = order['id_customer']
        customer_url = f'{prestashop_url}/customers/{customer_id}?output_format=JSON'
        customer_data = get_prestashop_data(customer_url)
        print(f"Order ID: {order['id']}, Customer ID: {customer_id}, Payment Method: {'Tarjeta' if order['current_state'] == '2' else 'Transferencia'}, Reference: {order['reference']}, Tipo de Pago: {order['payment']}, Cart ID: {order['id_cart']}")
        print(
            f"Customer firstname: {customer_data['customer']['firstname']}, lastname: {customer_data['customer']['lastname']}, email: {customer_data['customer']['email']}")
        # Llamada a la función para obtener el token
        token = get_current_laudus_token()
        # print(f"Token: {token}")
        headers_auth = headers_authorization(token)
        check_order = post_laudus(
            ORDERS_LIST,
            headers_auth,
            {
                "options": {
                    "offset": 0,
                    "limit": 0
                },
                "fields": [
                    "salesOrderId"
                ],
                "filterBy": [
                    {
                        "field": "purchaseOrderNumber",
                        "operator": "=",
                        "value": order['reference']
                    }
                ]
            }
        )

        if (check_order['status'] == False):

            if order['id_address_delivery'] == order['id_address_invoice']:
                address_id = order['id_address_delivery']
                address_url = f'{prestashop_url}/addresses/{address_id}?output_format=JSON'
                address_data = get_prestashop_data(address_url)

                
                if len(address_data['address']['address1']) > 79:
                    address_data['address']['address1'] = address_data['address']['address1'][:79]

                print(
                    f"Delivery and Invoice Address: firstname: {address_data['address']['firstname']}, lastname: {address_data['address']['lastname']}, address1: {address_data['address']['address1']}, address2: {address_data['address']['address2']}, phone_mobile: {address_data['address']['phone_mobile']}, dni: {address_data['address']['dni']}")
                

                country_id = address_data['address']['id_country']
                country_url = f'{prestashop_url}/countries/{country_id}?output_format=JSON'
                country_data = get_prestashop_data(country_url)
                print(f"Región: {country_data['country']['name']}")

                state_id = address_data['address']['id_state']
                state_url = f'{prestashop_url}/states/{state_id}?output_format=JSON'
                state_data = get_prestashop_data(state_url)
                print(f"Comuna: {state_data['state']['name']}")

                total_shipping_tax_incl = order['total_shipping_tax_incl']
                print(f"flete del pedido {total_shipping_tax_incl}")

                rut_formateado = format_rut(address_data['address']['dni'])
                

                if check_rut(rut_formateado):
                    print(f"El rut {rut_formateado} es valido")

                    check_user = post_laudus(
                        CUSTOMERS_LIST,
                        headers_auth,
                        {
                            "options": {
                                "offset": 0,
                                "limit": 0
                            },
                            "fields": [
                                "customerId"
                            ],
                            "filterBy": [
                                {
                                    "field": "VATId",
                                    "operator": "=",
                                    "value": rut_formateado
                                }
                            ]
                        }
                    )

                    print (f"El check user es: {check_user}")

                    region = country_data['country']['name']
                    if len(country_data['country']['name']) > 15:
                        region = region[:15]
                    if check_user['status'] == False:

                        customer_data = {
                            'customer': {
                                'firstname': customer_data['customer']['firstname'],
                                'lastname': customer_data['customer']['lastname'],
                                'dni': format_rut(address_data['address']['dni']),
                                'payment': order['payment'],
                                'address': address_data['address']['address1'] + ' ' + address_data['address']['address2'],
                                'region': region,
                                'comuna': state_data['state']['name'],
                                'email': customer_data['customer']['email'],
                                'phone': address_data['address']['phone_mobile']
                            }
                        }
                        json_customer = create_json_customer(customer_data)
                        print(json_customer)
                        create_user = post_laudus(
                            SALES_CUSTOMERS,
                            headers_auth,
                            json_customer
                        )

                        print(create_user)

                        if create_user['status'] == True:

                            print(f"El usuario creado con exito")
                            address_data = {
                                'address': {
                                    'direccion': address_data['address']['address1'] + ' ' + address_data['address']['address2'],
                                    'comuna': state_data['state']['name'],
                                    'region': region
                                }
                            }

                            json_address_user = create_json_address(
                                address_data)

                            create_address = post_laudus_v2(
                                f'https://api.laudus.cl/sales/customers/{create_user["response"]["customerId"]}/addresses',
                                headers_auth,
                                json_address_user
                            )

                            print(create_address)

                            print(f"Direccion creada con exito")

                            new_json_cart = {
                                'cart_rows':[]
                            }

                            query = f"SELECT * FROM ps_order_detail WHERE id_order = {order['id']}"
                            result = execute_query(query)
                            for row in result:
                                new_row = {
                                    'id_product': str(row[5]), 
                                    'id_product_attribute': str(row[6]), 
                                    'id_address_delivery': str(address_id),  
                                    'id_customization': '0',         
                                    'quantity': str(row[9])
                                
                                }
                                new_json_cart['cart_rows'].append(new_row)

                            # Si deseas ver tu JSON:
                            print(new_json_cart)

                            carts_rows = create_list_id_products_prestashop(
                                new_json_cart)
                            # print(carts_rows)

                            clean_carts_rows = clean_list_id_products_prestashop(
                                carts_rows)
                            # print(clean_carts_rows)

                            json_product_id = get_product_id_laudus(
                                clean_carts_rows, headers_auth)
                            # print(json_product_id)

                            order_data = create_order_data(
                                create_user["response"]["customerId"],
                                order['payment'],
                                order['reference'],
                                create_address['response']['addressId'],
                                json_product_id,
                                float(total_shipping_tax_incl)
                            )

                            print(order_data)

                            json_order_data = create_json_order(order_data)

                            create_order = post_laudus(
                                SALES_ORDERS,
                                headers_auth,
                                json_order_data
                            )

                            if (create_order['status'] == True):
                                print(f'pedido creado con exito')
                            else:
                                print(
                                    f'Hubo un error al crear el pedido: {json_order_data}')

                        else:
                            print(f"Revisar error al crear el usuario en laudus")

                    elif check_user['status'] == True:

                        check_user_address = get_laudus(
                            f'https://api.laudus.cl/sales/customers/{check_user["response"][0]["customerId"]}/addresses',
                            headers_auth
                        )
                        print(check_user_address)

                        if check_user_address['status'] == True:

                            # json_cart = get_cart(order['id_cart'])
                            # print(json_cart)
                            

                            new_json_cart = {
                                'cart_rows':[]
                            }

                            query = f"SELECT * FROM ps_order_detail WHERE id_order = {order['id']}"
                            result = execute_query(query)
                            for row in result:
                                new_row = {
                                    'id_product': str(row[5]), 
                                    'id_product_attribute': str(row[6]), 
                                    'id_address_delivery': str(address_id),  
                                    'id_customization': '0',         
                                    'quantity': str(row[9])
                                
                                }
                                new_json_cart['cart_rows'].append(new_row)

                            # Si deseas ver tu JSON:
                            print(new_json_cart)

                            # if 'associations' not in json_cart:
                                                               
                            #     query = f"SELECT * FROM ps_order_detail WHERE id_order = {order['id']}"
                            #     result = execute_query(query)
                                
                            #     for row in result:
                            #         query = f"""insert into `spaciona_prestashopv1.7.7.8`.ps_cart_product(
                            #             id_cart,id_product,id_address_delivery,id_shop,id_product_attribute,
                            #             id_customization,quantity,date_add
                            #         )
                            #         values(
                            #             {order['id_cart']},{row[5]},{address_id},1,{row[6]},0,{row[9]},now()
                            #         )
                            #         """                                  
                            #         execute_query(query)
                                    

                            carts_rows = create_list_id_products_prestashop(
                                new_json_cart)
                            # print(carts_rows)

                            clean_carts_rows = clean_list_id_products_prestashop(
                                carts_rows)
                            # print(clean_carts_rows)

                            json_product_id = get_product_id_laudus(
                                clean_carts_rows, headers_auth)
                            # print(json_product_id)

                            order_data = create_order_data(
                                check_user["response"][0]["customerId"],
                                order['payment'],
                                order['reference'],
                                check_user_address['response'][0]['addressId'],
                                json_product_id,
                                float(total_shipping_tax_incl)
                            )
                            print(order_data)

                            json_order_data = create_json_order(order_data)

                            create_order = post_laudus(
                                SALES_ORDERS,
                                headers_auth,
                                json_order_data
                            )

                            if (create_order['status'] == True):
                                print(f'pedido creado con exito')
                            else:
                                print(
                                    f'Hubo un error al crear el pedido: {json_order_data}')

                        elif check_user_address['status'] == False:
                            address_data = {
                                'address': {
                                    'direccion': address_data['address']['address1'] + ' ' + address_data['address']['address2'],
                                    'comuna': state_data['state']['name'],
                                    'region': region
                                }
                            }
                            # print(address_data)

                            json_address_user = create_json_address(
                                address_data)
                            # print(json_address_user)

                            # print(f'https://api.laudus.cl/sales/customers/{check_user["customerId"]}/addresses')

                            create_address = post_laudus_v2(
                                f'https://api.laudus.cl/sales/customers/{check_user["response"][0]["customerId"]}/addresses',
                                headers_auth,
                                json_address_user
                            )
                            print(create_address)

                            print(f"Direccion creada con exito")

                            # json_cart = get_cart(order['id_cart'])
                            # print(json_cart)

                            new_json_cart = {
                                'cart_rows':[]
                            }

                            query = f"SELECT * FROM ps_order_detail WHERE id_order = {order['id']}"
                            result = execute_query(query)
                            for row in result:
                                new_row = {
                                    'id_product': str(row[5]), 
                                    'id_product_attribute': str(row[6]), 
                                    'id_address_delivery': str(address_id),  
                                    'id_customization': '0',         
                                    'quantity': str(row[9])
                                
                                }
                                new_json_cart['cart_rows'].append(new_row)

                            # Si deseas ver tu JSON:
                            print(new_json_cart)                            

                            # if 'associations' not in json_cart:                                                              
                            #     query = f"SELECT * FROM ps_order_detail WHERE id_order = {order['id']}"
                            #     result = execute_query(query)
                            
                            #     for row in result:
                            #         query = f"""insert into `spaciona_prestashopv1.7.7.8`.ps_cart_product(
                            #             id_cart,id_product,id_address_delivery,id_shop,id_product_attribute,
                            #             id_customization,quantity,date_add
                            #         )
                            #         values(
                            #             {order['id_cart']},{row[5]},{address_id},1,{row[6]},0,{row[9]},now()
                            #         )
                            #         """
                            #         execute_query(query)

                            carts_rows = create_list_id_products_prestashop(
                                new_json_cart)
                            # print(carts_rows)

                            clean_carts_rows = clean_list_id_products_prestashop(
                                carts_rows)
                            # print(clean_carts_rows)

                            json_product_id = get_product_id_laudus(
                                clean_carts_rows, headers_auth)
                            # print(json_product_id)

                            order_data = create_order_data(
                                check_user["response"][0]["customerId"],
                                order['payment'],
                                order['reference'],
                                create_address['response']['addressId'],
                                json_product_id,
                                float(total_shipping_tax_incl)
                            )
                            print(order_data)

                            json_order_data = create_json_order(order_data)

                            create_order = post_laudus(
                                SALES_ORDERS,
                                headers_auth,
                                json_order_data
                            )

                            if (create_order['status'] == True):
                                print(f'pedido creado con exito')
                            else:
                                print(
                                    f'Hubo un error al crear el pedido: {json_order_data}')

                        print(f"El usuario esta creado")

                    else:
                        print(f"Revisar error")

                    # parametros_lista = {
                    #     "options": {
                    #         "offset": 0,
                    #         "limit": 0
                    #     },
                    #     "fields": [
                    #         "customerId"
                    #     ],
                    #     "filterBy": [
                    #         {
                    #             "field": "VATId",
                    #             "operator": "=",
                    #             "value": "22.318.327-1"
                    #         }
                    #     ]
                    # }

                else:
                    print(f"El rut no es valido")

            else:
                address_id = order['id_address_invoice']
                address_url = f'{prestashop_url}/addresses/{address_id}?output_format=JSON'
                address_data = get_prestashop_data(address_url)
                print(
                    f"Delivery and Invoice Address: firstname: {address_data['address']['firstname']}, lastname: {address_data['address']['lastname']}, address1: {address_data['address']['address1']}, address2: {address_data['address']['address2']}, phone_mobile: {address_data['address']['phone_mobile']}, dni: {address_data['address']['dni']}")
        else:
            print(f"pedido {order['id']} ya fué agregado al laudus")            
    else:
        print(f"las direcciones del pedido {order['id']} son distintas")
            
    print ("-----------------------------------------------------------------")  
