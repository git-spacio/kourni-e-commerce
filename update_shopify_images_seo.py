import sys

sys.path.append('/home/snparada/Spacionatural/Libraries')
from shopify_lib.products import ShopifyProducts
from shopify_lib.collections import ShopifyCollections


obj = ShopifyProducts()
product_images = obj.read_all_images()

for product_image in product_images:
    if product_image['alt'] == '' or product_image['alt'] == None:
        break
        new_alt = 'new_alt_text'
        # ...
        # get alt from GPT and set new_alt
        # ...
        obj.update_image_seo(product_image['product_id'], product_image['id'], new_alt)

obj = ShopifyCollections()
collection_images = obj.read_all_images()

for collection_image in collection_images:
    if collection_image['alt'] == 'new_text':
        print(collection_image['collection_id'])
    if collection_image['alt'] == '' or collection_image['alt'] == None:
        break
        new_alt = 'new_alt_text'
        # ...
        # get alt from GPT and set new_alt
        # ...
        obj.update_image_seo(collection_image['collection_id'], new_alt)