import requests

BASE_URL = "http://127.0.0.1:8000"

def get_products():
    response = requests.get(f"{BASE_URL}/products")
    return response.json()

def create_sale(sale_data):
    response = requests.post(f"{BASE_URL}/sales", json=sale_data)
    return response.json()
