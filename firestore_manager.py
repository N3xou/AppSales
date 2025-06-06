import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from collections import defaultdict
import os,sys
def resource_path(relative_path):
    # Get absolute path to resource, works for dev and PyInstaller
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

firebase_json_path = resource_path("firebase_key.json")
# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_json_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_costs_summary():
    # Assume 'additional_costs' collection has docs with fields:
    # 'category' (one of 'restock', 'shipping', 'extra'), 'amount', 'timestamp'

    costs_docs = db.collection("additional_costs").stream()

    costs_by_month_category = defaultdict(float)
    for doc in costs_docs:
        data = doc.to_dict()
        category = data.get("category", "").lower()
        amount = data.get("amount", 0)
        timestamp = data.get("timestamp")
        if not timestamp or category not in {"restock", "shipping", "extra"}:
            continue
        month_str = timestamp.strftime("%Y-%m")
        costs_by_month_category[(month_str, category)] += amount

    result = []
    for (month, category), amount in sorted(costs_by_month_category.items()):
        result.append({"month": month, "category": category.capitalize(), "amount": amount})

    return result

def add_shop(name):
    db.collection("stores").add({"name": name})



def add_color_to_category(category_name, color):
    docs = db.collection("categories").where("name", "==", category_name).stream()
    for doc in docs:
        ref = doc.reference
        data = doc.to_dict()
        colors = data.get("colors", [])
        if color not in colors:
            colors.append(color)
            ref.update({"colors": colors})
        break

def add_additional_cost(amount):
    db.collection("additional_costs").add({
        "amount": amount,
        "timestamp": datetime.utcnow()
    })
def get_colors_for_category(category_name):
    docs = db.collection("categories").where("name", "==", category_name).stream()
    for doc in docs:
        data = doc.to_dict()
        return data.get("colors", [])
    return []
def get_sales_summary(grouping):
    if grouping != "month_store":
        raise NotImplementedError("Only 'month_store' grouping is implemented")

    sales_ref = db.collection("sales")
    docs = sales_ref.stream()

    # Aggregate sales by month and store
    summary = defaultdict(float)  # key: (month, store), value: total sales

    for doc in docs:
        data = doc.to_dict()
        price = data.get("price", 0)
        store = data.get("shop") or data.get("store") or "Unknown"

        # Extract month from timestamp
        timestamp = data.get("timestamp")
        if not timestamp:
            continue

        if hasattr(timestamp, "strftime"):  # Firestore timestamp
            month_str = timestamp.strftime("%Y-%m")
        else:  # fallback
            month_str = datetime.utcnow().strftime("%Y-%m")

        key = (month_str, store)
        summary[key] += price

    # Convert to list of dicts with "group" and "total_sales"
    results = []
    for (month, store), total in summary.items():
        results.append({
            "group": f"{month}|{store}",
            "month": month,
            "store": store,
            "total_sales": total,
        })

    return results


def get_stock_for_item(category, color):
    docs = db.collection("stock")\
             .where("category", "==", category)\
             .where("color", "==", color)\
             .stream()

    for doc in docs:
        return doc.to_dict().get("qty", 0)
    return 0  # No matching document found

def deduct_stock(category, color, quantity):
    docs = db.collection("stock")\
             .where("category", "==", category)\
             .where("color", "==", color)\
             .stream()

    for doc in docs:
        data = doc.to_dict()
        current_qty = data.get("qty", 0)
        doc.reference.update({"qty": max(0, current_qty - quantity)})
        return

def get_stock_summary():
    stock_ref = db.collection("stock")
    stock_docs = stock_ref.stream()

    summary = defaultdict(int)

    for doc in stock_docs:
        data = doc.to_dict()

        category = data.get("category", "Unknown")
        color = data.get("color", "Unknown")
        qty = data.get("qty", 0)
        summary[(category, color)] += qty

    return [{"category": cat, "color": col, "qty": q} for (cat, col), q in summary.items()]



def get_profits_summary():
    # Fetch all sales, restocks, and additional costs
    sales_docs = db.collection("sales").stream()
    restocks_docs = db.collection("stock").stream()
    costs_docs = db.collection("additional_costs").stream()

    # Aggregate sales revenue by month
    sales_by_month = defaultdict(float)
    for doc in sales_docs:
        data = doc.to_dict()
        price = data.get("price", 0)
        timestamp = data.get("timestamp")
        if not timestamp:
            continue
        month_str = timestamp.strftime("%Y-%m")
        sales_by_month[month_str] += price

    # Aggregate restock costs by month
    restocks_by_month = defaultdict(float)
    for doc in restocks_docs:
        data = doc.to_dict()
        cost = data.get("restock_cost", 0)
        qty = data.get("qty", 0)
        timestamp = data.get("timestamp")  # Make sure restock docs have timestamp
        if not timestamp:
            continue
        month_str = timestamp.strftime("%Y-%m")
        restocks_by_month[month_str] += cost * qty

    # Aggregate additional costs by month
    additional_costs_by_month = defaultdict(float)
    for doc in costs_docs:
        data = doc.to_dict()
        amount = data.get("amount", 0)
        timestamp = data.get("timestamp")
        if not timestamp:
            continue
        month_str = timestamp.strftime("%Y-%m")
        additional_costs_by_month[month_str] += amount

    # Calculate profits by month = sales - restock costs - additional costs
    months = set(list(sales_by_month.keys()) + list(restocks_by_month.keys()) + list(additional_costs_by_month.keys()))
    profits = []
    for month in sorted(months):
        total_sales = sales_by_month.get(month, 0)
        total_restock = restocks_by_month.get(month, 0)
        total_additional = additional_costs_by_month.get(month, 0)
        profit = total_sales - total_restock - total_additional
        profits.append({"month": month, "profit": profit})

    return profits

def add_store(name):
    db.collection("stores").add({"name": name})

def add_color(name):
    db.collection("colors").add({"name": name})

def get_all(collection_name):
    docs = db.collection(collection_name).stream()
    return [doc.to_dict()['name'] for doc in docs]

def add_stock(category, color, qty, restock_cost):
    # Check if stock for category+color exists
    docs = db.collection("stock")\
             .where("category", "==", category)\
             .where("color", "==", color)\
             .stream()

    for doc in docs:
        data = doc.to_dict()
        current_qty = data.get("qty", 0)
        doc.reference.update({"qty": current_qty + qty})
        return

    # If no document exists, create one
    db.collection("stock").add({
        "category": category,
        "color": color,
        "qty": qty,
        "restock_cost": restock_cost,
    })


def add_sale(shop, category, color, price):
    db.collection("sales").add({
        "shop": shop,
        "category": category,
        "color": color,
        "price": price,
        "timestamp": datetime.utcnow()
    })

def add_monthly_cost(amount):
    now = datetime.utcnow().strftime("%Y-%m")
    doc_ref = db.collection("costs").document(now)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({"amount": firestore.Increment(amount)})
    else:
        doc_ref.set({"amount": amount})

def get_summary():
    from collections import defaultdict
    import pandas as pd

    sales_docs = db.collection("sales").stream()
    stock_docs = db.collection("stock").stream()
    cost_docs = db.collection("costs").stream()

    sales = []
    for doc in sales_docs:
        d = doc.to_dict()
        month = d['timestamp'].strftime("%Y-%m")
        sales.append([month, d['shop'], d['price']])
    sales_df = pd.DataFrame(sales, columns=["Month", "Shop", "Price"])
    monthly_sales = sales_df.groupby(["Month", "Shop"])["Price"].sum().unstack(fill_value=0)

    stock = []
    for doc in stock_docs:
        d = doc.to_dict()
        month = d['timestamp'].strftime("%Y-%m")
        stock.append([month, d['restock_cost']])
    stock_df = pd.DataFrame(stock, columns=["Month", "Restock Cost"])
    monthly_restock = stock_df.groupby("Month")["Restock Cost"].sum()

    costs = {}
    for doc in cost_docs:
        costs[doc.id] = doc.to_dict()["amount"]
    cost_df = pd.Series(costs)

    monthly_profit = monthly_sales.sum(axis=1) - (monthly_restock + cost_df)
    return monthly_sales, monthly_restock, cost_df, monthly_profit

def get_remaining_stock():
    stock_docs = db.collection("stock").stream()
    sale_docs = db.collection("sales").stream()

    stock = defaultdict(int)
    for doc in stock_docs:
        d = doc.to_dict()
        key = (d['category'], d['color'])
        stock[key] += d['qty']

    for doc in sale_docs:
        d = doc.to_dict()
        key = (d['category'], d['color'])
        stock[key] -= 1

    return stock
