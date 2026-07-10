import pandas as pd
import random

# City-wise base price multiplier (makes dataset more realistic)
city_multiplier = {
    "Mumbai": 1.5,
    "Bangalore": 1.3,
    "Delhi": 1.1,
    "Gurgaon": 1.05,
    "Noida": 1.0,
    "Pune": 0.95,
    "Hyderabad": 0.9,
    "Chennai": 0.85,
    "Kolkata": 0.8,
    "Ahmedabad": 0.75
}

categories = ["Flat", "PG", "Rent Room"]
types_flat = ["1BHK Flat", "2BHK Flat", "3BHK Flat", "Studio Apartment", "4BHK Villa"]
types_pg = ["PG Single Sharing", "PG Double Sharing", "PG Triple Sharing"]
types_room = ["1RK Room", "Rent Room", "Shared Room"]
locations = list(city_multiplier.keys())
status_options = ["Furnished", "Semi-Furnished", "Unfurnished"]

data = []
num_entries = 120

for i in range(1, num_entries + 1):
    category = random.choice(categories)
    city = random.choice(locations)
    mult = city_multiplier.get(city, 1.0)

    if category == "Flat":
        ptype = random.choice(types_flat)
        # base between 40L to 1.2Cr (in rupees)
        base_price = random.randint(4_000_000, 12_000_000)
        price = int(base_price * mult)
        area = random.randint(700, 2500)
        bedrooms = random.choice([1, 2, 3, 4])
    elif category == "PG":
        ptype = random.choice(types_pg)
        base_price = random.randint(6_000, 18_000)
        price = int(base_price * mult * 0.01) if mult > 1.2 else int(base_price * (mult))
        # ensure PG prices remain realistic — scale a bit
        if price < 3000:
            price = random.randint(5000, 20000)
        area = random.randint(120, 300)
        bedrooms = 1
    else:  # Rent Room
        ptype = random.choice(types_room)
        base_price = random.randint(5_000, 12_000)
        price = int(base_price * mult * 0.9)
        area = random.randint(180, 400)
        bedrooms = 1

    entry = {
        "ID": i,
        "Type": ptype,
        "Category": category,
        "Location": city,
        "Price": price,
        "Area": area,
        "Bedrooms": bedrooms,
        "Status": random.choice(status_options)
    }
    data.append(entry)

df = pd.DataFrame(data)
df.to_csv("properties.csv", index=False)
print(f"✅ Generated {len(df)} property records in 'properties.csv'")
