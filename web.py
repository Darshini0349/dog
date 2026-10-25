

"""
Project 5 (Automation): Web Scraper Dashboard
Scrapes structured product data from an HTML page with BeautifulSoup,
analyzes it (price stats, sorting, filtering), and exports a CSV report.

HOW THE DATA WORKS: real scrapers fetch a live URL with requests, then
parse the returned HTML. Since sandboxes often block outbound web requests,
this script GENERATES a realistic sample product page (embedded HTML) and
scrapes THAT — so the BeautifulSoup parsing, extraction, and reporting logic
is 100% real and verifiable. To point it at a live site, replace
get_html() with:  requests.get(url).text  (fetch code included, commented).

Run: pip install beautifulsoup4 pandas
     python 05_web_scraper_dashboard.py

Concepts practiced: HTML parsing with BeautifulSoup (find/find_all, CSS
selectors), extracting + cleaning scraped fields, aggregating into a report,
CSV export, and respecting that the PARSING is the transferable skill.
"""

import pandas as pd
from bs4 import BeautifulSoup

# --- How you'd fetch a real page (kept as reference) ---
# import requests
# def get_html(url):
#     resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
#     resp.raise_for_status()
#     return resp.text


def get_html():
    """Realistic sample product-listing HTML to scrape (stands in for a live page)."""
    products = [
        ("Wireless Mouse", "Electronics", 599, 4.3, "In Stock"),
        ("Mechanical Keyboard", "Electronics", 2499, 4.7, "In Stock"),
        ("Desk Lamp", "Home", 899, 4.1, "Out of Stock"),
        ("Water Bottle", "Home", 349, 4.5, "In Stock"),
        ("Backpack", "Accessories", 1599, 4.6, "In Stock"),
        ("USB-C Hub", "Electronics", 1299, 3.9, "In Stock"),
        ("Notebook Set", "Stationery", 199, 4.2, "Out of Stock"),
        ("Bluetooth Speaker", "Electronics", 1899, 4.4, "In Stock"),
    ]
    cards = ""
    for name, cat, price, rating, stock in products:
        cards += f"""
        <div class="product-card" data-category="{cat}">
            <h3 class="name">{name}</h3>
            <span class="price">Rs {price}</span>
            <span class="rating">{rating}</span>
            <span class="stock">{stock}</span>
        </div>"""
    return f"<html><body><div class='listing'>{cards}</div></body></html>"


def scrape_products(html):
    """The REAL parsing logic — identical whether the HTML is live or sample."""
    soup = BeautifulSoup(html, "html.parser")
    products = []
    for card in soup.find_all("div", class_="product-card"):
        name = card.find("h3", class_="name").get_text(strip=True)
        category = card["data-category"]
        # Clean the price: strip "Rs " and commas, convert to int.
        price_text = card.find("span", class_="price").get_text(strip=True)
        price = int(price_text.replace("Rs", "").replace(",", "").strip())
        rating = float(card.find("span", class_="rating").get_text(strip=True))
        stock = card.find("span", class_="stock").get_text(strip=True)
        products.append({"name": name, "category": category,
                         "price": price, "rating": rating, "stock": stock})
    return products


def build_report(products):
    df = pd.DataFrame(products)
    print(f"Scraped {len(df)} products.\n")

    print("--- Price statistics ---")
    print(f"  Cheapest: {df.loc[df['price'].idxmin(), 'name']} (Rs {df['price'].min()})")
    print(f"  Priciest: {df.loc[df['price'].idxmax(), 'name']} (Rs {df['price'].max()})")
    print(f"  Average price: Rs {df['price'].mean():.0f}")

    print("\n--- By category (avg price) ---")
    for cat, group in df.groupby("category"):
        print(f"  {cat}: {len(group)} items, avg Rs {group['price'].mean():.0f}")

    print("\n--- Top rated, in stock ---")
    in_stock = df[df["stock"] == "In Stock"].sort_values("rating", ascending=False)
    for _, row in in_stock.head(3).iterrows():
        print(f"  {row['name']} — {row['rating']}★ (Rs {row['price']})")

    csv_path = "scraped_products.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nFull data exported: {csv_path}")
    return df


def main():
    print("=== Web Scraper Dashboard ===")
    html = get_html()
    products = scrape_products(html)
    build_report(products)


if __name__ == "__main__":
    main()