import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Beer Price Comparison", page_icon="🍺", layout="centered")

st.title("🍺 Víking Lite Price Comparison (500ml cans)")
st.caption("Real-time comparison from Icelandic Online Liquor Stores")

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
        print(f"Error fetching Vínbúðin price: {e}")
        return "-"

@st.cache_data
def get_desma_price():
    try:
        url = "https://desma.is/products/viking-lite-500ml-4-4"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        # Look for sale price first
        sale_price = soup.find("span", class_="price-item price-item--sale price-item--last")
        if sale_price and sale_price.text.strip():
            price = sale_price.text.strip()
        else:
            price = soup.find("span", class_="price-item price-item--regular").text.strip()

        return price
    except Exception as e:
        print("⚠️ Desma fetch error:", e)
        return "-"

@st.cache_data
def get_sante_price():
    try:
        url = "https://sante.is/products/viking-lite-50-cl-dos"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        # Look for sale price first
        sale_price = soup.find("span", class_="price-item price-item--sale price-item--last")
        if sale_price and sale_price.text.strip():
            price = sale_price.text.strip()
        else:
            price = soup.find("span", class_="price-item price-item--regular").text.strip()

        return price
    except Exception as e:
        print("⚠️ Santé fetch error:", e)
        return "-"

@st.cache_data
def get_hagkaup_price():
    try:
        url = "https://www.veigar.eu/vara/viking-lite-500-ml-12pk-157969"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all <p> tags and look for one that starts with "Verð:"
        price_paragraphs = soup.find_all("p")
        for p in price_paragraphs:
            if p.text.strip().startswith("Verð:"):
                price_span = p.find("span")
                if price_span:
                    return price_span.text.strip()

        return "-"
    except Exception as e:
        print("⚠️ Hagkaup (veigar) fetch error:", e)
        return "-"

@st.cache_data
def get_costco_price():
    try:
        url = "https://www.costco.is/Alcohol-Click-Collect/Viking-Lite-12-x-500ml/p/453945"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        price_tag = soup.find("span", class_="notranslate ng-star-inserted")
        if price_tag:
            return price_tag.text.strip()
        else:
            return "-"
    except Exception as e:
        print("⚠️ Costco fetch error:", e)
        return "-"

# Fetch data
smarikid_total, smarikid_unit = get_smarikid_price()
heimkaup_total, heimkaup_unit = get_heimkaup_price()
nyjavinbudin_unit = get_nyjavinbudin_price()
vinbudin_unit = get_vinbudin_price()
desma_unit = get_desma_price()
sante_unit = get_sante_price()
hagkaup_unit = get_hagkaup_price()
costco_unit = get_costco_price()

# Calculate total (12 cans at unit price)
try:
    numeric = int(nyjavinbudin_unit.replace("kr.", "").replace("kr", "").replace(".", "").strip())
    nyjavinbudin_total = f"{numeric * 12} kr"
except:
    nyjavinbudin_total = "-"

try:
    desma_numeric = int(desma_unit.replace("kr.", "").replace("kr", "").replace(".", "").strip())
    desma_total = f"{desma_numeric} kr"
    desma_unit_calc = f"{round(desma_numeric / 12)} kr"
except:
    desma_total = "-"
    desma_unit_calc = "-"

try:
    sante_numeric = int(sante_unit.replace("kr.", "").replace("ISK", "").replace("kr", "").replace(".", "").strip())
    sante_total = f"{sante_numeric} kr"
    sante_unit_calc = f"{round(sante_numeric / 12)} kr"
except:
    sante_total = "-"
    sante_unit_calc = "-"

try:
    hagkaup_numeric = int(hagkaup_unit.replace("kr.", "").replace("kr", "").replace(".", "").strip())
    hagkaup_total = f"{hagkaup_numeric} kr"
    hagkaup_unit_calc = f"{round(hagkaup_numeric / 12)} kr"
except:
    hagkaup_total = "-"
    hagkaup_unit_calc = "-"

try:
    costco_numeric = int(costco_unit.replace("kr.", "").replace("kr", "").replace(".", "").strip())
    costco_total = f"{costco_numeric} kr"
    costco_unit_calc = f"{round(costco_numeric / 12)} kr"
except:
    costco_total = "-"
    costco_unit_calc = "-"

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
desma_total_int = to_int(desma_total)
desma_unit_int = to_int(desma_unit_calc)
sante_total_int = to_int(sante_total)
sante_unit_int = to_int(sante_unit_calc)
hagkaup_total_int = to_int(hagkaup_total)
hagkaup_unit_int = to_int(hagkaup_unit_calc)
costco_total_int = to_int(costco_total)
costco_unit_int = to_int(costco_unit_calc)  

# Build comparison DataFrame
df = pd.DataFrame({
    "Store": [
        "Smárikid (12-pack)",
        "Hagkaup (12-pack)",
        "Nýja Vínbúðin (12-pack)",
        "Santé (12-pack)",
        "Heimkaup (12-pack)",
        "Desma Vínbúð (12-pack)",
        "Costco (12-pack)"
    ],
    "Total Price": [
        smarikid_total_int,
        hagkaup_total_int,
        nyjavinbudin_total_int,
        sante_total_int,
        heimkaup_total_int,
        desma_total_int,
        costco_total_int
    ],
    "Unit Price": [
        smarikid_unit_int,
        hagkaup_unit_int,
        nyjavinbudin_unit_int,
        sante_unit_int,
        heimkaup_unit_int,
        desma_unit_int,
        costco_unit_int
    ],
    "Link": [
        "https://smarikid.is/product/65577db2c98d14ede00b576d",
        "https://www.veigar.eu/vara/viking-lite-500-ml-12pk-157969",
        "https://nyjavinbudin.is/vara/viking-lite/",
        "https://sante.is/products/viking-lite-50-cl-dos",
        "https://www.heimkaup.is/viking-lite-0-5l-10pk-dos-afhendist-kaldur",
        "https://desma.is/products/viking-lite-500ml-4-4",
        "https://www.costco.is/Alcohol-Click-Collect/Viking-Lite-12-x-500ml/p/453945"
    ]
})

# Remove any rows where Total Price is missing or invalid
df = df[df["Total Price"].notna()]
df = df[df["Total Price"] != "-"]

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

import pandas as pd
import streamlit as st

# Add the Buy column with clickable markdown links
df_sorted["Buy"] = df_sorted.apply(
    lambda row: f'[Buy at {row["Store"]}]({row["Link"]})' if pd.notna(row["Link"]) else "-", axis=1
)

# Drop the 'Link' column before styling and displaying
df_display = df_sorted.drop(columns=["Link"])

# Display the dataframe with formatting and clickable Buy links
st.markdown("### 📊 Current Prices – Sorted")

st.write(
    df_display.style.format({
        "Total Price": "{:,.0f} kr",
        "Unit Price": "{:,.0f} kr",
        "Buy": lambda x: x  # Pass-through so markdown renders as clickable links
    }).set_properties(subset=["Buy"], **{"text-align": "center"})
     .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])
     .format({"Buy": lambda x: x}, escape="html")
)

st.markdown("---")
st.caption("Made by Daniel using Python & Streamlit 💻")

