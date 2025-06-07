import requests

BASE_URL = "http://127.0.0.1:8000"
quick_buttons = [None] * 9

def get_products():
    response = requests.get(f"{BASE_URL}/products")
    return response.json()

def get_product(product_id):
    response = requests.get(f"{BASE_URL}/products/{product_id}")
    return response.json()

def create_sale(sale_data):
    response = requests.post(f"{BASE_URL}/sales", json=sale_data)
    return response.json()

def add_product(product_data):
    response = requests.post(f"{BASE_URL}/products", json=product_data)
    try:
        return response.json()
    except Exception:
        print("Грешка при парсване на отговора!")
        print(response.text)
        return {}

def update_product(product_id, product_data):
    response = requests.put(f"{BASE_URL}/products/{product_id}", json=product_data)
    return response.json()

def save_quick_buttons(buttons_list):
    global quick_buttons
    quick_buttons = buttons_list
