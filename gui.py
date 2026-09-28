import tkinter as tk
from tkinter import messagebox, ttk


LOW_STOCK_LIMIT = 5


class InventoryManagementGUI:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.inventory = controller.inventory
        self.current_page = "Dashboard"
        self.page = None
        self.search_var = tk.StringVar()
        self._search_after = None

        self.root.title("Product Inventory Management System")
        self.root.geometry("1120x740")
        self.root.minsize(860, 600)
        self.root.configure(background="#f3f6f4")

        self._configure_styles()
        self._build_layout()
        self.show_page("Dashboard")

    def _configure_styles(self):
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TFrame", background="#f3f6f4")
        style.configure("TLabel", background="#f3f6f4", foreground="#25332d", font=("Segoe UI", 10))
        style.configure("PageTitle.TLabel", font=("Segoe UI", 18, "bold"), foreground="#172820")
        style.configure("Muted.TLabel", foreground="#6a7971")
        style.configure("Metric.TFrame", background="#ffffff", relief="solid", borderwidth=1)
        style.configure("MetricTitle.TLabel", background="#ffffff", foreground="#617068", font=("Segoe UI", 10))
        style.configure("MetricValue.TLabel", background="#ffffff", foreground="#173f32", font=("Segoe UI", 22, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=(12, 8))
        style.configure("Primary.TButton", background="#176b50", foreground="#ffffff")
        style.map("Primary.TButton", background=[("active", "#12573f")], foreground=[("active", "#ffffff")])
        style.configure("Treeview", rowheight=34, font=("Segoe UI", 10), background="#ffffff", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e8efeb", foreground="#26372f", padding=8)

    def _build_layout(self):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        sidebar = tk.Frame(self.root, bg="#183b30", width=220)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        tk.Label(
            sidebar,
            text="INVENTORY",
            bg="#183b30",
            fg="#ffffff",
            font=("Segoe UI", 15, "bold"),
            anchor="w",
        ).pack(fill="x", padx=22, pady=(28, 4))
        tk.Label(
            sidebar,
            text="Management System",
            bg="#183b30",
            fg="#b7c9c0",
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(fill="x", padx=22, pady=(0, 26))

        self.nav_buttons = {}
        for label in (
            "Dashboard",
            "Add Product",
            "Products",
            "Add Stock",
            "Sell Product",
            "Sales History",
            "Stock History",
        ):
            button = tk.Button(
                sidebar,
                text=label,
                command=lambda page=label: self.show_page(page),
                anchor="w",
                padx=22,
                pady=11,
                relief="flat",
                bd=0,
                cursor="hand2",
                font=("Segoe UI", 10),
                bg="#183b30",
                fg="#e3ece7",
                activebackground="#285544",
                activeforeground="#ffffff",
            )
            button.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[label] = button

        tk.Button(
            sidebar,
            text="Exit",
            command=self.root.destroy,
            anchor="w",
            padx=22,
            pady=11,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 10),
            bg="#183b30",
            fg="#e3ece7",
            activebackground="#285544",
            activeforeground="#ffffff",
        ).pack(side="bottom", fill="x", padx=10, pady=18)

        self.main_area = ttk.Frame(self.root, padding=(30, 24))
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.columnconfigure(0, weight=1)
        self.main_area.rowconfigure(1, weight=1)

        self.header = ttk.Frame(self.main_area)
        self.header.grid(row=0, column=0, sticky="ew", pady=(0, 22))
        self.header.columnconfigure(0, weight=1)
        ttk.Label(
            self.header,
            text="Product Inventory Management System",
            style="PageTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")
        self.subtitle = ttk.Label(self.header, text="", style="Muted.TLabel")
        self.subtitle.grid(row=1, column=0, sticky="w", pady=(5, 0))

        self.page_host = ttk.Frame(self.main_area)
        self.page_host.grid(row=1, column=0, sticky="nsew")
        self.page_host.columnconfigure(0, weight=1)
        self.page_host.rowconfigure(0, weight=1)

    def show_page(self, page_name):
        self.current_page = page_name
        self.subtitle.configure(text=page_name)
        for name, button in self.nav_buttons.items():
            button.configure(bg="#285544" if name == page_name else "#183b30")

        if self.page is not None:
            self.page.destroy()
        self.page = ttk.Frame(self.page_host)
        self.page.grid(row=0, column=0, sticky="nsew")
        self.page.columnconfigure(0, weight=1)
        self.page.rowconfigure(0, weight=1)

        builders = {
            "Dashboard": self._build_dashboard,
            "Add Product": self._build_add_product,
            "Products": self._build_products,
            "Add Stock": self._build_add_stock,
            "Sell Product": self._build_sell_product,
            "Sales History": self._build_sales_history,
            "Stock History": self._build_stock_history,
        }
        builders[page_name]()

    def _build_dashboard(self):
        try:
            stats = self.inventory.get_dashboard_stats(LOW_STOCK_LIMIT)
            values = (
                ("Total Products", f"{stats['total_products']:,}"),
                ("Total Stock", f"{stats['total_stock']:,}"),
                ("Total Sales", f"{stats['total_sales']:,.2f}"),
                ("Low Stock Products", f"{stats['low_stock_products']:,}"),
            )
        except Exception as exc:
            messagebox.showerror("Dashboard unavailable", str(exc), parent=self.root)
            values = (("Total Products", "--"), ("Total Stock", "--"), ("Total Sales", "--"), ("Low Stock", "--"))

        metrics = ttk.Frame(self.page)
        metrics.grid(row=0, column=0, sticky="new")
        for column in range(4):
            metrics.columnconfigure(column, weight=1, uniform="metrics")
        for column, (title, value) in enumerate(values):
            card = ttk.Frame(metrics, style="Metric.TFrame", padding=(16, 17))
            card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 8, 8 if column < 3 else 0))
            ttk.Label(card, text=title, style="MetricTitle.TLabel").pack(anchor="w")
            ttk.Label(card, text=value, style="MetricValue.TLabel").pack(anchor="w", pady=(10, 0))
        ttk.Label(
            self.page,
            text=f"Low-stock items are products with {LOW_STOCK_LIMIT} or fewer units.",
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(18, 0))

    def _form_shell(self, heading, description):
        shell = ttk.Frame(self.page, padding=(24, 22))
        shell.grid(row=0, column=0, sticky="new")
        shell.columnconfigure(0, weight=1)
        ttk.Label(shell, text=heading, style="PageTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(shell, text=description, style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(5, 18))
        return shell

    def _add_form_field(self, parent, row, label, variable=None):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=(0, 6))
        entry = ttk.Entry(parent, textvariable=variable, width=42)
        entry.grid(row=row + 1, column=0, sticky="ew", pady=(0, 14))
        return entry

    def _build_add_product(self):
        shell = self._form_shell("Add Product", "Enter the product details to add it to inventory.")
        form = ttk.Frame(shell)
        form.grid(row=2, column=0, sticky="ew")
        form.columnconfigure(0, weight=1)
        fields = {}
        for row, label in enumerate(("Product ID", "Product Name", "Category", "Price", "Quantity")):
            fields[label] = self._add_form_field(form, row * 2, label)
        fields["Category"].insert(0, "Uncategorized")

        def submit():
            try:
                item = self.controller.add_product(
                    fields["Product Name"].get().strip(),
                    fields["Product ID"].get().strip(),
                    int(fields["Quantity"].get().strip()),
                    float(fields["Price"].get().strip()),
                    fields["Category"].get().strip(),
                )
            except (ValueError, TypeError) as exc:
                messagebox.showerror("Invalid product", str(exc), parent=self.root)
                return
            except Exception as exc:
                messagebox.showerror("Could not add product", str(exc), parent=self.root)
                return

            messagebox.showinfo("Product added", f"{item.name} was added successfully.", parent=self.root)
            for entry in fields.values():
                entry.delete(0, tk.END)

        ttk.Button(form, text="Add Product", style="Primary.TButton", command=submit).grid(row=10, column=0, sticky="w")

    def _build_products(self):
        self.page.columnconfigure(0, weight=1)
        self.page.rowconfigure(1, weight=1)
        toolbar = ttk.Frame(self.page)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        toolbar.columnconfigure(1, weight=1)
        ttk.Label(toolbar, text="Search Product").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.search_var.set("")
        search = ttk.Entry(toolbar, textvariable=self.search_var)
        search.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        search.bind("<KeyRelease>", self._schedule_product_search)
        ttk.Button(toolbar, text="Refresh", command=self._refresh_products).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(toolbar, text="Edit", command=self._edit_selected_product).grid(row=0, column=3, padx=(0, 8))
        ttk.Button(toolbar, text="Delete Product", command=self._delete_selected_product).grid(row=0, column=4)

        table_frame = ttk.Frame(self.page)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        columns = ("id", "name", "category", "price", "quantity")
        self.product_table = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        headings = (("id", "Product ID", 100), ("name", "Product Name", 220), ("category", "Category", 160), ("price", "Price", 120), ("quantity", "Quantity", 100))
        for column, title, width in headings:
            self.product_table.heading(column, text=title)
            self.product_table.column(column, width=width, minwidth=70, anchor="w" if column in ("name", "category") else "center", stretch=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.product_table.yview)
        self.product_table.configure(yscrollcommand=scrollbar.set)
        self.product_table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self._refresh_products()

    def _refresh_products(self):
        if not hasattr(self, "product_table") or not self.product_table.winfo_exists():
            return
        try:
            products = self.inventory.get_products(self.search_var.get())
        except Exception as exc:
            messagebox.showerror("Could not load products", str(exc), parent=self.root)
            return
        for row_id in self.product_table.get_children():
            self.product_table.delete(row_id)
        for item in products:
            values = (item.product_id, item.name, item.category, f"{item.price:.2f}", item.quantity)
            self.product_table.insert("", "end", iid=str(item.product_id), values=values)

    def _schedule_product_search(self, _event=None):
        if self._search_after is not None:
            self.root.after_cancel(self._search_after)
        self._search_after = self.root.after(250, self._refresh_products)

    def _edit_selected_product(self):
        selected = self.product_table.selection()
        if not selected:
            messagebox.showwarning("Select a product", "Choose a product in the table first.", parent=self.root)
            return
        try:
            item = self.inventory.find_product(int(selected[0]))
        except Exception as exc:
            messagebox.showerror("Could not load product", str(exc), parent=self.root)
            return
        if item is None:
            messagebox.showerror("Product not found", "The product no longer exists.", parent=self.root)
            self._refresh_products()
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Product")
        dialog.transient(self.root)
        dialog.resizable(False, False)
        form = ttk.Frame(dialog, padding=22)
        form.grid(row=0, column=0, sticky="nsew")
        form.columnconfigure(0, weight=1)
        ttk.Label(form, text=f"Product ID: {item.product_id}").grid(row=0, column=0, sticky="w", pady=(0, 14))
        name = self._add_form_field(form, 1, "Product Name")
        name.insert(0, item.name)
        category = self._add_form_field(form, 3, "Category")
        category.insert(0, item.category)
        price = self._add_form_field(form, 5, "Price")
        price.insert(0, str(item.price))

        def save():
            try:
                updated = self.inventory.update_product(
                    item.product_id,
                    name.get().strip(),
                    float(price.get().strip()),
                    category.get().strip(),
                )
                if not updated:
                    raise LookupError("Product not found.")
            except (ValueError, LookupError) as exc:
                messagebox.showerror("Could not update product", str(exc), parent=dialog)
                return
            except Exception as exc:
                messagebox.showerror("Could not update product", str(exc), parent=dialog)
                return
            dialog.destroy()
            self._refresh_products()
            messagebox.showinfo("Product updated", "Product details updated successfully.", parent=self.root)

        ttk.Button(form, text="Save Changes", style="Primary.TButton", command=save).grid(row=7, column=0, sticky="w")
        dialog.grab_set()
        name.focus_set()

    def _build_sales_history(self):
        self._build_history_table(
            "Sales History",
            self.inventory.get_sales_history,
            (
                ("sale_id", "Sale ID", 85),
                ("product_id", "Product ID", 95),
                ("product_name", "Product Name", 180),
                ("quantity", "Quantity", 85),
                ("price", "Price", 105),
                ("total_amount", "Total Amount", 125),
                ("sale_date", "Sale Date", 170),
            ),
        )

    def _build_stock_history(self):
        self._build_history_table(
            "Stock History",
            self.inventory.get_stock_history,
            (
                ("stock_id", "Stock ID", 95),
                ("product_id", "Product ID", 110),
                ("quantity_added", "Quantity Added", 150),
                ("stock_date", "Date", 190),
            ),
        )

    def _build_history_table(self, title, data_loader, columns):
        self.page.columnconfigure(0, weight=1)
        self.page.rowconfigure(1, weight=1)
        toolbar = ttk.Frame(self.page)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        ttk.Label(toolbar, text=title, style="PageTitle.TLabel").pack(side="left")
        ttk.Button(
            toolbar,
            text="Refresh",
            command=lambda: self._refresh_history(table, data_loader, columns),
        ).pack(side="right")
        table_frame = ttk.Frame(self.page)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        keys = tuple(column[0] for column in columns)
        table = ttk.Treeview(table_frame, columns=keys, show="headings")
        for key, heading, width in columns:
            table.heading(key, text=heading)
            table.column(key, width=width, minwidth=70, stretch=True, anchor="w" if key == "product_name" else "center")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self._refresh_history(table, data_loader, columns)

    def _refresh_history(self, table, data_loader, columns):
        try:
            rows = data_loader()
        except Exception as exc:
            messagebox.showerror("Could not load history", str(exc), parent=self.root)
            return
        for row_id in table.get_children():
            table.delete(row_id)
        for row in rows:
            values = []
            for key, _heading, _width in columns:
                value = row[key]
                if hasattr(value, "strftime"):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                elif key in ("price", "total_amount"):
                    value = f"{value:,.2f}"
                values.append(value)
            table.insert("", "end", values=values)

    def _delete_selected_product(self):
        selected = self.product_table.selection()
        if not selected:
            messagebox.showwarning("Select a product", "Choose a product in the table first.", parent=self.root)
            return
        product_id = selected[0]
        if not messagebox.askyesno("Delete Product", f"Delete product {product_id}?", parent=self.root):
            return
        try:
            deleted = self.inventory.remove_product(product_id)
            if not deleted:
                messagebox.showerror("Product not found", "The product could not be found.", parent=self.root)
                self._refresh_products()
                return
        except Exception as exc:
            messagebox.showerror("Could not delete product", str(exc), parent=self.root)
            return
        self._refresh_products()
        messagebox.showinfo("Product deleted", "The product was deleted.", parent=self.root)

    def _build_add_stock(self):
        shell = self._form_shell("Add Stock", "Increase the quantity for an existing product.")
        form = ttk.Frame(shell)
        form.grid(row=2, column=0, sticky="ew")
        form.columnconfigure(0, weight=1)
        product_id = self._add_form_field(form, 0, "Product ID")
        quantity = self._add_form_field(form, 2, "Quantity to Add")

        def submit():
            try:
                changed = self.inventory.add_stock(int(product_id.get().strip()), int(quantity.get().strip()))
                if not changed:
                    raise LookupError("Product not found.")
            except (ValueError, LookupError) as exc:
                messagebox.showerror("Could not add stock", str(exc), parent=self.root)
                return
            except Exception as exc:
                messagebox.showerror("Could not add stock", str(exc), parent=self.root)
                return
            messagebox.showinfo("Stock updated", "Stock added successfully.", parent=self.root)
            product_id.delete(0, tk.END)
            quantity.delete(0, tk.END)
            self._refresh_after_change()

        ttk.Button(form, text="Add Stock", style="Primary.TButton", command=submit).grid(row=4, column=0, sticky="w")

    def _build_sell_product(self):
        shell = self._form_shell("Sell Product", "Record a sale and reduce the available stock.")
        form = ttk.Frame(shell)
        form.grid(row=2, column=0, sticky="ew")
        form.columnconfigure(0, weight=1)
        product_id = self._add_form_field(form, 0, "Product ID")
        quantity = self._add_form_field(form, 2, "Quantity to Sell")

        def submit():
            try:
                revenue = self.inventory.sell_product(int(product_id.get().strip()), int(quantity.get().strip()))
            except (ValueError, LookupError) as exc:
                messagebox.showerror("Could not complete sale", str(exc), parent=self.root)
                return
            except Exception as exc:
                messagebox.showerror("Could not complete sale", str(exc), parent=self.root)
                return
            messagebox.showinfo("Sale complete", f"Sale successful. Total: {revenue:.2f}", parent=self.root)
            product_id.delete(0, tk.END)
            quantity.delete(0, tk.END)
            self._refresh_after_change()

        ttk.Button(form, text="Sell Product", style="Primary.TButton", command=submit).grid(row=4, column=0, sticky="w")

    def _refresh_after_change(self):
        if self.current_page == "Dashboard":
            self.show_page("Dashboard")
        elif self.current_page == "Products":
            self._refresh_products()
        elif self.current_page == "Sales History":
            self.show_page("Sales History")
        elif self.current_page == "Stock History":
            self.show_page("Stock History")


def launch_gui(app_factory):
    root = tk.Tk()
    root.withdraw()
    try:
        controller = app_factory()
    except Exception as exc:
        messagebox.showerror(
            "Startup failed",
            f"Could not start the inventory system. Check the database connection.\n\n{exc}",
            parent=root,
        )
        root.destroy()
        return
    root.deiconify()
    InventoryManagementGUI(root, controller)
    root.mainloop()