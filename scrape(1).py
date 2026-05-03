import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

# Create a 'data' folder if it doesn't exist (important for GitHub Actions)
os.makedirs("data", exist_ok=True)
file_path = "data/books_history.csv"

base_url = "http://books.toscrape.com/catalogue/page-{}.html"
products = []
scrape_time = datetime.now().strftime("%Y-%m-%d") # Added timestamp

for page in range(1, 51):
    response = requests.get(base_url.format(page))
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select(".product_pod")

    for item in items:
        title = item.h3.a["title"]
        price_text = item.select_one(".price_color").get_text().replace("£", "").replace("Â", "").strip()
        
        try:
            price = float(price_text)
        except:
            price = None

        rating_text = item.p["class"][1]
        rating_map = {"One":1, "Two":2, "Three":3, "Four":4, "Five":5}
        rating = rating_map.get(rating_text, None)
        availability = item.select_one(".availability").get_text(strip=True)

        products.append({
            "date": scrape_time, # Added this column
            "title": title,
            "price": price,
            "rating": rating,
            "availability": availability,
            "in_stock": "In stock" in availability
        })

new_df = pd.DataFrame(products).dropna()

# LOGIC: If the file exists, append. If not, create it.
if os.path.exists(file_path):
    # Avoid duplicate scrapes for the same day
    existing_df = pd.read_csv(file_path)
    if scrape_time not in existing_df['date'].values:
        final_df = pd.concat([existing_df, new_df], ignore_index=True)
        final_df.to_csv(file_path, index=False)
        print(f"✅ Data appended for {scrape_time}")
    else:
        print(f"⚠️ Data for {scrape_time} already exists. Skipping append.")
else:
    new_df.to_csv(file_path, index=False)
    print("✅ Initial CSV created.")