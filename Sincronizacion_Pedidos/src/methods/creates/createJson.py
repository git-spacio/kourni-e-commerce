
import datetime

def create_json_customer(customer_data):
    json_data = {
        "name": "",
        "legalName": "",
        "VATId": "",
        "activityName": "",
        "account": None,
        "dealer": None,
        "term": {"termId": ""},
        "priceList": None,
        "customerCategory": None,
        "salesman": {"salesmanId": 24},
        "address": "",
        "city": "",
        "county": "",
        "zipCode": "",
        "state": "",
        "country": "Chile",
        "foreigner": False,
        "addressBilling": "",
        "cityBilling": "",
        "countyBilling": "",
        "zipCodeBilling": "",
        "stateBilling": "",
        "countryBilling": "Chile",
        "phone1": "",
        "phone2": "",
        "fax": "",
        "DTEEmail": "",
        "email": "",
        "webPage": "",
        "schedule": "",
        "creditLimit": 0,
        "collectWeekday": 0,
        "daysToExpiration": 0,
        "discount": 0,
        "discountIsAdditive": False,
        "blocked": False,
        "blockedIfOverCreditLimit": False,
        "blockedIfOverdueInvoices": False,
        "defaultQuoteHeader": "",
        "defaultQuoteFooter": "",
        "comercioNetBranchCode": "",
        "comercioNetCode": "",
        "notes": "",
        "createdBy": {"userId": "07"},
        "customFields": {}
    }

    # sustituir la key 'name'
    json_data['name'] = customer_data['customer']['firstname'] + \
        " " + customer_data['customer']['lastname']
    json_data['VATId'] = customer_data['customer']['dni']

    if customer_data['customer']['payment'] == 'Payku':
        json_data['term']['termId'] = '18'
    elif customer_data['customer']['payment'] == 'Pagos por transferencia bancaria':
        json_data['term']['termId'] = '12'
    elif customer_data['customer']['payment'] == 'Klap Checkout (2.0.0)':
        json_data['term']['termId'] = '19'
    elif customer_data['customer']['payment'] == 'Webpay Plus':
        json_data['term']['termId'] = '1B'

    json_data['address'] = customer_data['customer']['address']
    json_data['addressBilling'] = customer_data['customer']['address']
    json_data['state'] = customer_data['customer']['region']
    json_data['stateBilling'] = customer_data['customer']['region']
    json_data['county'] = customer_data['customer']['comuna']
    json_data['countyBilling'] = customer_data['customer']['comuna']
    json_data['cityBilling'] = customer_data['customer']['comuna']
    json_data['email'] = customer_data['customer']['email']
    json_data['phone1'] = customer_data['customer']['phone']

    return json_data

def create_json_address(address_data):
    json_data = {
        "description": "direccion cargada desde el API",
        "address": "",
        "county": "",
        "zipCode": "",
        "city": "",
        "state": "",
        "country": "Chile",
        "notes": ""
    }

    json_data['address'] = address_data['address']['direccion']
    json_data['county'] = address_data['address']['comuna']
    json_data['state'] = address_data['address']['region']

    return json_data


def create_json_order(order_data):

    json_data = {
        "customer": {
            "customerId": ""
        },
        "contact": None,
        "salesman": {
            "salesmanId": 24
        },
        "dealer": None,
        "carrier": None,
        "priceList": None,
        "term": {
            "termId": "12"
        },
        "branch":  {
            "branchId": 1
        },
        "dueDate": "",
        "issuedDate": "",
        "nullDoc": False,
        "locked": False,
        "approved": False,
        "approvedBy": None,
        "purchaseOrderNumber": "",
        "deliveryAddress": {
            "addressId": ""
        },
        "deliveryCost": 0,
        "deliveryNotes": "Sin comentarios",
        "bypassCreditLimit": False,
        "source": {
            "code": "PS",
            "description": "PrestaShop"
        },
        "sourceOrderId": None,
        "amountPaid": 0,
        "amountPaidCurrencyCode": None,
        "invoiceDocType": None,
        "notes": "Pedido cargado desde el api",
        "createdBy": {
            "userId": "07"
        },
        "modifiedBy": None,
        "modifiedAt": None,
        "customFields": {},
        "items": [


        ]
    }

    for row in order_data['order']['carts_rows']:
        item = {
            "product": {
                "productId": int(row['productId'])

            },
            "quantity": int(row['quantity']),
            "originalUnitPrice": row['unitPrice'],
            "unitPrice": row['unitPrice']
        }

        json_data['items'].append(item)

    if (order_data['order']['total_shipping_tax_incl'] != 0.0):
        order_data['order']['total_shipping_tax_incl'] /= 1.19
        item = {
            "product": {
                "productId": 17253,
                "description": "SPACIO DELIVERY"
            },
            "itemDescription": "SPACIO DELIVERY",
            "quantity": 1,
            "originalUnitPrice": order_data['order']['total_shipping_tax_incl'],
            "unitPrice": order_data['order']['total_shipping_tax_incl']
        }
        json_data['items'].append(item)

    json_data['customer']['customerId'] = order_data['order']['customerId']
    if order_data['order']['payment'] == 'Payku':
        json_data['term']['termId'] = '18'
    elif order_data['order']['payment'] == 'Pagos por transferencia bancaria':
        json_data['term']['termId'] = '12'
    elif order_data['order']['payment'] == 'Klap Checkout (2.0.0)':
        json_data['term']['termId'] = '19'
    elif order_data['order']['payment'] == 'Webpay Plus':
        json_data['term']['termId'] = '1B'
    json_data['purchaseOrderNumber'] = order_data['order']['reference']
    json_data['deliveryAddress']['addressId'] = order_data['order']['addressId']
    # Obtener la fecha y hora actual
    now = datetime.datetime.now()
    formatted_now = now.strftime("%Y-%m-%dT%H:%M:%S")
    json_data['dueDate'] = formatted_now
    json_data['issuedDate'] = formatted_now
    # print(json_data)
    return json_data
