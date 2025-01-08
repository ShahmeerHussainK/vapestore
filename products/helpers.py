import requests, os
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List
from urllib.parse import urlparse
from django.conf import settings
from django.core.files.storage import default_storage
from .models import *

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

def save_image(image_url, save_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    save_path = os.path.join(settings.MEDIA_ROOT, save_path)
    # Make a GET request to fetch the image
    response = requests.get(image_url, stream=True,headers=headers)
    response.raise_for_status()

    with open(save_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
    return save_path


def fetch_and_update_disposable_pods():
    @dataclass
    class Product:
        name: str
        price: str
        sale_price: str
        url: str
        image_urls: List[str]
        description: str
        brand: str

    base_url = 'https://vapebar.pk'
    products_list: List[Product] = []

    # Loop through the product pages

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    for i in range(1, 20):
            print(f"scrappig {i}")
            url = f"https://vapebar.pk/product-category/prefilled-disposable/page/{i}/"
            print(headers)
            # Send a GET request to the website
            response = requests.get(url,headers=headers)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content of the page
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all product containers
                products = soup.find_all('div', class_='box-text box-text-products text-center grid-style-2')

                # Loop through each product and extract the necessary details
                for product in products:
                    # Extract the product price
                    product_name = product.find('p', class_='name').text.strip()

                    # Extract the product URL
                    product_url = product.find('a', class_='woocommerce-LoopProduct-link')['href']

                    # Extract the original price (inside the <del> tag)
                    original_price_tag = product.find('del')
                    if original_price_tag:
                        soriginal_price = original_price_tag.find('span',class_='woocommerce-Price-amount amount').text.strip()
                        original_price=int(soriginal_price.replace('Rs', '').replace('₨', '').replace(',', '').strip())
                    else:
                        original_price = None  # No original price found

                    # Extract the sale price (inside the <ins> tag)
                    sale_price_tag = product.find('ins')
                    if sale_price_tag:
                        ssale_price = sale_price_tag.find('span', class_='woocommerce-Price-amount amount').text.strip()
                        sale_price=int(ssale_price.replace('Rs', '').replace('₨', '').replace(',', '').strip())
                    else:
                        sale_price = None

                    product_response = requests.get(product_url, headers=headers)
                    if product_response.status_code == 200:
                        product_soup = BeautifulSoup(product_response.content, 'html.parser')
                        # Extract the brand name from the text inside the 'a' tag
                        brand_tag = product_soup.find('div', class_='pwb-single-product-brands pwb-clearfix').find('a')
                        brand_name = brand_tag.text
                        # Extract the product description
                        description_div = product_soup.find('div', class_='panel entry-content')
                        product_description = str(description_div) if description_div else '<div>No description available</div>'

                    # Extract all image URLs
                        image_urls = []
                        images = product_soup.find_all('div', class_='woocommerce-product-gallery__image')
                        for img_tag in images:
                            img = img_tag.find('img')
                            if img:
                                # Get the largest available image URL (data-large_image or src)
                                img_url = img.get('data-large_image') or img.get('src')
                                if img_url:
                                    image_urls.append(img_url)

                        current_dir = os.getcwd()
                        save_directory = os.path.join(current_dir, 'media')

                        images = []

                        for image in image_urls:
                            parsed_url = urlparse(image)
                            image_filename = parsed_url.path.split('/')[-1]
                            save_path = os.path.join(save_directory, image_filename)
                            images.append(save_image(image, image_filename))
                        product_obj = Product(name=product_name, price=original_price, sale_price=sale_price,
                                              url=product_url, image_urls=image_urls, description=product_description,
                                              brand=brand_name)
                        products_list.append(product_obj)
                        print("image url: ",image_urls)
                        print("brand name: ",brand_name)
                    # Update or create DisposableVapes objects
                    category, _ = CategoryGroupings.objects.get_or_create(name="Pod Kits")
                    sub_category, _ = SubCategory.objects.get_or_create(name="disposable")

                    try:

                        product, created = DisposableVapes.objects.update_or_create(
                            sku=product_url,  # Unique identifier
                            defaults={
                                'name': product_obj.name,
                                'price': product_obj.price,
                                'rrp': product_obj.price,  # Assuming the RRP is the same as price, adjust if needed
                                'discounted_price': product_obj.sale_price,
                                # Set appropriate discounted price if available
                                'image_url': product_obj.image_urls[0] if product_obj.image_urls else 'No image',
                                'stock_level': 10,  # Set appropriate stock level if available
                                'in_stock': True,
                                'category': category,
                                'sub_category': sub_category,
                                'description': product_obj.description,
                                'brand': product_obj.brand  # Ensure this field is correct
                            }
                        )
                        print(product_obj.name,product_obj.price,product_obj.description)
                        print('********************************')

                        for img in images:
                            image_instance, created = Image.objects.get_or_create(
                                image=img)
                            product.images.add(image_instance)

                    except Exception as e:
                        print(f"An error occurred: {e}")


def fetch_and_update_e_liquids():
    @dataclass
    class Product:
        name: str
        price: str
        sale_price: str
        url: str
        image_urls: List[str]
        description: str
        brand: str

    base_url = 'https://vapebar.pk'
    products_list: List[Product] = []

    # Loop through the product pages

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    for i in range(16,24):
            print(f"scrappig {i}")
            url = f"https://vapebar.pk/product-category/nic-salt-e-liquid/page/{i}/"
            print(headers)
            # Send a GET request to the website
            response = requests.get(url,headers=headers)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content of the page
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all product containers
                products = soup.find_all('div', class_='box-text box-text-products text-center grid-style-2')

                # Loop through each product and extract the necessary details
                for product in products:

                    # Extract the product price
                    product_name = product.find('p', class_='name').text.strip()

                    # Extract the product URL
                    product_url = product.find('a', class_='woocommerce-LoopProduct-link')['href']

                    # Extract the original price (inside the <del> tag)
                    original_price_tag = product.find('del')
                    if original_price_tag:
                        soriginal_price = original_price_tag.find('span',class_='woocommerce-Price-amount amount').text.strip()
                        original_price=int(soriginal_price.replace('Rs', '').replace('₨', '').replace(',', '').strip())
                    else:
                        original_price = None  # No original price found

                    # Extract the sale price (inside the <ins> tag)
                    sale_price_tag = product.find('ins')
                    if sale_price_tag:
                        ssale_price = sale_price_tag.find('span', class_='woocommerce-Price-amount amount').text.strip()
                        sale_price=int(ssale_price.replace('Rs', '').replace('₨', '').replace(',', '').strip())
                    else:
                        sale_price = None
                    print(product_url)

                    product_response = requests.get(product_url, headers=headers)
                    if product_response.status_code == 200:
                        product_soup = BeautifulSoup(product_response.content, 'html.parser')
                        # Extract the brand name from the text inside the 'a' tag
                        brand_tag = product_soup.find('div', class_='pwb-single-product-brands pwb-clearfix').find('a')
                        brand_name = brand_tag.text

                        # Extract the product description
                        description_div = product_soup.find('div', class_='panel entry-content')
                        product_description = str(description_div) if description_div else '<div>No description available</div>'

                    # Extract all image URLs
                        image_urls = []
                        images = product_soup.find_all('div', class_='woocommerce-product-gallery__image')
                        for img_tag in images:
                            img = img_tag.find('img')
                            if img:
                                # Get the largest available image URL (data-large_image or src)
                                img_url = img.get('data-large_image') or img.get('src')
                                if img_url:
                                    image_urls.append(img_url)

                        current_dir = os.getcwd()
                        save_directory = os.path.join(current_dir, 'media')

                        images = []

                        for image in image_urls:
                            parsed_url = urlparse(image)
                            image_filename = parsed_url.path.split('/')[-1]
                            save_path = os.path.join(save_directory, image_filename)
                            images.append(save_image(image, image_filename))
                        product_obj = Product(name=product_name, price=original_price, sale_price=sale_price,
                                              url=product_url, image_urls=image_urls, description=product_description,
                                              brand=brand_name)
                        products_list.append(product_obj)
                        print("image url: ",image_urls)

                    # Update or create DisposableVapes objects
                    category, _ = CategoryGroupings.objects.get_or_create(name="Vape Juice")
                    sub_category, _ = SubCategory.objects.get_or_create(name="e-liquids")

                    try:
                        product, created = VapeJuice.objects.update_or_create(
                            sku=product_url,  # Unique identifier
                            defaults={
                                'name': product_obj.name,
                                'price': product_obj.price,
                                'rrp': product_obj.price,  # Assuming the RRP is the same as price, adjust if needed
                                'discounted_price': product_obj.sale_price,
                                # Set appropriate discounted price if available
                                'image_url': product_obj.image_urls[0] if product_obj.image_urls else 'No image',
                                'stock_level': 10,  # Set appropriate stock level if available
                                'in_stock': True,
                                'category': category,
                                'sub_category': sub_category,
                                'description': product_obj.description,
                                'brand': product_obj.brand  # Ensure this field is correct
                            }
                        )
                        print(product_obj.name,product_obj.price,product_obj.description)
                        print('********************************')

                        for img in images:
                            image_instance, created = Image.objects.get_or_create(
                                image=img)
                            product.images.add(image_instance)

                    except Exception as e:
                        print(f"An error occurred: {e}")






def fetch_and_update_pods():
    @dataclass
    class Product:
        name: str
        price: str
        sale_price: str
        url: str
        image_urls: List[str]
        description: str
        brand: str

    base_url = 'https://vapebar.pk'
    products_list: List[Product] = []

    # Loop through the product pages

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    for i in range(1,6):
            print(f"scrappig {i}")
            url = f"https://vapebar.pk/product-category/pod-system-devices/page/{i}/"
            print(headers)
            # Send a GET request to the website
            response = requests.get(url,headers=headers)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content of the page
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all product containers
                products = soup.find_all('div', class_='box-text box-text-products text-center grid-style-2')

                # Loop through each product and extract the necessary details
                for product in products:
                    # Extract the product price
                    product_name = product.find('p', class_='name').text.strip()

                    # Extract the product URL
                    product_url = product.find('a', class_='woocommerce-LoopProduct-link')['href']

                    # Extract the original price (inside the <del> tag)
                    original_price_tag = product.find('del')
                    if original_price_tag:
                        soriginal_price = original_price_tag.find('span',class_='woocommerce-Price-amount amount').text.strip()
                        original_price=int(soriginal_price.replace('Rs', '').replace('₨', '').replace(',', '').strip())
                    else:
                        continue  # No original price found

                    # Extract the sale price (inside the <ins> tag)
                    sale_price_tag = product.find('ins')
                    if sale_price_tag:
                        ssale_price = sale_price_tag.find('span', class_='woocommerce-Price-amount amount').text.strip()
                        sale_price=int(ssale_price.replace('Rs', '').replace('₨', '').replace(',', '').strip())
                    else:
                        sale_price = None

                    product_response = requests.get(product_url, headers=headers)
                    if product_response.status_code == 200:
                        product_soup = BeautifulSoup(product_response.content, 'html.parser')
                        # Extract the brand name from the text inside the 'a' tag
                        brand_tag = product_soup.find('div', class_='pwb-single-product-brands pwb-clearfix').find('a')
                        brand_name = brand_tag.text
                        # Extract the product description
                        description_div = product_soup.find('div', class_='panel entry-content')
                        product_description = str(description_div) if description_div else '<div>No description available</div>'

                    # Extract all image URLs
                        image_urls = []
                        images = product_soup.find_all('div', class_='woocommerce-product-gallery__image')
                        for img_tag in images:
                            img = img_tag.find('img')
                            if img:
                                # Get the largest available image URL (data-large_image or src)
                                img_url = img.get('data-large_image') or img.get('src')
                                if img_url:
                                    image_urls.append(img_url)

                        current_dir = os.getcwd()
                        save_directory = os.path.join(current_dir, 'media')

                        images = []

                        for image in image_urls:
                            parsed_url = urlparse(image)
                            image_filename = parsed_url.path.split('/')[-1]
                            save_path = os.path.join(save_directory, image_filename)
                            images.append(save_image(image, image_filename))
                        product_obj = Product(name=product_name, price=original_price, sale_price=sale_price,
                                              url=product_url, image_urls=image_urls, description=product_description,
                                              brand=brand_name)
                        products_list.append(product_obj)
                        print("image url: ",image_urls)

                    # Update or create DisposableVapes objects
                    category, _ = CategoryGroupings.objects.get_or_create(name="vaping_devices")
                    sub_category, _ = SubCategory.objects.get_or_create(name="pods")

                    try:
                        product, created = Pods.objects.update_or_create(
                            sku=product_url,  # Unique identifier
                            defaults={
                                'name': product_obj.name,
                                'price': product_obj.price,
                                'rrp': product_obj.price,  # Assuming the RRP is the same as price, adjust if needed
                                'discounted_price': product_obj.sale_price,
                                # Set appropriate discounted price if available
                                'image_url': product_obj.image_urls[0] if product_obj.image_urls else 'No image',
                                'stock_level': 10,  # Set appropriate stock level if available
                                'in_stock': True,
                                'category': category,
                                'sub_category': sub_category,
                                'description': product_obj.description,
                                'brand': product_obj.brand  # Ensure this field is correct
                            }
                        )
                        print(product_obj.name,product_obj.price,product_obj.description)
                        print('********************************')

                        for img in images:
                            image_instance, created = Image.objects.get_or_create(
                                image=img)
                            product.images.add(image_instance)

                    except Exception as e:
                        print(f"An error occurred: {e}")




def fetch_and_update_mods():
    @dataclass
    class Product:
        name: str
        price: str
        sale_price: str
        url: str
        image_urls: List[str]
        description: str
        brand: str

    base_url = 'https://vapebar.pk'
    products_list: List[Product] = []

    # Loop through the product pages

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    for i in range(1, 2):
            print(f"scrappig {i}")
            url = f"https://vapebar.pk/product-category/pod-system-devices/pod-mod/"
            print(headers)
            # Send a GET request to the website
            response = requests.get(url,headers=headers)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content of the page
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all product containers
                products = soup.find_all('div', class_='box-text box-text-products text-center grid-style-2')

                # Loop through each product and extract the necessary details
                for product in products:
                    # Extract the product name
                    brand_name = product.find('p', class_='category').text.strip()

                    # Extract the product price
                    product_name = product.find('p', class_='name').text.strip()

                    # Extract the product URL
                    product_url = product.find('a', class_='woocommerce-LoopProduct-link')['href']

                    # Extract the original price (inside the <del> tag)
                    original_price_tag = product.find('del')
                    if original_price_tag:
                        soriginal_price = original_price_tag.find('span',class_='woocommerce-Price-amount amount').text.strip()
                        original_price=int(soriginal_price.replace('Rs', '').replace('₨', '').replace(',', '').strip())
                    else:
                        original_price = None  # No original price found

                    # Extract the sale price (inside the <ins> tag)
                    sale_price_tag = product.find('ins')
                    if sale_price_tag:
                        ssale_price = sale_price_tag.find('span', class_='woocommerce-Price-amount amount').text.strip()
                        sale_price=int(ssale_price.replace('Rs', '').replace('₨', '').replace(',', '').strip())
                    else:
                        sale_price = None

                    product_response = requests.get(product_url, headers=headers)
                    if product_response.status_code == 200:
                        product_soup = BeautifulSoup(product_response.content, 'html.parser')

                        # Extract the product description
                        description_div = product_soup.find('div', class_='panel entry-content')
                        product_description = str(description_div) if description_div else '<div>No description available</div>'

                    # Extract all image URLs
                        image_urls = []
                        images = product_soup.find_all('div', class_='woocommerce-product-gallery__image')
                        for img_tag in images:
                            img = img_tag.find('img')
                            if img:
                                # Get the largest available image URL (data-large_image or src)
                                img_url = img.get('data-large_image') or img.get('src')
                                if img_url:
                                    image_urls.append(img_url)

                        current_dir = os.getcwd()
                        save_directory = os.path.join(current_dir, 'media')

                        images = []

                        for image in image_urls:
                            parsed_url = urlparse(image)
                            image_filename = parsed_url.path.split('/')[-1]
                            save_path = os.path.join(save_directory, image_filename)
                            images.append(save_image(image, image_filename))
                        product_obj = Product(name=product_name, price=original_price, sale_price=sale_price,
                                              url=product_url, image_urls=image_urls, description=product_description,
                                              brand=brand_name)
                        products_list.append(product_obj)
                        print("image url: ",image_urls)

                    # Update or create DisposableVapes objects
                    category, _ = CategoryGroupings.objects.get_or_create(name="Mods Category")
                    sub_category, _ = SubCategory.objects.get_or_create(name="mod")

                    try:
                        product, created = Mods.objects.update_or_create(
                            sku=product_url,  # Unique identifier
                            defaults={
                                'name': product_obj.name,
                                'price': product_obj.price,
                                'rrp': product_obj.price,  # Assuming the RRP is the same as price, adjust if needed
                                'discounted_price': product_obj.sale_price,
                                # Set appropriate discounted price if available
                                'image_url': product_obj.image_urls[0] if product_obj.image_urls else 'No image',
                                'stock_level': 10,  # Set appropriate stock level if available
                                'in_stock': True,
                                'category': category,
                                'sub_category': sub_category,
                                'description': product_obj.description,
                                'brand': product_obj.brand  # Ensure this field is correct
                            }
                        )
                        print(product_obj.name,product_obj.price,product_obj.description)
                        print('********************************')

                        for img in images:
                            image_instance, created = Image.objects.get_or_create(
                                image=img)
                            product.images.add(image_instance)

                    except Exception as e:
                        print(f"An error occurred: {e}")



def fetch_and_update_tanks():
    @dataclass
    class Product:
        name: str
        price: str
        sale_price: str
        url: str
        image_urls: List[str]
        description: str
        brand: str

    base_url = 'https://vapebar.pk'
    products_list: List[Product] = []

    # Loop through the product pages

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    for i in range(1, 2):
            print(f"scrappig {i}")
            url = f"https://vapebar.pk/product-category/tanks/"
            print(headers)
            # Send a GET request to the website
            response = requests.get(url,headers=headers)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content of the page
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all product containers
                products = soup.find_all('div', class_='box-text box-text-products text-center grid-style-2')

                # Loop through each product and extract the necessary details
                for product in products:
                    # Extract the product name
                    brand_name = product.find('p', class_='category').text.strip()

                    # Extract the product price
                    product_name = product.find('p', class_='name').text.strip()

                    # Extract the product URL
                    product_url = product.find('a', class_='woocommerce-LoopProduct-link')['href']

                    # Extract the original price (inside the <del> tag)
                    original_price_tag = product.find('del')
                    if original_price_tag:
                        soriginal_price = original_price_tag.find('span',class_='woocommerce-Price-amount amount').text.strip()
                        original_price=int(soriginal_price.replace('Rs', '').replace('₨', '').replace(',', '').strip())
                    else:
                        original_price = None  # No original price found

                    # Extract the sale price (inside the <ins> tag)
                    sale_price_tag = product.find('ins')
                    if sale_price_tag:
                        ssale_price = sale_price_tag.find('span', class_='woocommerce-Price-amount amount').text.strip()
                        sale_price=int(ssale_price.replace('Rs', '').replace('₨', '').replace(',', '').strip())
                    else:
                        sale_price = None

                    product_response = requests.get(product_url, headers=headers)
                    if product_response.status_code == 200:
                        product_soup = BeautifulSoup(product_response.content, 'html.parser')

                        # Extract the product description
                        description_div = product_soup.find('div', class_='panel entry-content')
                        product_description = str(description_div) if description_div else '<div>No description available</div>'

                    # Extract all image URLs
                        image_urls = []
                        images = product_soup.find_all('div', class_='woocommerce-product-gallery__image')
                        for img_tag in images:
                            img = img_tag.find('img')
                            if img:
                                # Get the largest available image URL (data-large_image or src)
                                img_url = img.get('data-large_image') or img.get('src')
                                if img_url:
                                    image_urls.append(img_url)

                        current_dir = os.getcwd()
                        save_directory = os.path.join(current_dir, 'media')

                        images = []

                        for image in image_urls:
                            parsed_url = urlparse(image)
                            image_filename = parsed_url.path.split('/')[-1]
                            save_path = os.path.join(save_directory, image_filename)
                            images.append(save_image(image, image_filename))
                        product_obj = Product(name=product_name, price=original_price, sale_price=sale_price,
                                              url=product_url, image_urls=image_urls, description=product_description,
                                              brand=brand_name)
                        products_list.append(product_obj)
                        print("image url: ",image_urls)

                    # Update or create DisposableVapes objects
                    category, _ = CategoryGroupings.objects.get_or_create(name="Vape Category")
                    sub_category, _ = SubCategory.objects.get_or_create(name="tank")

                    try:
                        product, created = Tanks.objects.update_or_create(
                            sku=product_url,  # Unique identifier
                            defaults={
                                'name': product_obj.name,
                                'price': product_obj.price,
                                'rrp': product_obj.price,  # Assuming the RRP is the same as price, adjust if needed
                                'discounted_price': product_obj.sale_price,
                                # Set appropriate discounted price if available
                                'image_url': product_obj.image_urls[0] if product_obj.image_urls else 'No image',
                                'stock_level': 10,  # Set appropriate stock level if available
                                'in_stock': True,
                                'category': category,
                                'sub_category': sub_category,
                                'description': product_obj.description,
                                'brand': product_obj.brand  # Ensure this field is correct
                            }
                        )
                        print(product_obj.name,product_obj.price,product_obj.description)
                        print('********************************')

                        for img in images:
                            image_instance, created = Image.objects.get_or_create(
                                image=img)
                            product.images.add(image_instance)

                    except Exception as e:
                        print(f"An error occurred: {e}")


def fetch_and_update_coils():
    @dataclass
    class Product:
        name: str
        price: str
        sale_price: str
        url: str
        image_urls: List[str]
        description: str
        brand: str

    base_url = 'https://vapebar.pk'
    products_list: List[Product] = []

    # Loop through the product pages

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    for i in range(1, 4):
            print(f"scrappig {i}")
            url = f"https://vapebar.pk/product-category/accessories/coils-pods/page/{i}/"
            print(headers)
            # Send a GET request to the website
            response = requests.get(url,headers=headers)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content of the page
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all product containers
                products = soup.find_all('div', class_='box-text box-text-products text-center grid-style-2')

                # Loop through each product and extract the necessary details
                for product in products:
                    # Extract the product name
                    brand_name = product.find('p', class_='category').text.strip()

                    # Extract the product price
                    product_name = product.find('p', class_='name').text.strip()

                    # Extract the product URL
                    product_url = product.find('a', class_='woocommerce-LoopProduct-link')['href']

                    # Extract the original price (inside the <del> tag)
                    original_price_tag = product.find('del')
                    if original_price_tag:
                        soriginal_price = original_price_tag.find('span',class_='woocommerce-Price-amount amount').text.strip()
                        original_price=int(soriginal_price.replace('Rs', '').replace('₨', '').replace(',', '').strip())
                    else:
                        original_price = None  # No original price found

                    # Extract the sale price (inside the <ins> tag)
                    sale_price_tag = product.find('ins')
                    if sale_price_tag:
                        ssale_price = sale_price_tag.find('span', class_='woocommerce-Price-amount amount').text.strip()
                        sale_price=int(ssale_price.replace('Rs', '').replace('₨', '').replace(',', '').strip())
                    else:
                        sale_price = None

                    product_response = requests.get(product_url, headers=headers)
                    if product_response.status_code == 200:
                        product_soup = BeautifulSoup(product_response.content, 'html.parser')

                        # Extract the product description
                        description_div = product_soup.find('div', class_='panel entry-content')
                        product_description = str(description_div) if description_div else '<div>No description available</div>'

                    # Extract all image URLs
                        image_urls = []
                        images = product_soup.find_all('div', class_='woocommerce-product-gallery__image')
                        for img_tag in images:
                            img = img_tag.find('img')
                            if img:
                                # Get the largest available image URL (data-large_image or src)
                                img_url = img.get('data-large_image') or img.get('src')
                                if img_url:
                                    image_urls.append(img_url)

                        current_dir = os.getcwd()
                        save_directory = os.path.join(current_dir, 'media')

                        images = []

                        for image in image_urls:
                            parsed_url = urlparse(image)
                            image_filename = parsed_url.path.split('/')[-1]
                            save_path = os.path.join(save_directory, image_filename)
                            images.append(save_image(image, image_filename))
                        product_obj = Product(name=product_name, price=original_price, sale_price=sale_price,
                                              url=product_url, image_urls=image_urls, description=product_description,
                                              brand=brand_name)
                        products_list.append(product_obj)
                        print("image url: ",image_urls)

                    # Update or create DisposableVapes objects
                    category, _ = CategoryGroupings.objects.get_or_create(name="Vape Category")
                    sub_category, _ = SubCategory.objects.get_or_create(name="coil")

                    try:
                        product, created = PreBuiltCoils.objects.update_or_create(
                            sku=product_url,  # Unique identifier
                            defaults={
                                'name': product_obj.name,
                                'price': product_obj.price,
                                'rrp': product_obj.price,  # Assuming the RRP is the same as price, adjust if needed
                                'discounted_price': product_obj.sale_price,
                                # Set appropriate discounted price if available
                                'image_url': product_obj.image_urls[0] if product_obj.image_urls else 'No image',
                                'stock_level': 10,  # Set appropriate stock level if available
                                'in_stock': True,
                                'category': category,
                                'sub_category': sub_category,
                                'description': product_obj.description,
                                'brand': product_obj.brand  # Ensure this field is correct
                            }
                        )
                        print(product_obj.name,product_obj.price,product_obj.description)
                        print('********************************')

                        for img in images:
                            image_instance, created = Image.objects.get_or_create(
                                image=img)
                            product.images.add(image_instance)

                    except Exception as e:
                        print(f"An error occurred: {e}")

def fetch_and_update_accessories():
    @dataclass
    class Product:
        name: str
        price: str
        sale_price: str
        url: str
        image_urls: List[str]
        description: str
        brand: str

    base_url = 'https://vapebar.pk'
    products_list: List[Product] = []

    # Loop through the product pages

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    for i in range(1, 4):
            print(f"scrappig {i}")
            url = f"https://vapebar.pk/product-category/accessories/page/{i}/"
            print(headers)
            # Send a GET request to the website
            response = requests.get(url,headers=headers)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content of the page
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all product containers
                products = soup.find_all('div', class_='box-text box-text-products text-center grid-style-2')

                # Loop through each product and extract the necessary details
                for product in products:
                    # Extract the product name
                    brand_name = product.find('p', class_='category').text.strip()

                    # Extract the product price
                    product_name = product.find('p', class_='name').text.strip()

                    # Extract the product URL
                    product_url = product.find('a', class_='woocommerce-LoopProduct-link')['href']

                    # Extract the original price (inside the <del> tag)
                    original_price_tag = product.find('del')
                    if original_price_tag:
                        soriginal_price = original_price_tag.find('span',class_='woocommerce-Price-amount amount').text.strip()
                        original_price=int(soriginal_price.replace('Rs', '').replace('₨', '').replace(',', '').strip())
                    else:
                        original_price = None  # No original price found

                    # Extract the sale price (inside the <ins> tag)
                    sale_price_tag = product.find('ins')
                    if sale_price_tag:
                        ssale_price = sale_price_tag.find('span', class_='woocommerce-Price-amount amount').text.strip()
                        sale_price=int(ssale_price.replace('Rs', '').replace('₨', '').replace(',', '').strip())
                    else:
                        sale_price = None

                    product_response = requests.get(product_url, headers=headers)
                    if product_response.status_code == 200:
                        product_soup = BeautifulSoup(product_response.content, 'html.parser')

                        # Extract the product description
                        description_div = product_soup.find('div', class_='panel entry-content')
                        product_description = str(description_div) if description_div else '<div>No description available</div>'

                    # Extract all image URLs
                        image_urls = []
                        images = product_soup.find_all('div', class_='woocommerce-product-gallery__image')
                        for img_tag in images:
                            img = img_tag.find('img')
                            if img:
                                # Get the largest available image URL (data-large_image or src)
                                img_url = img.get('data-large_image') or img.get('src')
                                if img_url:
                                    image_urls.append(img_url)

                        current_dir = os.getcwd()
                        save_directory = os.path.join(current_dir, 'media')

                        images = []

                        for image in image_urls:
                            parsed_url = urlparse(image)
                            image_filename = parsed_url.path.split('/')[-1]
                            save_path = os.path.join(save_directory, image_filename)
                            images.append(save_image(image, image_filename))
                        product_obj = Product(name=product_name, price=original_price, sale_price=sale_price,
                                              url=product_url, image_urls=image_urls, description=product_description,
                                              brand=brand_name)
                        products_list.append(product_obj)
                        print("image url: ",image_urls)

                    # Update or create DisposableVapes objects
                    category, _ = CategoryGroupings.objects.get_or_create(name="Vape Category")
                    sub_category, _ = SubCategory.objects.get_or_create(name="accessory")

                    try:
                        product, created = Accessories.objects.update_or_create(
                            sku=product_url,  # Unique identifier
                            defaults={
                                'name': product_obj.name,
                                'price': product_obj.price,
                                'rrp': product_obj.price,  # Assuming the RRP is the same as price, adjust if needed
                                'discounted_price': product_obj.sale_price,
                                # Set appropriate discounted price if available
                                'image_url': product_obj.image_urls[0] if product_obj.image_urls else 'No image',
                                'stock_level': 10,  # Set appropriate stock level if available
                                'in_stock': True,
                                'category': category,
                                'sub_category': sub_category,
                                'description': product_obj.description,
                                'brand': product_obj.brand  # Ensure this field is correct
                            }
                        )
                        print(product_obj.name,product_obj.price,product_obj.description)
                        print('********************************')

                        for img in images:
                            image_instance, created = Image.objects.get_or_create(
                                image=img)
                            product.images.add(image_instance)

                    except Exception as e:
                        print(f"An error occurred: {e}")

