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

@st.cache_data
def get_vinbudin_price():
    try:
        url = "https://www.vinbudin.is/heim/vorur/tabid-2311.aspx/?category=beer/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        rows = soup.find_all("tr", class_="product")

        for row in rows:
            name_cell = row.find("td", class_="name")
            price_cell = row.find("td", class_="price")
            volume_cell = row.find("td", class_="volume")

            name = name_cell.text.strip().lower() if name_cell else ""
            volume = volume_cell.text.strip() if volume_cell else ""

            if name == "víking lite" and "500" in volume:
                return price_cell.text.strip() + " kr"

        return "-"
    except Exception as e:
        return f"Error: {e}"

# Fetch data
smarikid_total, smarikid_unit = get_smarikid_price()
heimkaup_total, heimkaup_unit = get_heimkaup_price()
nyjavinbudin_unit = get_nyjavinbudin_price()
vinbudin_unit = get_vinbudin_price()
st.write("🧪 vinbudin_unit =", vinbudin_unit)

# Calculate total for Nýja Vínbúðin (12 cans at unit price)
try:
    numeric = int(nyjavinbudin_unit.replace("kr.", "").replace("kr", "").replace(".", "").strip())
    nyjavinbudin_total = f"{numeric * 12} kr"
except:
    nyjavinbudin_total = "-"

import pandas as pd

# Clean numeric values from kr strings
def to_int(value):
    try:
        # Remove non-digit characters, except space and comma
        value = value.replace("kr.", "").replace("kr", "").replace(".", "").replace("stk", "").strip()
        return int("".join(filter(str.isdigit, value)))
    except:
        return None

# Convert prices to integers
smarikid_total_int = to_int(smarikid_total)
heimkaup_total_int = to_int(heimkaup_total)
nyjavinbudin_total_int = to_int(nyjavinbudin_total)
smarikid_unit_int = to_int(smarikid_unit)
heimkaup_unit_int = to_int(heimkaup_unit)
nyjavinbudin_unit_int = to_int(nyjavinbudin_unit)
vinbudin_unit_int = to_int(vinbudin_unit)
vinbudin_total_int = vinbudin_unit_int * 12 if vinbudin_unit_int else None

# Build comparison DataFrame
df = pd.DataFrame({
    "Store": [
        "Smárikid (12-pack)",
        "Heimkaup (12-pack)",
        "Nýja Vínbúðin (12-pack)",
        "Vínbúðin (12-pack)"
    ],
    "Total Price": [
        smarikid_total_int,
        heimkaup_total_int,
        nyjavinbudin_total_int,
        vinbudin_total_int
    ],
    "Unit Price": [
        smarikid_unit_int,
        heimkaup_unit_int,
        nyjavinbudin_unit_int,
        vinbudin_unit_int
    ]
})

# Find the lowest price
min_price = df["Total Price"].min()

# Add comparison column
df["Compared to Cheapest"] = df["Total Price"].apply(
    lambda x: (
        "Cheapest 🥇" if pd.notna(x) and x == min_price
        else f"+{round(((x - min_price) / min_price) * 100)}%" if pd.notna(x) and pd.notna(min_price) and min_price != 0
        else "-"
    )
)

# Sort by Total Price ascending
df_sorted = df.sort_values("Total Price").reset_index(drop=True)

# Display
st.markdown("### 📊 Current Prices – Sorted")
st.dataframe(df_sorted.style.format({
    "Total Price": "{:,.0f} kr",
    "Unit Price": "{:,.0f} kr"
}))

st.markdown("---")
st.caption("Made by Daniel using Python & Streamlit 💻")
