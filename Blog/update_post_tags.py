import sys
sys.path.append('/home/snparada/Spacionatural/Libraries/shopify_lib')
from blogs import ShopifyBlogs

def main():
    blog_id = '87871914153' #Aparece al final de la URL del blog cuando se gestiona el blog en el backoffice

    # Diccionario de tags a actualizar
    tags_to_update = {
        'Category_Consejos': 'Consejos',
        'Category_Recetas': 'Recetas',
        'Category_Destacados': 'Destacados',
        'Category_Propiedades': 'Propiedades',
        'Category_Cuidado Facial>Limpiadores Faciales': 'Consejos',
        'Category_Versus':'Versus'
        # Añade más según sea necesario
    }

    # Crear instancia de ShopifyBlogs
    shopify_blogs = ShopifyBlogs()

    # Obtener todos los posts del blog
    posts = shopify_blogs.read_all_blog_posts(blog_id)

    # Iterar sobre cada post y actualizar los tags
    for post in posts:
        current_tags = post['tags'].split(", ")
        new_tags = [tags_to_update.get(tag, tag) for tag in current_tags]
        shopify_blogs.update_blog_post_tags(post['id'], new_tags)

    print("Tags actualizados exitosamente.")

if __name__ == "__main__":
    main()