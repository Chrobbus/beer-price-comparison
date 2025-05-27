
import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Beer Price Comparison", page_icon="🍺", layout="centered")

st.title("🍺 Víking Lite Price Comparison (500ml cans)")
st.caption("Real-time comparison from Smárikid, Heimkaup, and Nýja Vínbúðin")

@st.cache_data
def get_smarikid_price():
    try:
        url = "https://smarikid.is/api/products"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        data = response.json()
        product_list = data.get("products", [])

        for product in product_list:
            if "Víking Lite 500ml" in product.get("name", ""):
                base_price = product["base_price"]
                sale_price = product.get("sale_price", base_price)
                unit_price = round(sale_price / 12)
                return f"{sale_price} kr", f"{unit_price} kr"
    except:
        return "-", "-"
    return "-", "-"

@st.cache_data
def get_heimkaup_price():
    try:
        url = "https://www.heimkaup.is/viking-lite-0-5l-10pk-dos-afhendist-kaldur"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        price_tag = soup.find("span", class_="Price")
        unit_price_tag = soup.find("span", class_="Price-unit")
        price = price_tag.text.strip() if price_tag else "-"
        unit_price = unit_price_tag.text.strip() if unit_price_tag else "-"
        return price, unit_price
    except:
        return "-", "-"

@st.cache_data
def get_nyjavinbudin_price():
    try:
        url = "https://nyjavinbudin.is/vara/viking-lite/"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        discount_tag = soup.find("p", class_="price").find("ins")
        price = discount_tag.text.strip() if discount_tag else "-"
        return price
    except:
        return "-"

# Fetch data
smarikid_total, smarikid_unit = get_smarikid_price()
heimkaup_total, heimkaup_unit = get_heimkaup_price()
nyjavinbudin_unit = get_nyjavinbudin_price()

# Calculate total for Nýja Vínbúðin (12 cans at unit price)
try:
    numeric = int(nyjavinbudin_unit.replace("kr.", "").replace("kr", "").replace(".", "").strip())
    nyjavinbudin_total = f"{numeric * 12} kr"
except:
    nyjavinbudin_total = "-"

# Display updated results
st.markdown("### 📊 Current Prices")
st.table({
    "Store": ["Smárikid (12-pack)", "Heimkaup (12-pack)", "Nýja Vínbúðin (12 cans)"],
    "Total Price": [smarikid_total, heimkaup_total, nyjavinbudin_total],
    "Unit Price": [smarikid_unit, heimkaup_unit, nyjavinbudin_unit]
})

st.markdown("---")
st.caption("Made by Daniel using Python & Streamlit 💻")
