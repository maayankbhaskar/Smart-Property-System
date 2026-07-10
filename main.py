import pandas as pd
from tabulate import tabulate

# ----------------------- DATA LOADING -----------------------
def load_data(filename="properties.csv"):
    try:
        data = pd.read_csv(filename)
        return data
    except FileNotFoundError:
        print("Error: Database file not found! Make sure 'properties.csv' exists in the project folder.")
        return pd.DataFrame()

# ----------------------- CORE FUNCTIONS -----------------------
def view_all_properties(data):
    if data.empty:
        print("No data available.")
        return
    print("\nAll Properties (first 50 shown):\n")
    print(tabulate(data.head(50), headers="keys", tablefmt="grid", showindex=False))

def search_by_location(data):
    location = input("Enter location/city name: ").strip().lower()
    results = data[data['Location'].str.lower().str.contains(location, na=False)]
    if results.empty:
        print(f"No properties found in {location.title()}.")
    else:
        print(f"\nProperties found in {location.title()}:\n")
        print(tabulate(results, headers="keys", tablefmt="grid", showindex=False))

def filter_by_category(data):
    category = input("Enter category (Flat / PG / Rent Room): ").strip().lower()
    results = data[data['Category'].str.lower() == category]
    if results.empty:
        print(f"No properties found under category '{category.title()}'.")
    else:
        print(f"\n{category.title()} Listings:\n")
        print(tabulate(results, headers="keys", tablefmt="grid", showindex=False))

def find_by_budget(data):
    try:
        budget = float(input("Enter your budget (in ₹): "))
        lower_limit = budget * 0.9
        upper_limit = budget * 1.1
        print(f"\nShowing properties within ₹{lower_limit:,.0f} – ₹{upper_limit:,.0f}\n")

        results = data[(data['Price'] >= lower_limit) & (data['Price'] <= upper_limit)]
        if results.empty:
            print("No properties found within your budget range.")
        else:
            print(tabulate(results, headers="keys", tablefmt="grid", showindex=False))
    except ValueError:
        print("Invalid input! Please enter a numeric budget.")

def combined_search(data):
    category = input("Enter category (Flat / PG / Rent Room): ").strip().lower()
    location = input("Enter location (city or area): ").strip().lower()

    try:
        budget = float(input("Enter your budget (in ₹): "))
    except ValueError:
        print("Invalid input! Please enter a numeric value.")
        return

    lower_limit = budget * 0.9
    upper_limit = budget * 1.1

    results = data[
        (data['Category'].str.lower() == category) &
        (data['Location'].str.lower().str.contains(location, na=False)) &
        (data['Price'] >= lower_limit) &
        (data['Price'] <= upper_limit)
    ]

    print(f"\nSearching for {category.title()}s in {location.title()} within ₹{lower_limit:,.0f} – ₹{upper_limit:,.0f}\n")

    if results.empty:
        print("No matching properties found.")
    else:
        print(tabulate(results, headers="keys", tablefmt="grid", showindex=False))

def sort_by_price(data):
    order = input("Sort by price (asc/desc): ").strip().lower()
    ascending = True if order == "asc" else False
    sorted_data = data.sort_values(by="Price", ascending=ascending)
    print(f"\nProperties sorted by price ({'ascending' if ascending else 'descending'}):\n")
    print(tabulate(sorted_data.head(50), headers="keys", tablefmt="grid", showindex=False))

def avg_price_by_location(data):
    if data.empty:
        print("No data available.")
        return
    grouped = data.groupby('Location')['Price'].mean().sort_values(ascending=False)
    df = grouped.reset_index().rename(columns={'Price':'Average Price'})
    print("\nAverage price by location:\n")
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))

# ----------------------- MAIN MENU -----------------------
def main():
    data = load_data()
    if data.empty:
        return

    while True:
        print("\n" + "-"*50)
        print("🏡  SMART PROPERTY SYSTEM")
        print("-"*50)
        print("1. View All Properties")
        print("2. Search by Location")
        print("3. Filter by Category (Flat / PG / Rent Room)")
        print("4. Find Properties Within Budget")
        print("5. Combined Search (Type + Location + Budget)")
        print("6. Sort Properties by Price")
        print("7. Average Price by Location")
        print("8. Exit")
        print("-"*50)

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            view_all_properties(data)
        elif choice == '2':
            search_by_location(data)
        elif choice == '3':
            filter_by_category(data)
        elif choice == '4':
            find_by_budget(data)
        elif choice == '5':
            combined_search(data)
        elif choice == '6':
            sort_by_price(data)
        elif choice == '7':
            avg_price_by_location(data)
        elif choice == '8':
            print("Exiting Smart Property System. Goodbye!")
            break
        else:
            print("Invalid choice! Please enter a valid option (1–8).")

if __name__ == "__main__":
    main()
