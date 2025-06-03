import tkinter as tk
from tkinter import ttk, messagebox
from firestore_manager import *


class ShopManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Shop Manager - Sales & Stock & Info")
        self.geometry("600x500")

        self.mode = None  # "sales", "stock", "info"
        self.info_option = None
        self.selected_store = None
        self.selected_category = None
        self.selected_color = None

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)

        self.show_mode_selection()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_mode_selection(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Select Mode:", font=("Arial", 18)).pack(pady=20)

        stock_btn = tk.Button(self.main_frame, text="Stock (Restock)", font=("Arial", 16), height=2,
                              command=lambda: self.select_mode("stock"))
        stock_btn.pack(fill="x", padx=40, pady=10)

        sales_btn = tk.Button(self.main_frame, text="Sales", font=("Arial", 16), height=2,
                              command=lambda: self.select_mode("sales"))
        sales_btn.pack(fill="x", padx=40, pady=10)

        info_btn = tk.Button(self.main_frame, text="INFO", font=("Arial", 16), height=2,
                             command=lambda: self.select_mode("info"))
        info_btn.pack(fill="x", padx=40, pady=10)

        add_btn = tk.Button(self.main_frame, text="ADD", font=("Arial", 16), height=2,
                            command=self.show_add_menu)
        add_btn.pack(fill="x", padx=40, pady=10)

    def add_new_shop(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Enter New Shop Name:", font=("Arial", 14)).pack(pady=10)
        entry = tk.Entry(self.main_frame)
        entry.pack(pady=5)
        tk.Button(self.main_frame, text="Submit", command=lambda: self.submit_new_shop(entry.get())).pack(pady=10)
        tk.Button(self.main_frame, text="Back", command=self.show_add_menu).pack()

    def submit_new_shop(self, name):
        if name.strip():
            add_shop(name.strip())
            messagebox.showinfo("Success", f"Shop '{name}' added.")
            self.show_add_menu()
        else:
            messagebox.showerror("Error", "Shop name cannot be empty.")

    def add_new_category(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Enter New Category Name:", font=("Arial", 14)).pack(pady=10)
        entry = tk.Entry(self.main_frame)
        entry.pack(pady=5)
        tk.Button(self.main_frame, text="Submit", command=lambda: self.submit_new_category(entry.get())).pack(pady=10)
        tk.Button(self.main_frame, text="Back", command=self.show_add_menu).pack()

    def submit_new_category(self, name):
        if name.strip():
            add_category(name.strip())
            messagebox.showinfo("Success", f"Category '{name}' added.")
            self.show_add_menu()
        else:
            messagebox.showerror("Error", "Category name cannot be empty.")

    def select_category_for_color(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Select Category to Add Color:", font=("Arial", 14)).pack(pady=10)
        categories = get_all("categories")
        for cat in categories:
            tk.Button(self.main_frame, text=cat, font=("Arial", 12),
                      command=lambda c=cat: self.add_color_to_category(c)).pack(fill="x", padx=20, pady=2)
        tk.Button(self.main_frame, text="Back", command=self.show_add_menu).pack(pady=10)

    def add_color_to_category(self, category):
        self.clear_frame()
        tk.Label(self.main_frame, text=f"Add Color to '{category}':", font=("Arial", 14)).pack(pady=10)
        entry = tk.Entry(self.main_frame)
        entry.pack(pady=5)
        tk.Button(self.main_frame, text="Submit", command=lambda: self.submit_new_color(category, entry.get())).pack(
            pady=10)
        tk.Button(self.main_frame, text="Back", command=self.select_category_for_color).pack()

    def submit_new_color(self, category, color):
        if color.strip():
            add_color_to_category(category, color.strip())
            messagebox.showinfo("Success", f"Color '{color}' added to category '{category}'.")
            self.show_add_menu()
        else:
            messagebox.showerror("Error", "Color cannot be empty.")

    def add_additional_cost(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Enter Additional Cost Amount ($):", font=("Arial", 14)).pack(pady=10)
        entry = tk.Entry(self.main_frame)
        entry.pack(pady=5)
        tk.Button(self.main_frame, text="Submit", command=lambda: self.submit_additional_cost(entry.get())).pack(
            pady=10)
        tk.Button(self.main_frame, text="Back", command=self.show_add_menu).pack()

    def submit_additional_cost(self, value):
        try:
            amount = float(value)
            add_additional_cost(amount)
            messagebox.showinfo("Success", f"Cost of ${amount:.2f} added.")
            self.show_add_menu()
        except:
            messagebox.showerror("Error", "Invalid number.")
    def show_add_menu(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Add New Data:", font=("Arial", 18)).pack(pady=20)

        tk.Button(self.main_frame, text="Add New Shop", font=("Arial", 14),
                  command=self.add_new_shop).pack(fill="x", padx=40, pady=5)

        tk.Button(self.main_frame, text="Add New Category", font=("Arial", 14),
                  command=self.add_new_category).pack(fill="x", padx=40, pady=5)

        tk.Button(self.main_frame, text="Add New Color to Category", font=("Arial", 14),
                  command=self.select_category_for_color).pack(fill="x", padx=40, pady=5)

        tk.Button(self.main_frame, text="Add Additional Cost", font=("Arial", 14),
                  command=self.add_additional_cost).pack(fill="x", padx=40, pady=5)

        tk.Button(self.main_frame, text="Back to Mode Selection", command=self.show_mode_selection).pack(pady=20)

    def select_mode(self, mode):
        self.mode = mode
        self.selected_store = None
        self.selected_category = None
        self.selected_color = None

        if self.mode == "sales":
            self.show_stores()
        elif self.mode == "stock":
            self.show_categories()
        else:  # info
            self.show_info_options()

    def show_stores(self):
        self.clear_frame()
        stores = get_all("stores")
        tk.Label(self.main_frame, text=f"Mode: {self.mode.title()}\nSelect Store:", font=("Arial", 16)).pack(pady=10)
        for store in stores:
            btn = tk.Button(self.main_frame, text=store, font=("Arial", 14), height=2,
                            command=lambda s=store: self.select_store(s))
            btn.pack(fill="x", pady=5, padx=20)
        back_btn = tk.Button(self.main_frame, text="Back to Mode Selection", command=self.show_mode_selection)
        back_btn.pack(pady=15)

    def select_store(self, store):
        self.selected_store = store
        self.show_categories()

    def show_categories(self):
        self.clear_frame()
        categories = get_all("categories")
        title = f"Mode: {self.mode.title()}"
        if self.mode == "sales":
            title += f"\nStore: {self.selected_store}"
        title += "\nSelect Category:"
        tk.Label(self.main_frame, text=title, font=("Arial", 16)).pack(pady=10)
        for cat in categories:
            btn = tk.Button(self.main_frame, text=cat, font=("Arial", 14), height=2,
                            command=lambda c=cat: self.select_category(c))
            btn.pack(fill="x", pady=5, padx=20)
        if self.mode == "sales":
            back_btn = tk.Button(self.main_frame, text="Back to Stores", command=self.show_stores)
        else:
            back_btn = tk.Button(self.main_frame, text="Back to Mode Selection", command=self.show_mode_selection)
        back_btn.pack(pady=15)

    def select_category(self, category):
        self.selected_category = category
        self.show_colors()

    def show_colors(self):
        self.clear_frame()

        # Fetch category-specific colors
        colors = get_colors_for_category(self.selected_category)  # ← This function queries Firestore

        title = f"Mode: {self.mode.title()}"
        if self.mode == "sales":
            title += f"\nStore: {self.selected_store}"
        title += f"\nCategory: {self.selected_category}\nSelect Color:"
        tk.Label(self.main_frame, text=title, font=("Arial", 16)).pack(pady=10)

        if not colors:
            tk.Label(self.main_frame, text="No colors found for this category.", font=("Arial", 12)).pack(pady=10)
        else:
            for color in colors:
                btn = tk.Button(self.main_frame, text=color, font=("Arial", 14), height=2,
                                command=lambda col=color: self.select_color(col))
                btn.pack(fill="x", pady=5, padx=20)

        back_btn = tk.Button(self.main_frame, text="Back to Categories", command=self.show_categories)
        back_btn.pack(pady=15)

    def select_color(self, color):
        self.selected_color = color
        self.show_input_form()

    def show_input_form(self):
        self.clear_frame()
        title = f"Mode: {self.mode.title()}"
        if self.mode == "sales":
            title += f"\nStore: {self.selected_store}"
        title += f"\nCategory: {self.selected_category}\nColor: {self.selected_color}"
        tk.Label(self.main_frame, text=title, font=("Arial", 16)).pack(pady=10)

        if self.mode == "stock":
            tk.Label(self.main_frame, text="Enter Quantity to Restock:").pack(pady=5)
            self.qty_entry = tk.Entry(self.main_frame)
            self.qty_entry.pack()
            tk.Label(self.main_frame, text="Enter Restock Cost (per unit):").pack(pady=5)
            self.cost_entry = tk.Entry(self.main_frame)
            self.cost_entry.pack()

            submit_btn = tk.Button(self.main_frame, text="Add Stock", font=("Arial", 14), command=self.add_stock)
            submit_btn.pack(pady=15)
        else:  # sales
            tk.Label(self.main_frame, text="Enter Sale Price:").pack(pady=5)
            entry_frame = tk.Frame(self.main_frame)
            entry_frame.pack(pady=5)

            self.price_entry = tk.Entry(entry_frame, width=10, font=("Arial", 14))
            self.price_entry.pack(side="left", padx=(0, 10))

            # Default price buttons
            default_prices = [50, 100, 200, 230, 250, 155]
            for price in default_prices:
                btn = tk.Button(entry_frame, text=str(price), width=4,
                                command=lambda p=price: self.quick_add_sale(p))
                btn.pack(side="left", padx=2)

            submit_btn = tk.Button(self.main_frame, text="Add Sale", font=("Arial", 14), command=self.add_sale)
            submit_btn.pack(pady=15)

        back_btn = tk.Button(self.main_frame, text="Back to Colors", command=self.show_colors)
        back_btn.pack(pady=10)

    def add_stock(self):
        try:
            qty = int(self.qty_entry.get())
            cost = float(self.cost_entry.get())
            add_stock(self.selected_category, self.selected_color, qty, cost)
            messagebox.showinfo("Success", "Stock added!")
            self.show_mode_selection()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def quick_add_sale(self, price):
        try:
            stock_qty = get_stock_for_item(self.selected_category, self.selected_color)
            if stock_qty <= 0:
                messagebox.showwarning("No Stock", "Cannot make sale: No stock available.")
                return

            # Add sale record
            add_sale(self.selected_store, self.selected_category, self.selected_color, float(price))

            # Now update stock qty - need the document reference to update
            docs = db.collection("stock") \
                .where("category", "==", self.selected_category) \
                .where("color", "==", self.selected_color) \
                .stream()

            for doc in docs:
                # Update qty by subtracting 1
                doc.reference.update({"qty": stock_qty - 1})
                break  # only update the first match

            messagebox.showinfo("Success", f"Sale added for ${price}")
            self.show_mode_selection()
        except Exception as e:
            messagebox.showerror("Error", f"Could not add sale: {e}")
    def add_sale(self):
        try:
            price = float(self.price_entry.get())
            current_stock = get_stock_for_item(self.selected_category, self.selected_color)

            if current_stock <= 0:
                messagebox.showerror("Error", "No stock available for this item.")
                return

            add_sale(self.selected_store, self.selected_category, self.selected_color, price)
            deduct_stock(self.selected_category, self.selected_color, 1)
            messagebox.showinfo("Success", "Sale added!")
            self.show_mode_selection()

        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def show_info_options(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="INFO Options:", font=("Arial", 18)).pack(pady=20)
        sales_info_btn = tk.Button(self.main_frame, text="Sales Summary", font=("Arial", 14), height=2,
                                   command=lambda: self.show_sales_info())
        sales_info_btn.pack(fill="x", padx=40, pady=5)

        stock_info_btn = tk.Button(self.main_frame, text="Stock Summary", font=("Arial", 14), height=2,
                                   command=lambda: self.show_stock_info())
        stock_info_btn.pack(fill="x", padx=40, pady=5)

        profits_info_btn = tk.Button(self.main_frame, text="Profits Summary", font=("Arial", 14), height=2,
                                     command=lambda: self.show_profits_info())
        profits_info_btn.pack(fill="x", padx=40, pady=5)

        back_btn = tk.Button(self.main_frame, text="Back to Mode Selection", command=self.show_mode_selection)
        back_btn.pack(pady=20)

    def show_sales_info(self):
        self.clear_frame()

        tk.Label(self.main_frame, text="Sales Summary Grouped by Month and Store:", font=("Arial", 14)).pack(pady=5)

        self.sales_tree = ttk.Treeview(self.main_frame, columns=("Month", "Store", "Total Sales"), show='headings')
        self.sales_tree.heading("Month", text="Month")
        self.sales_tree.heading("Store", text="Store")
        self.sales_tree.heading("Total Sales", text="Total Sales ($)")
        self.sales_tree.pack(fill="both", expand=True, pady=10)

        back_btn = tk.Button(self.main_frame, text="Back to INFO", command=self.show_info_options)
        back_btn.pack(pady=10)

        self.load_sales_data()

    def load_sales_data(self):
        grouping = "month_store"
        data = get_sales_summary(grouping)
        print("Sales summary data:", data)  # DEBUG

        # Clear treeview rows
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)

        if not data:
            print("No sales data found!")
            return

        # Sort and parse as before
        data_sorted = sorted(data, key=lambda x: x["month"])
        for item in data_sorted:
            group_parts = item["group"].split("|")
            month = group_parts[0]
            store = group_parts[1] if len(group_parts) > 1 else ""
            self.sales_tree.insert("", "end", values=(month, store, f"{item['total_sales']:.2f}"))

    def show_stock_info(self):
        self.clear_frame()

        tk.Label(self.main_frame, text="Stock Summary (Grouped by Category & Color):", font=("Arial", 14)).pack(pady=5)

        self.stock_tree = ttk.Treeview(self.main_frame, columns=("Category", "Color", "Quantity"), show='headings')
        self.stock_tree.heading("Category", text="Category")
        self.stock_tree.heading("Color", text="Color")
        self.stock_tree.heading("Quantity", text="Quantity")
        self.stock_tree.pack(fill="both", expand=True, pady=10)

        back_btn = tk.Button(self.main_frame, text="Back to INFO", command=self.show_info_options)
        back_btn.pack(pady=10)

        # Load stock data immediately
        self.load_stock_data()

    def load_stock_data(self):
        data = get_stock_summary()
        # Clear treeview rows
        for row in self.stock_tree.get_children():
            self.stock_tree.delete(row)

        for item in data:
            self.stock_tree.insert("", "end", values=(item["category"], item["color"], item["qty"]))

    def show_profits_info(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Profits Summary Grouped by Month:", font=("Arial", 14)).pack(pady=5)

        self.profits_tree = ttk.Treeview(self.main_frame)
        self.profits_tree.pack(fill="both", expand=True, pady=10)

        back_btn = tk.Button(self.main_frame, text="Back to INFO", command=self.show_info_options)
        back_btn.pack(pady=10)

        # Load profits data immediately
        self.load_profits_data()

    def load_profits_data(self):
        data = get_profits_summary()
        # Clear treeview
        for col in self.profits_tree.get_children():
            self.profits_tree.delete(col)
        self.profits_tree["columns"] = ("Month", "Profit")
        self.profits_tree.heading("#0", text="")
        self.profits_tree.column("#0", width=0, stretch=False)
        self.profits_tree.heading("Month", text="Month")
        self.profits_tree.heading("Profit", text="Profit ($)")

        for item in data:
            self.profits_tree.insert("", "end", values=(item["month"], f"{item['profit']:.2f}"))


if __name__ == "__main__":
    app = ShopManagerApp()
    app.mainloop()
