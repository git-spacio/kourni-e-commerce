from Sincronizacion_Pedidos.src.urls.urlApiPrestashop import prestashop_url
from Sincronizacion_Pedidos.src.methods.getPrestashop import get_prestashop_data, get_orders
from Sincronizacion_Pedidos.src.methods.prints.print import print_order_info

def process_orders():
    orders = get_orders()
    if orders is not None:
        for order in orders:
            order_id = order['id']
            order_url = f'{prestashop_url}/orders/{order_id}?output_format=JSON'
            order_details = get_prestashop_data(order_url)
            if order_details is not None:
                # Llamada a la función aquí
                print_order_info(order_details['order'])