import tkinter as tk
from tkinter import ttk, messagebox
from firestore_manager import *
import sys
import os

class ShopManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Shop Manager - Monthly Sales & Stock & Info")

        # Desired window size
        window_width = 800
        window_height = 600

        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate position for centering
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # Set the geometry with calculated position
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

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

        sales_info_btn = tk.Button(self.main_frame, text="Sales & Stock", font=("Arial", 14), height=2,
                                   command=lambda: self.show_sales_and_stock_info())
        sales_info_btn.pack(fill="x", padx=40, pady=5)

        sales_btn = tk.Button(self.main_frame, text="Add Sale", font=("Arial", 16), height=2,
                              command=lambda: self.select_mode("sales"))
        sales_btn.pack(fill="x", padx=40, pady=10)

        stock_btn = tk.Button(self.main_frame, text="Restock Set", font=("Arial", 16), height=2,
                              command=self.restock_set)
        stock_btn.pack(fill="x", padx=40, pady=10)

        add_btn = tk.Button(self.main_frame, text="ADD", font=("Arial", 16), height=2,
                            command=self.show_add_menu)
        add_btn.pack(fill="x", padx=40, pady=10)

        profits_info_btn = tk.Button(self.main_frame, text="Profits & Costs", font=("Arial", 14), height=2,
                                     command=lambda: self.show_profits_sales_history())
        profits_info_btn.pack(fill="x", padx=40, pady=5)

        info_btn = tk.Button(self.main_frame, text="EXTRA", font=("Arial", 16), height=2,
                             command=lambda: self.select_mode("info"))
        info_btn.pack(fill="x", padx=40, pady=10)
    def show_add_menu(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Add New Data:", font=("Arial", 18)).pack(pady=20)

        tk.Button(self.main_frame, text="Add Stock", font=("Arial", 14),
                  command=self.add_stock).pack(fill="x", padx=40, pady=5)

        tk.Button(self.main_frame, text="New Acc", font=("Arial", 14),
                  command=self.add_new_acc).pack(fill="x", padx=40, pady=5)

        tk.Button(self.main_frame, text="New category", font=("Arial", 14),
                  command=self.add_new_category).pack(fill="x", padx=40, pady=5)

        tk.Button(self.main_frame, text="New color", font=("Arial", 14),
                  command=self.select_category_for_color).pack(fill="x", padx=40, pady=5)

        tk.Button(self.main_frame, text="Cost", font=("Arial", 14),
                  command=self.add_additional_cost).pack(fill="x", padx=40, pady=5)

        tk.Button(self.main_frame, text="Back to Mode Selection", command=self.show_mode_selection).pack(pady=20)

    def restock_set(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Select Category to Restock:", font=("Arial", 16)).pack(pady=10)

        def choose_category(category_data):
            self.ask_restock_quantity(category_data)

        categories = db.collection("categories").stream()
        for doc in categories:
            category_data = doc.to_dict()
            category_name = category_data.get("name")
            tk.Button(self.main_frame, text=category_name, font=("Arial", 14),
                      command=lambda cat=category_data: choose_category(cat)).pack(pady=5)

        tk.Button(self.main_frame, text="Back", command=self.show_mode_selection).pack(pady=10)

    def ask_restock_quantity(self, category_data):
        self.clear_frame()
        category_name = category_data["name"]
        default_price = category_data.get("default_price", 0)  # fix field name here
        colors = category_data.get("colors", [])

        if not colors:
            messagebox.showerror("Error", f"No colors found for category '{category_name}'.")
            self.restock_set()
            return

        tk.Label(self.main_frame, text=f"Enter number of sets to restock for '{category_name}':",
                 font=("Arial", 14)).pack(pady=10)
        qty_entry = tk.Entry(self.main_frame, font=("Arial", 14))
        qty_entry.pack(pady=5)

        def submit_restock():
            try:
                num_sets = int(qty_entry.get())
                total_units = 0

                for color_name in colors:
                    # Update stock for each color
                    stock_query = db.collection("stock") \
                        .where("category", "==", category_name) \
                        .where("color", "==", color_name) \
                        .limit(1).stream()

                    updated = False
                    for stock_doc in stock_query:
                        stock = stock_doc.to_dict()
                        new_qty = stock.get("qty", 0) + num_sets
                        db.collection("stock").document(stock_doc.id).update({"qty": new_qty})
                        updated = True

                    if not updated:
                        db.collection("stock").add({
                            "category": category_name,
                            "color": color_name,
                            "qty": num_sets
                        })

                    total_units += num_sets

                # Log cost
                total_cost = total_units * default_price
                from datetime import datetime
                db.collection("additional_costs").add({
                    "category": "restock",
                    "amount": total_cost,
                    "timestamp": datetime.utcnow()
                })

                #messagebox.showinfo("Success",
                #                    f"{num_sets} sets restocked in '{category_name}' (Total cost: ${total_cost:.2f})")
                self.show_mode_selection()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid input: {e}")

        tk.Button(self.main_frame, text="Submit", command=submit_restock).pack(pady=10)
        tk.Button(self.main_frame, text="Back", command=self.restock_set).pack(pady=10)

    def add_new_acc(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Enter New Acc Name:", font=("Arial", 14)).pack(pady=10)
        entry = tk.Entry(self.main_frame)
        entry.pack(pady=5)
        tk.Button(self.main_frame, text="Submit", command=lambda: self.submit_new_shop(entry.get())).pack(pady=10)
        tk.Button(self.main_frame, text="Back", command=self.show_add_menu).pack()

    def submit_new_shop(self, name):
        if name.strip():
            add_shop(name.strip())
            #messagebox.showinfo("Success", f"Acc '{name}' added.")
            self.show_add_menu()
        else:
            messagebox.showerror("Error", "Acc name cannot be empty.")

    def add_new_category(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Add New Category", font=("Arial", 18)).pack(pady=10)

        tk.Label(self.main_frame, text="Category Name:", font=("Arial", 14)).pack()
        name_entry = tk.Entry(self.main_frame, font=("Arial", 14))
        name_entry.pack(pady=5)

        tk.Label(self.main_frame, text="Default Restock Price ($):", font=("Arial", 14)).pack()
        price_entry = tk.Entry(self.main_frame, font=("Arial", 14))
        price_entry.pack(pady=5)

        def set_price(value):
            price_entry.delete(0, tk.END)
            price_entry.insert(0, str(value))

        defaults = [19.20, 24.90, 15, 12, 12]
        button_frame = tk.Frame(self.main_frame)
        button_frame.pack(pady=5)
        for val in defaults:
            tk.Button(button_frame, text=str(val), width=6, command=lambda v=val: set_price(v)).pack(side="left",
                                                                                                     padx=2)

        def submit():
            name = name_entry.get().strip()
            try:
                price = float(price_entry.get())
                if not name:
                    raise ValueError("Category name is required.")
                db.collection("categories").add({
                    "name": name,
                    "default_price": price
                })
                #messagebox.showinfo("Success", f"Category '{name}' added with default price ${price:.2f}")
                self.show_add_menu()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid input: {e}")

        tk.Button(self.main_frame, text="Submit", font=("Arial", 14), command=submit).pack(pady=10)
        tk.Button(self.main_frame, text="Back", font=("Arial", 14), command=self.show_add_menu).pack(pady=5)

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
            #messagebox.showinfo("Success", f"Color '{color}' added to category '{category}'.")
            self.show_add_menu()
        else:
            messagebox.showerror("Error", "Color cannot be empty.")

    def add_additional_cost(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Enter Additional Cost Amount ($):", font=("Arial", 14)).pack(pady=10)
        amount_entry = tk.Entry(self.main_frame)
        amount_entry.pack(pady=5)

        tk.Label(self.main_frame, text="Select Cost Category:", font=("Arial", 14)).pack(pady=10)
        category_var = tk.StringVar(value="restock")  # default value
        categories = ["restock", "shipping", "extra"]
        category_menu = ttk.Combobox(self.main_frame, textvariable=category_var, values=categories, state="readonly")
        category_menu.pack(pady=5)

        def submit():
            amount_str = amount_entry.get()
            category = category_var.get()
            self.submit_additional_cost(amount_str, category)

        tk.Button(self.main_frame, text="Submit", command=submit).pack(pady=10)
        tk.Button(self.main_frame, text="Back", command=self.show_add_menu).pack()

    def add_shipping_cost(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Add Shipping Cost", font=("Arial", 18)).pack(pady=20)

        tk.Label(self.main_frame, text="Amount ($):", font=("Arial", 14)).pack(pady=5)
        amount_entry = tk.Entry(self.main_frame, font=("Arial", 14))
        amount_entry.pack(pady=5)



    def submit_additional_cost(self, amount_str, category):
        try:
            amount = float(amount_str)
            from datetime import datetime
            db.collection("additional_costs").add({
                "category": category,
                "amount": amount,
                "timestamp": datetime.utcnow()
            })
            #messagebox.showinfo("Success", f"Additional cost added to '{category}'!")
            self.show_add_menu()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")



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
        tk.Label(self.main_frame, text=f"Mode: {self.mode.title()}\nSelect Acc:", font=("Arial", 16)).pack(pady=10)
        for store in stores:
            btn = tk.Button(self.main_frame, text=store, font=("Arial", 14), height=2,
                            command=lambda s=store: self.select_store(s))
            btn.pack(fill="x", pady=5, padx=20)
        back_btn = tk.Button(self.main_frame, text="Back to Mode Selection", command=self.show_mode_selection)
        back_btn.pack(pady=15)

    def select_store(self, store):
        self.selected_store = store
        self.show_categories()

    def custom_sale_input(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Custom Sale", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.main_frame, text="Enter Color Name:", font=("Arial", 12)).pack()
        color_entry = tk.Entry(self.main_frame, font=("Arial", 12))
        color_entry.pack(pady=5)

        tk.Label(self.main_frame, text="Enter Price ($):", font=("Arial", 12)).pack()
        price_entry = tk.Entry(self.main_frame, font=("Arial", 12))
        price_entry.pack(pady=5)

        def submit_custom_sale():
            try:
                color = color_entry.get().strip()
                price = float(price_entry.get())

                if not color:
                    raise ValueError("Color cannot be empty.")

                # Log sale to Firestore
                add_sale(self.selected_store, "custom", color, price)
                #messagebox.showinfo("Success", f"Custom sale added for ${price:.2f}")
                self.show_mode_selection()

            except Exception as e:
                messagebox.showerror("Error", f"Invalid input: {e}")

        tk.Button(self.main_frame, text="Submit Sale", command=submit_custom_sale).pack(pady=10)
        tk.Button(self.main_frame, text="Back", command=self.show_mode_selection).pack(pady=10)

    def show_categories(self):
        self.clear_frame()
        categories = get_all("categories")
        title = f"Mode: {self.mode.title()}"
        if self.mode == "sales":
            title += f"\nAcc: {self.selected_store}"
        title += "\nSelect Category:"
        tk.Label(self.main_frame, text=title, font=("Arial", 16)).pack(pady=10)

        # ✅ Add Custom Sale button for sales mode
        if self.mode == "sales":
            tk.Button(self.main_frame, text="Custom Sale", font=("Arial", 14), bg="#007BFF", fg="white",
                      command=self.custom_sale_input).pack(fill="x", padx=20, pady=5)

        # Category buttons
        for cat in categories:
            btn = tk.Button(self.main_frame, text=cat, font=("Arial", 14), height=2,
                            command=lambda c=cat: self.select_category(c))
            btn.pack(fill="x", pady=5, padx=20)

        # Back button
        if self.mode == "sales":
            back_btn = tk.Button(self.main_frame, text="Back to Accs", command=self.show_stores)
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
            title += f"\nAcc: {self.selected_store}"
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
            title += f"\nAcc: {self.selected_store}"
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
            default_prices = [45, 60, 100, 200, 230, 250 ]
            for price in default_prices:
                btn = tk.Button(entry_frame, text=str(price), width=4,
                                command=lambda p=price: self.quick_add_sale(p))
                btn.pack(side="left", padx=2)

            submit_btn = tk.Button(self.main_frame, text="Add Sale", font=("Arial", 14), command=self.add_sale)
            submit_btn.pack(pady=15)

        back_btn = tk.Button(self.main_frame, text="Back to Colors", command=self.show_colors)
        back_btn.pack(pady=10)

    def add_stock(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Select Category to Add Stock", font=("Arial", 18)).pack(pady=10)

        categories = list(db.collection("categories").stream())
        for cat_doc in categories:
            cat_data = cat_doc.to_dict()
            category_name = cat_data.get("name", "Unknown")
            tk.Button(self.main_frame, text=category_name, font=("Arial", 14), height=2,
                      command=lambda c=cat_data: self.select_color_for_stock(c)).pack(fill="x", padx=40, pady=5)

        tk.Button(self.main_frame, text="Back", font=("Arial", 12),
                  command=self.show_add_menu).pack(pady=10)

    def select_color_for_stock(self, category_data):
        self.clear_frame()
        category_name = category_data.get("name", "")
        tk.Label(self.main_frame, text=f"Select Color in '{category_name}'", font=("Arial", 18)).pack(pady=10)

        colors = category_data.get("colors", [])
        if not colors:
            messagebox.showerror("Error", f"No colors found in category '{category_name}'.")
            self.add_stock()
            return

        for color in colors:
            tk.Button(self.main_frame, text=color, font=("Arial", 14), height=2,
                      command=lambda col=color: self.select_quantity_for_stock(category_data, col)).pack(fill="x",
                                                                                                         padx=40,
                                                                                                         pady=5)

        tk.Button(self.main_frame, text="Back", font=("Arial", 12),
                  command=self.add_stock).pack(pady=10)

    def select_quantity_for_stock(self, category_data, color):
        self.clear_frame()
        category_name = category_data.get("name", "")
        default_price = category_data.get("default_price", 0)

        tk.Label(self.main_frame, text=f"Select Quantity to Add for {category_name} - {color}",
                 font=("Arial", 18)).pack(pady=10)

        def restock_with_quantity(qty):
            try:
                qty = int(qty)
                if qty <= 0:
                    raise ValueError("Quantity must be positive.")

                # Query stock for this category/color
                stock_query = db.collection("stock") \
                    .where("category", "==", category_name) \
                    .where("color", "==", color) \
                    .limit(1).stream()

                updated = False
                for stock_doc in stock_query:
                    stock = stock_doc.to_dict()
                    new_qty = stock.get("qty", 0) + qty
                    db.collection("stock").document(stock_doc.id).update({"qty": new_qty})
                    updated = True

                if not updated:
                    db.collection("stock").add({
                        "category": category_name,
                        "color": color,
                        "qty": qty,
                        "restock_cost": default_price
                    })

                # Log restock cost
                total_cost = qty * default_price
                from datetime import datetime
                db.collection("additional_costs").add({
                    "category": "restock",
                    "amount": total_cost,
                    "timestamp": datetime.utcnow()
                })

                self.add_stock()

            except ValueError as ve:
                messagebox.showerror("Error", f"Invalid quantity: {ve}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add stock: {e}")

        # Frame for preset quantity buttons + manual entry
        qty_frame = tk.Frame(self.main_frame)
        qty_frame.pack(pady=10)

        # Preset quantity buttons 1 to 5
        for q in range(1, 6):
            tk.Button(qty_frame, text=str(q), font=("Arial", 14), width=4,
                      command=lambda qty=q: restock_with_quantity(qty)).pack(side="left", padx=5)

        # Manual entry label and entry box
        manual_frame = tk.Frame(self.main_frame)
        manual_frame.pack(pady=10)

        tk.Label(manual_frame, text="Or enter quantity:", font=("Arial", 14)).pack(side="left", padx=5)
        qty_entry = tk.Entry(manual_frame, font=("Arial", 14), width=5)
        qty_entry.pack(side="left", padx=5)

        def submit_manual_qty():
            qty_val = qty_entry.get().strip()
            if not qty_val:
                messagebox.showerror("Error", "Please enter a quantity.")
                return
            restock_with_quantity(qty_val)

        tk.Button(manual_frame, text="Submit", font=("Arial", 14), command=submit_manual_qty).pack(side="left", padx=5)

        tk.Button(self.main_frame, text="Back", font=("Arial", 12),
                  command=lambda: self.select_color_for_stock(category_data)).pack(pady=10)

    def select_price_for_stock(self, category, color):
        self.clear_frame()
        tk.Label(self.main_frame, text=f"Select Restock Price for {category} - {color}", font=("Arial", 18)).pack(
            pady=10)

        default_prices = [64.34, 82.3, 85.8, 102.94]
        for price in default_prices:
            tk.Button(self.main_frame, text=f"${price}", font=("Arial", 14), height=2,
                      command=lambda p=price: self.restock_and_submit(category, color, p)).pack(fill="x", padx=40,
                                                                                                pady=5)

        tk.Button(self.main_frame, text="Back", font=("Arial", 12),
                  command=lambda: self.select_color_for_stock(category)).pack(pady=10)



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

            #messagebox.showinfo("Success", f"Sale added for ${price}")
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
            #messagebox.showinfo("Success", "Sale added!")
            self.show_mode_selection()

        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def show_info_options(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="INFO Options:", font=("Arial", 18)).pack(pady=20)

        back_btn = tk.Button(self.main_frame, text="Back to Mode Selection", command=self.show_mode_selection)
        back_btn.pack(pady=20)

    def show_sales_and_stock_info(self):
        self.clear_frame()

        # Sorting helper
        def treeview_sort_column(tv, col, reverse):
            data = [(tv.set(k, col), k) for k in tv.get_children('')]
            try:
                data.sort(key=lambda t: float(t[0]) if t[0].replace('.', '', 1).isdigit() else t[0], reverse=reverse)
            except:
                data.sort(reverse=reverse)
            for index, (val, k) in enumerate(data):
                tv.move(k, '', index)
            tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))

        # --- Sales Frame ---
        sales_frame = tk.Frame(self.main_frame, height=150)
        sales_frame.pack(side="top", fill="x", padx=10, pady=(10, 5))
        sales_frame.pack_propagate(False)

        tk.Label(sales_frame, text="Sales", font=("Arial", 14)).pack(pady=5)

        self.sales_tree = ttk.Treeview(sales_frame, columns=("Month", "Store", "Total Sales"), show='headings',
                                       height=5)
        for col in ("Month", "Store", "Total Sales"):
            self.sales_tree.heading(col, text=col,
                                    command=lambda c=col: treeview_sort_column(self.sales_tree, c, False))
        self.sales_tree.pack(fill="x", expand=False)

        # --- Stock Frame ---
        stock_frame = tk.Frame(self.main_frame)
        stock_frame.pack(side="top", fill="both", expand=True, padx=10, pady=(5, 10))

        tk.Label(stock_frame, text="Stock:", font=("Arial", 14)).pack(pady=5)

        self.stock_tree = ttk.Treeview(stock_frame, columns=("Category", "Color", "Quantity"), show='headings')
        for col in ("Category", "Color", "Quantity"):
            self.stock_tree.heading(col, text=col,
                                    command=lambda c=col: treeview_sort_column(self.stock_tree, c, False))
        self.stock_tree.pack(fill="both", expand=True)

        # --- Back Button ---
        back_btn = tk.Button(self.main_frame, text="Back to INFO", command=self.show_mode_selection)
        back_btn.pack(pady=10, fill="x", padx=10)

        # Load data for both
        self.load_sales_data()
        self.load_stock_data()

    def load_sales_data(self):
        data = get_sales_summary("month_store")
        # Clear existing rows
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)

        # Get current month in "YYYY-MM" format
        current_month = datetime.utcnow().strftime("%Y-%m")

        # Filter data for current month only
        current_month_data = [item for item in data if item["month"].startswith(current_month)]

        # Sort by store name or keep as is
        current_month_data_sorted = sorted(current_month_data, key=lambda x: x["store"])

        for item in current_month_data_sorted:
            self.sales_tree.insert("", "end", values=(item["month"], item["store"], f"{item['total_sales']:.2f}"))

    def load_stock_data(self):
        data = get_stock_summary()

        # Clear existing rows
        for row in self.stock_tree.get_children():
            self.stock_tree.delete(row)

        # Insert only items with qty > 0
        for item in data:
            if item.get("qty", 0) > 0:  # ✅ Skip if qty is 0 or missing
                self.stock_tree.insert("", "end", values=(item["category"], item["color"], item["qty"]))

    def show_sales_info(self):
        self.clear_frame()

        tk.Label(self.main_frame, text="Sales Summary Grouped by Month and Acc:", font=("Arial", 14)).pack(pady=5)

        self.sales_tree = ttk.Treeview(self.main_frame, columns=("Month", "Store", "Total Sales"), show='headings')
        self.sales_tree.heading("Month", text="Month")
        self.sales_tree.heading("Shop", text="Acc")
        self.sales_tree.heading("Total Sales", text="Total Sales ($)")
        self.sales_tree.pack(fill="both", expand=True, pady=10)

        back_btn = tk.Button(self.main_frame, text="Back", command=self.show_mode_selection)
        back_btn.pack(pady=10)

        self.load_sales_data()


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



    def show_profits_sales_history(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Summary Grouped by Month:", font=("Arial", 14)).pack(pady=5)

        # Dropdown to select between 'Profits' and 'Costs'
        self.summary_var = tk.StringVar(value="Profits")
        summary_options = ["Profits", "Costs", "History"]
        summary_menu = ttk.Combobox(self.main_frame, values=summary_options, textvariable=self.summary_var,
                                    state="readonly")
        summary_menu.pack(pady=5)
        summary_menu.bind("<<ComboboxSelected>>", lambda e: self.load_summary_data())

        # Treeview setup
        self.summary_tree = ttk.Treeview(self.main_frame)
        self.summary_tree.pack(fill="both", expand=True, pady=10)

        back_btn = tk.Button(self.main_frame, text="Back", command=self.show_mode_selection)
        back_btn.pack(pady=10)

        # Load default data (profits)
        self.load_summary_data()

    def load_summary_data(self):
        selection = self.summary_var.get()

        # Clear existing data and reset tree columns
        for row in self.summary_tree.get_children():
            self.summary_tree.delete(row)

        if selection == "Profits":
            data = get_profits_summary()
            self.summary_tree["columns"] = ("Month", "Profit")
            self.summary_tree.heading("#0", text="")
            self.summary_tree.column("#0", width=0, stretch=False)
            self.summary_tree.heading("Month", text="Month")
            self.summary_tree.heading("Profit", text="Profit ($)")

            for item in data:
                self.summary_tree.insert("", "end", values=(item["month"], f"{item['profit']:.2f}"))

        elif selection == "Costs":
            data = get_costs_summary()
            self.summary_tree["columns"] = ("Month", "Category", "Amount")
            self.summary_tree.heading("#0", text="")
            self.summary_tree.column("#0", width=0, stretch=False)
            self.summary_tree.heading("Month", text="Month")
            self.summary_tree.heading("Category", text="Category")
            self.summary_tree.heading("Amount", text="Amount ($)")

            for item in data:
                self.summary_tree.insert("", "end", values=(item["month"], item["category"], f"{item['amount']:.2f}"))

        elif selection == "History":
            self.summary_tree["columns"] = ("Date", "Type", "Acc", "Category", "Color", "Amount ($)")
            self.summary_tree.heading("#0", text="")
            self.summary_tree.column("#0", width=0, stretch=False)

            for col in self.summary_tree["columns"]:
                self.summary_tree.heading(col, text=col)

            sales = db.collection("sales").stream()
            costs = db.collection("additional_costs").stream()

            records = []

            for doc in sales:
                s = doc.to_dict()
                ts = s.get("timestamp")
                records.append({
                    "type": "Sale",
                    "shop": s.get("shop", ""),
                    "category": s.get("category", ""),
                    "color": s.get("color", ""),
                    "amount": s.get("price", 0),
                    "timestamp": ts or datetime.min  # use min date if missing
                })

            for doc in costs:
                c = doc.to_dict()
                ts = c.get("timestamp")
                records.append({
                    "type": "Cost",
                    "shop": "",
                    "category": c.get("category", ""),
                    "color": "",
                    "amount": -abs(c.get("amount", 0)),
                    "timestamp": ts or datetime.min
                })

            # Sort by timestamp (descending)
            records.sort(key=lambda x: x["timestamp"], reverse=True)

            # Define tag styles
            self.summary_tree.tag_configure("sale", foreground="green")
            self.summary_tree.tag_configure("cost", foreground="red")

            for r in records:
                dt = r["timestamp"].strftime("%Y-%m-%d %H:%M") if isinstance(r["timestamp"], datetime) else ""
                tag = "sale" if r["type"] == "Sale" else "cost"
                self.summary_tree.insert(
                    "", "end",
                    values=(dt, r["type"], r["shop"], r["category"], r["color"], f"{r['amount']:.2f}"),
                    tags=(tag,)
                )

    def load_profits_data(self):
        data = get_profits_summary()
        # Clear treeview rows
        for row in self.profits_tree.get_children():
            self.profits_tree.delete(row)

        self.profits_tree["columns"] = ("Month", "Profit")
        self.profits_tree.heading("Month", text="Month")
        self.profits_tree.heading("Profit", text="Profit ($)")
        self.profits_tree.column("#0", width=0, stretch=False)


        # Data already sorted by month in get_profits_summary, just insert
        for item in data:
            self.profits_tree.insert("", "end", values=(item["month"], f"{item['profit']:.2f}"))


if __name__ == "__main__":
    app = ShopManagerApp()
    app.mainloop()
#nc