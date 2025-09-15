from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker
import random
from app.db.schemas import Base, User, Customer, ProductCategory, Product, Transaction, TransactionItem
import os
from decimal import Decimal
import uuid

# Define the database URL from an environment variable or a default value.
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://ecommerce:Niffier2025@localhost:5433/ecommerce"
)

# Create the database engine and a session factory.
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

fake = Faker("id_ID")  # Using Indonesian locale for realistic data.

# A dictionary mapping product categories to a list of product names.
CATEGORY_PRODUCTS = {
    "Electronics": [
        "Laptop", "Smartphone", "Headphones", "Smartwatch", "Camera",
        "Tablet", "Monitor", "Printer", "Keyboard", "Mouse"
    ],
    "Clothing": [
        "T-shirt", "Jeans", "Dress", "Jacket", "Shoes",
        "Sweater", "Skirt", "Shorts", "Socks", "Cap"
    ],
    "Groceries": [
        "Milk", "Bread", "Eggs", "Cheese", "Fruits", "Vegetables",
        "Rice", "Cooking Oil", "Sugar", "Snacks", "Coffee", "Tea"
    ],
    "Books": [
        "Novel", "Science", "History", "Biography", "Comic",
        "Children Book", "Dictionary", "Textbook", "Magazine"
    ],
    "Sports": [
        "Football", "Tennis Racket", "Basketball", "Shoes", "Fitness Band",
        "Yoga Mat", "Dumbbell", "Cycling Helmet", "Swimwear"
    ],
    "Home Appliances": [
        "Refrigerator", "Washing Machine", "Microwave", "Blender", "Rice Cooker",
        "Vacuum Cleaner", "Air Conditioner", "Fan", "Water Dispenser"
    ],
    "Beauty & Personal Care": [
        "Shampoo", "Conditioner", "Body Lotion", "Perfume", "Lipstick",
        "Makeup Kit", "Face Wash", "Sunscreen", "Hair Dryer"
    ],
    "Toys & Games": [
        "Action Figure", "Board Game", "Doll", "Puzzle", "RC Car",
        "LEGO Set", "Toy Gun", "Drone Mini", "Play-Doh"
    ],
    "Furniture": [
        "Sofa", "Dining Table", "Chair", "Bed", "Wardrobe",
        "Bookshelf", "Desk", "TV Stand", "Mattress"
    ],
    "Automotive": [
        "Motorcycle Helmet", "Car Tire", "Car Battery", "Engine Oil",
        "Wiper Blade", "Car Seat Cover", "Spark Plug"
    ],
}

# A dictionary mapping categories to a price range for products.
CATEGORY_PRICE_RANGE = {
    "Electronics": (1_000_000, 15_000_000),
    "Clothing": (50_000, 1_000_000),
    "Groceries": (5_000, 500_000),
    "Books": (30_000, 500_000),
    "Sports": (100_000, 5_000_000),
    "Home Appliances": (300_000, 5_000_000),
    "Beauty & Personal Care": (20_000, 3_000_000),
    "Toys & Games": (50_000, 2_000_000),
    "Furniture": (500_000, 10_000_000),
    "Automotive": (100_000, 10_000_000),
}


def random_date_within_last_year():
    """Generates a random date within the last year."""
    return fake.date_between(start_date="-1y", end_date="today")


def seed():
    """Seeds the database with fake data for a retail store."""
    print("Seeding database...")
    
    # Drop and create tables based on the schema definition.
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Seed 10 users.
    users = []
    for _ in range(10):
        user = User(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            password_hash="hashed_password",
        )
        users.append(user)
    session.add_all(users)
    session.commit()
    print(f"Seeded {len(users)} users.")

    # Seed 500 customers.
    customers = []
    for i in range(500):
        customer = Customer(
            customer_code=f"CUST-{1000+i}",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            phone=fake.phone_number(),
            gender=random.choice(["Male", "Female"]),
            age=random.randint(18, 70),
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=70),
            address=fake.address(),
        )
        customers.append(customer)
    session.add_all(customers)
    session.commit()
    print(f"Seeded {len(customers)} customers.")

    # Seed product categories.
    categories = []
    for cat_name in CATEGORY_PRODUCTS.keys():
        # FIX: Generate a more descriptive sentence based on the category name
        description = f"Explore our comprehensive range of high-quality {cat_name.lower()} products, from everyday essentials to premium items."
        cat = ProductCategory(name=cat_name, description=description)
        categories.append(cat)
    session.add_all(categories)
    session.commit()
    print(f"Seeded {len(categories)} product categories.")

    # Seed products for each category.
    products = []
    for cat in categories:
        for prod_name in CATEGORY_PRODUCTS[cat.name]:
            price_range = CATEGORY_PRICE_RANGE[cat.name]
            price = Decimal(random.randint(*price_range))
            cost = price * Decimal("0.7")  # Assume cost is 70% of the price

            sku = f"{cat.name.upper()[:3]}-{prod_name.upper()[:3]}-{fake.unique.random_number(digits=5)}"
            description = fake.paragraph(nb_sentences=2)
            
            
            product = Product(
                name=prod_name,
                description=description,
                sku=sku,
                category_id=cat.id,
                price_per_unit=price,
                cost_per_unit=cost,
                stock_quantity=random.randint(50, 500),
                min_stock_level=random.randint(1, 10)
            )
            products.append(product)
    session.add_all(products)
    session.commit()
    print(f"Seeded {len(products)} products.")

    # Seed transactions for each customer.
    print("Seeding transactions and transaction items...")
    for customer in customers:
        num_trx = random.randint(1, 20)
        for _ in range(num_trx):
            trx_date = random_date_within_last_year()
            trx_number = f"TRX-{uuid.uuid4().hex[:8].upper()}"

            trx = Transaction(
                transaction_number=trx_number,
                transaction_date=trx_date,
                customer_id=customer.id,
            )
            session.add(trx)
            # Use session.flush() to get the transaction's ID before committing
            session.flush()

            subtotal = Decimal(0)
            num_items = random.randint(1, 5)

            for _ in range(num_items):
                product = random.choice(products)
                qty = random.randint(1, 3)
                discount = Decimal(random.choice([0, 0, 0, 5000, 10000]))
                line_subtotal = (product.price_per_unit - discount) * qty

                item = TransactionItem(
                    transaction_id=trx.id,
                    product_id=product.id,
                    quantity=qty,
                    price_per_unit=product.price_per_unit,
                    discount_per_unit=discount,
                    subtotal=line_subtotal,
                )
                subtotal += line_subtotal
                session.add(item)

            # Calculate and set the final amounts for the transaction
            tax_amount = subtotal * Decimal("0.1")
            trx.subtotal = subtotal
            trx.tax_amount = tax_amount
            trx.total_amount = subtotal + tax_amount
    
    session.commit()
    print("✅ Retail database seeded successfully!")


if __name__ == "__main__":
    seed()
