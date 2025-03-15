# Prices dictionary
prices = {
    # Cosmetics
    "Bath Soap": 25,
    "Face Cream": 80,
    "Face Wash": 120,
    "Hair Spray": 180,
    "Hair Gel": 140,
    "Body Lotion": 180,
    # Groceries
    "Rice": 50,
    "Dal": 100,
    "Oil": 120,
    "Wheat": 40,
    "Sugar": 45,
    "Tea": 140,
    # Energy Drinks
    "Red Bull": 120,
    "Hurricane": 90,
    "Blue Bull": 100,
    "Ocean": 85,
    "Monster": 110,
    "Coca Cola": 60
}

# Product categories
cosmetic_products = ["Bath Soap", "Face Cream", "Face Wash", "Hair Spray", "Hair Gel", "Body Lotion"]
grocery_products = ["Rice", "Dal", "Oil", "Wheat", "Sugar", "Tea"]
# Make sure drink_products are properly defined
drink_products = [
    "Red Bull",
    "Hurricane",
    "Blue Bull",
    "Ocean",
    "Monster",
    "Coca Cola"
]

# Example structure for product variants
cosmetic_products = {
    "Bath Soap": [
        {"name": "Dove Bath Soap", "price": 45},
        {"name": "Lux Bath Soap", "price": 35},
        {"name": "Pears Bath Soap", "price": 50},
        {"name": "Santoor Bath Soap", "price": 30}
    ],
    "Face Cream": [
        {"name": "Nivea Face Cream", "price": 120},
        {"name": "Ponds Face Cream", "price": 90},
        {"name": "Olay Face Cream", "price": 150}
    ],
    "Face Wash": [
        {"name": "Clean & Clear Face Wash", "price": 85},
        {"name": "Himalaya Face Wash", "price": 70},
        {"name": "Neutrogena Face Wash", "price": 110}
    ],
    "Hair Oil": [
        {"name": "Parachute Hair Oil", "price": 80},
        {"name": "Dabur Amla Hair Oil", "price": 95},
        {"name": "Bajaj Almond Hair Oil", "price": 110}
    ]
}

grocery_products = {
    "Rice": [
        {"name": "Basmati Rice", "price": 80},
        {"name": "Brown Rice", "price": 95},
        {"name": "Jasmine Rice", "price": 85}
    ],
    "Dal": [
        {"name": "Toor Dal", "price": 120},
        {"name": "Moong Dal", "price": 110},
        {"name": "Masoor Dal", "price": 100}
    ],
    "Oil": [
        {"name": "Sunflower Oil", "price": 180},
        {"name": "Olive Oil", "price": 350},
        {"name": "Mustard Oil", "price": 160}
    ],
    "Flour": [
        {"name": "Wheat Flour", "price": 45},
        {"name": "Besan Flour", "price": 60},
        {"name": "Rice Flour", "price": 50}
    ]
}

drink_products = {
    "Energy Drinks": [
        {"name": "Red Bull", "price": 110},
        {"name": "Monster", "price": 120},
        {"name": "Sting", "price": 85}
    ],
    "Soft Drinks": [
        {"name": "Coca Cola", "price": 40},
        {"name": "Pepsi", "price": 40},
        {"name": "Sprite", "price": 38},
        {"name": "Fanta", "price": 38}
    ],
    "Juices": [
        {"name": "Real Fruit Juice", "price": 95},
        {"name": "Tropicana", "price": 90},
        {"name": "Minute Maid", "price": 85}
    ]
}

# For backward compatibility, create a flat price dictionary
prices = {}
for category_dict in [cosmetic_products, grocery_products, drink_products]:
    for product_type, variants in category_dict.items():
        for variant in variants:
            prices[variant["name"]] = variant["price"]