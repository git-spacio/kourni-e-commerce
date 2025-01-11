import sys, json
sys.path.append('/home/snparada/Spacionatural/E-Commerce/')
sys.path.append('/home/snparada/Spacionatural/Libraries')

from shopify_lib.connection import Connection
from shopify_lib.creds.config import SHOPIFY_SHOP_URL, SHOPIFY_PASSWORD
from shopify_lib.orders import ShopifyOrders
# from data.data import Data


conn = Connection(SHOPIFY_SHOP_URL, SHOPIFY_PASSWORD)

# Crear la instancia de Orders y obtener la última orden
orders = ShopifyOrders(conn)
last_order = orders.read_last_order()
path = '/home/snparada/Spacionatural/Libraries/data/shopify/last_order.json'

# data = Data(conn)
# data.export_data_to_json(last_order,path)


