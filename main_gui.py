import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os

# ----------------------------
# Configuration / Constants
# ----------------------------
CSV_FILE = "properties.csv"
DEFAULT_TABLE_COLUMNS = ["ID", "Type", "Category", "Location", "Price", "Area", "Bedrooms", "Status"]

# ----------------------------
# Utility: load data
# ----------------------------
def load_data(filename=CSV_FILE):
    if not os.path.exists(filename):
        messagebox.showerror("File not found", f"'{filename}' not found in project folder.")
        return pd.DataFrame(columns=DEFAULT_TABLE_COLUMNS)
    df = pd.read_csv(filename)
    # Ensure expected columns exist (basic normalization)
    for col in DEFAULT_TABLE_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    # Ensure Price is numeric
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0).astype(float)
    return df[DEFAULT_TABLE_COLUMNS]

# ----------------------------
# UI helper: populate treeview
# ----------------------------
def clear_tree(tree):
    for row in tree.get_children():
        tree.delete(row)
# ----------------------------
# UI helper: populate treeview (REPLACE existing clear_tree & populate_tree)
# ----------------------------
def clear_tree(tree):
    for row in tree.get_children():
        tree.delete(row)

def populate_tree(tree, df):
    """
    Generic populater that uses the Treeview's configured columns.
    - Reads tree["columns"] to get the column order.
    - For any numeric 'Price' or 'Average Price' column, formats with commas and ₹.
    - df may have fewer/more columns than DEFAULT_TABLE_COLUMNS.
    """
    if tree is None:
        return

    clear_tree(tree)

    # get columns that the tree expects
    tree_cols = list(tree["columns"])
    if df is None or df.empty:
        return

    # Iterate rows and build a tuple matching tree_cols order
    for _, row in df.iterrows():
        vals = []
        for col in tree_cols:
            # sometimes column names differ in case/spaces; try to access robustly
            if col in df.columns:
                v = row[col]
            else:
                # fallback: try matching ignoring case
                matched = None
                for c in df.columns:
                    if str(c).strip().lower() == str(col).strip().lower():
                        matched = c
                        break
                v = row[matched] if matched is not None else ""

            # Format price-like numbers
            if str(col).strip().lower() in ("price", "average price", "avg price", "avg_price"):
                try:
                    num = float(v)
                    v = f"₹{int(num):,}"
                except Exception:
                    # if it's already a formatted string or empty, keep as-is
                    pass

            vals.append(v)
        tree.insert("", "end", values=vals)














def save_dataframe_to_csv(df):
    if df is None or df.empty:
        messagebox.showinfo("No data", "There is no data to save.")
        return
    path = filedialog.asksaveasfilename(defaultextension=".csv",
                                        filetypes=[("CSV files", "*.csv")],
                                        title="Save results as...")
    if path:
        df.to_csv(path, index=False)
        messagebox.showinfo("Saved", f"Results saved to:\n{path}")

# ----------------------------
# Main Application Class
# ----------------------------
class SmartPropertyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Property System — GUI (Dark Theme)")
        self.geometry("1000x650")
        self.resizable(True, True)
        # Load data
        self.df = load_data()
        # Track last result per tab (for save)
        self.last_result = {}
        # Sort order track
        self.sort_ascending = True

        # Configure dark theme styles
        self._configure_style()
        # Build UI
        self._build_ui()

    # ----------------------------
    # Styling
    # ----------------------------
    def _configure_style(self):
        style = ttk.Style(self)
        # Try to use 'clam' or 'alt' base theme for easier styling
        try:
            style.theme_use('clam')
        except Exception:
            pass

        # general colors
        bg = "#2b2b2b"
        light_bg = "#343434"
        panel_bg = "#222222"
        fg = "#e6e6e6"
        accent = "#3a86ff"  # blue accent

        self.configure(bg=bg)
        style.configure("TFrame", background=panel_bg)
        style.configure("TLabel", background=panel_bg, foreground=fg, font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("TButton", background=light_bg, foreground=fg, font=("Segoe UI", 10), padding=6)
        style.map("TButton",
                  background=[('active', '#3b3b3b')],
                  foreground=[('active', fg)])
        # Treeview styles
        style.configure("Treeview",
                        background="#1f1f1f",
                        foreground=fg,
                        fieldbackground="#1f1f1f",
                        font=("Segoe UI", 10),
                        rowheight=24)
        style.configure("Treeview.Heading", background=panel_bg, foreground=fg, font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[('selected', accent)])
        # Notebook style
        style.configure("TNotebook", background=bg, borderwidth=0)
        style.configure("TNotebook.Tab", background=light_bg, foreground=fg, padding=[10, 6])
        style.map("TNotebook.Tab", background=[("selected", panel_bg)])

    # ----------------------------
    # Build UI
    # ----------------------------
    def _build_ui(self):
        # Top frame (title)
        top = ttk.Frame(self)
        top.pack(side="top", fill="x", padx=10, pady=(10, 0))
        ttk.Label(top, text="Smart Property System", style="Title.TLabel").pack(side="left", padx=6)
        ttk.Label(top, text="(Dark Theme)", foreground="#a0a0a0").pack(side="left")

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tabs
        self._create_all_properties_tab()
        self._create_search_location_tab()
        self._create_filter_category_tab()
        self._create_budget_tab()
        self._create_combined_tab()
        self._create_avg_price_tab()
        self._create_sort_tab()

    # ----------------------------
    # TAB: All Properties
    # ----------------------------
    def _create_all_properties_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="All Properties")

        topbar = ttk.Frame(frame)
        topbar.pack(side="top", fill="x", pady=6, padx=6)
        ttk.Button(topbar, text="Refresh", command=self._refresh_all_properties).pack(side="left", padx=(0, 6))
        ttk.Button(topbar, text="Save Results", command=lambda: self._save_last("all")).pack(side="left")

        tree = self._create_table(frame)
        self.populate_initial_all(tree)
        # store reference
        frame.tree = tree

    def populate_initial_all(self, tree):
        df = self.df.copy()
        # sort by ID
        df = df.sort_values(by="ID")
        populate_tree(tree, df.head(200))  # show top 200 rows
        self.last_result['all'] = df

    def _refresh_all_properties(self):
        self.df = load_data()
        tab = self.notebook.tabs()[0]
        frame = self.nametowidget(tab)
        populate_tree(frame.tree, self.df.head(200))
        self.last_result['all'] = self.df

    # ----------------------------
    # TAB: Search by Location
    # ----------------------------
    def _create_search_location_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Search by Location")

        controls = ttk.Frame(frame)
        controls.pack(side="top", fill="x", padx=6, pady=6)
        ttk.Label(controls, text="Location:").pack(side="left")
        self.loc_entry = ttk.Entry(controls, width=30)
        self.loc_entry.pack(side="left", padx=(6, 12))
        ttk.Button(controls, text="Search", command=self._search_by_location).pack(side="left", padx=(0,6))
        ttk.Button(controls, text="Save Results", command=lambda: self._save_last("loc")).pack(side="left")

        tree = self._create_table(frame)
        frame.tree = tree

    def _search_by_location(self):
        txt = self.loc_entry.get().strip().lower()
        if not txt:
            messagebox.showinfo("Input required", "Please enter a location to search.")
            return
        res = self.df[self.df['Location'].str.lower().str.contains(txt, na=False)].copy()
        populate_tree(self._get_current_tree("Search by Location"), res)
        self.last_result['loc'] = res

    # ----------------------------
    # TAB: Filter by Category
    # ----------------------------
    def _create_filter_category_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Filter by Category")

        controls = ttk.Frame(frame)
        controls.pack(side="top", fill="x", padx=6, pady=6)
        ttk.Label(controls, text="Category:").pack(side="left")
        self.cat_cb = ttk.Combobox(controls, values=["Flat", "PG", "Rent Room"], state="readonly", width=18)
        self.cat_cb.pack(side="left", padx=(6,12))
        ttk.Button(controls, text="Filter", command=self._filter_by_category).pack(side="left", padx=(0,6))
        ttk.Button(controls, text="Save Results", command=lambda: self._save_last("cat")).pack(side="left")

        tree = self._create_table(frame)
        frame.tree = tree

    def _filter_by_category(self):
        cat = self.cat_cb.get().strip()
        if not cat:
            messagebox.showinfo("Input required", "Please select a category.")
            return
        res = self.df[self.df['Category'].str.lower() == cat.lower()].copy()
        populate_tree(self._get_current_tree("Filter by Category"), res)
        self.last_result['cat'] = res

    # ----------------------------
    # TAB: Find by Budget
    # ----------------------------
    def _create_budget_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Find by Budget")

        controls = ttk.Frame(frame)
        controls.pack(side="top", fill="x", padx=6, pady=6)
        ttk.Label(controls, text="Budget (₹):").pack(side="left")
        self.budget_entry = ttk.Entry(controls, width=20)
        self.budget_entry.pack(side="left", padx=(6,12))
        ttk.Button(controls, text="Find", command=self._find_by_budget).pack(side="left", padx=(0,6))
        ttk.Button(controls, text="Save Results", command=lambda: self._save_last("budget")).pack(side="left")

        tree = self._create_table(frame)
        frame.tree = tree

    def _find_by_budget(self):
        raw = self.budget_entry.get().strip().replace(",", "")
        try:
            budget = float(raw)
        except ValueError:
            messagebox.showerror("Invalid input", "Enter a numeric budget (example: 6000000 or 12,000).")
            return
        low = budget * 0.9
        high = budget * 1.1
        res = self.df[(self.df['Price'] >= low) & (self.df['Price'] <= high)].copy()
        populate_tree(self._get_current_tree("Find by Budget"), res)
        self.last_result['budget'] = res

    # ----------------------------
    # TAB: Combined Search
    # ----------------------------
    def _create_combined_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Combined Search")

        controls = ttk.Frame(frame)
        controls.pack(side="top", fill="x", padx=6, pady=6)
        ttk.Label(controls, text="Category:").pack(side="left")
        self.comb_cat = ttk.Combobox(controls, values=["Flat", "PG", "Rent Room"], state="readonly", width=14)
        self.comb_cat.pack(side="left", padx=(6,12))
        ttk.Label(controls, text="Location:").pack(side="left")
        self.comb_loc = ttk.Entry(controls, width=20)
        self.comb_loc.pack(side="left", padx=(6,12))
        ttk.Label(controls, text="Budget (₹):").pack(side="left")
        self.comb_budget = ttk.Entry(controls, width=15)
        self.comb_budget.pack(side="left", padx=(6,12))
        ttk.Button(controls, text="Search", command=self._combined_search).pack(side="left", padx=(0,6))
        ttk.Button(controls, text="Save Results", command=lambda: self._save_last("combined")).pack(side="left")

        tree = self._create_table(frame)
        frame.tree = tree

    def _combined_search(self):
        cat = self.comb_cat.get().strip().lower()
        loc = self.comb_loc.get().strip().lower()
        raw = self.comb_budget.get().strip().replace(",", "")
        try:
            budget = float(raw)
        except ValueError:
            messagebox.showerror("Invalid input", "Enter a numeric budget.")
            return
        low = budget * 0.9
        high = budget * 1.1

        res = self.df[
            (self.df['Category'].str.lower() == cat) &
            (self.df['Location'].str.lower().str.contains(loc, na=False)) &
            (self.df['Price'] >= low) &
            (self.df['Price'] <= high)
        ].copy()
        populate_tree(self._get_current_tree("Combined Search"), res)
        self.last_result['combined'] = res

    # ----------------------------
    # TAB: Average Price by Location
    # ----------------------------
    def _create_avg_price_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Average Price")

        top = ttk.Frame(frame)
        top.pack(side="top", fill="x", padx=6, pady=6)
        ttk.Button(top, text="Compute", command=self._compute_avg_price).pack(side="left", padx=(0,6))
        ttk.Button(top, text="Save Results", command=lambda: self._save_last("avg")).pack(side="left")

        tree = self._create_table(frame, columns=["Location", "Average Price"])
        frame.tree = tree

    def _compute_avg_price(self):
        grouped = self.df.groupby('Location')['Price'].mean().reset_index()
        grouped = grouped.sort_values(by='Price', ascending=False).rename(columns={'Price': 'Average Price'})
        # format average
        grouped['Average Price'] = grouped['Average Price'].apply(lambda x: f"₹{int(x):,}")
        # store raw numeric DF too
        numeric = self.df.groupby('Location')['Price'].mean().reset_index().rename(columns={'Price': 'Average Price'})
        self.last_result['avg'] = numeric
        populate_tree(self._get_current_tree("Average Price"), grouped)

    # ----------------------------
    # TAB: Sort by Price
    # ----------------------------
    def _create_sort_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Sort by Price")

        controls = ttk.Frame(frame)
        controls.pack(side="top", fill="x", padx=6, pady=6)
        self.sort_btn = ttk.Button(controls, text="Toggle Asc/Desc", command=self._toggle_sort)
        self.sort_btn.pack(side="left", padx=(0,6))
        ttk.Button(controls, text="Save Results", command=lambda: self._save_last("sort")).pack(side="left")

        tree = self._create_table(frame)
        frame.tree = tree
        # initial populate with current df
        populate_tree(tree, self.df.sort_values(by="Price", ascending=self.sort_ascending))
        self.last_result['sort'] = self.df.sort_values(by="Price", ascending=self.sort_ascending)

    def _toggle_sort(self):
        self.sort_ascending = not self.sort_ascending
        sorted_df = self.df.sort_values(by="Price", ascending=self.sort_ascending)
        populate_tree(self._get_current_tree("Sort by Price"), sorted_df)
        self.last_result['sort'] = sorted_df

    # ----------------------------
    # Table creation utility
    # ----------------------------
    def _create_table(self, parent, columns=None):
        if columns is None:
            columns = DEFAULT_TABLE_COLUMNS
        # Container
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill="both", expand=True, padx=6, pady=(0,6))
        # Treeview
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        # Setup headings
        for col in columns:
            tree.heading(col, text=col)
            # set column widths
            if col == "Type":
                tree.column(col, width=220, anchor="w")
            elif col == "Location":
                tree.column(col, width=140, anchor="w")
            elif col == "Price":
                tree.column(col, width=120, anchor="e")
            else:
                tree.column(col, width=100, anchor="center")
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        return tree

    # ----------------------------
    # Helpers to get tree for current tab
    # ----------------------------
    def _get_current_tree(self, tab_text):
        # find tab by text
        for tab_id in self.notebook.tabs():
            widget = self.nametowidget(tab_id)
            if self.notebook.tab(tab_id, "text") == tab_text:
                return widget.tree
        # fallback: current tab
        current = self.nametowidget(self.notebook.select())
        return getattr(current, "tree", None)

    def _save_last(self, key):
        df = self.last_result.get(key)
        if df is None or getattr(df, "empty", True):
            messagebox.showinfo("No data", "No results to save for this tab.")
            return
        save_dataframe_to_csv(df)

# ----------------------------
# Run the app
# ----------------------------
if __name__ == "__main__":
    app = SmartPropertyApp()
    app.mainloop()
