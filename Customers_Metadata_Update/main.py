from flask import Flask, request, jsonify
from Libraries.shopify_lib.customers import ShopifyCustomers
import os

app = Flask(__name__)

# Inicializar la clase ShopifyCustomers
shopify_customers = ShopifyCustomers()

@app.route('/webhook/order-create', methods=['POST'])
def order_create_webhook():
    webhook_data = request.json

    if 'customer' not in webhook_data:
        return jsonify({'status': 'no customer found'}), 400

    customer_id = webhook_data['customer']['id']
    note_attributes = webhook_data.get('note_attributes', [])
    
    # Extraer información relevante
    fields_to_update = {
        'RUT': next((attr['value'] for attr in note_attributes if attr['name'] == 'RUT'), None),
        'razon_social': next((attr['value'] for attr in note_attributes if attr['name'] == 'Razón Social'), None),
        'giro': next((attr['value'] for attr in note_attributes if attr['name'] == 'Giro'), None)
    }

    # Actualizar metacampos del cliente
    for key, value in fields_to_update.items():
        if value:
            shopify_customers.update_customer_metafield(customer_id, key, value)

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
