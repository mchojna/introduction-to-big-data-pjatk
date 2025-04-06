import os
import csv
import time
import random
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from data_models import Base, Customer, Product, Order, OrderItem, get_db_session

# Database connection parameters
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSOWRD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "business_db")

# Database connection URL
DB_URL = f"postgresql://{DB_USER}:{DB_PASSOWRD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Paths to CSV files
DATA_DIR = os.getenv("DATA_DIR", "/app/data")
CUSTOMER_CSV = os.path.join(DATA_DIR, "customers.csv")
PRODUCTS_CSV = os.path.join(DATA_DIR, "products.csv")
ORDERS_CSV = os.path.join(DATA_DIR, "orders.csv")

def wait_for_postgres():
    """Wait for PostgreSQL to be available"""
    engine = create_engine(DB_URL)
    max_retries = 30
    for i in range(max_retries):
        try:
            engine.connect()
            print("Successfully connected to PostgreSQL")
            return True
        except Exception as e:
            print(f"Waiting for PostgreSQL to be available... ({i+1}/{max_retries})")
            time.sleep(2)
    
    print("Failed to connect to PostgreSQL after multiple attempts")
    return False

def load_csv_data(file_path):
    """Load data from a CSV file"""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading CSV file {file_path}:{e}")
        return pd.DataFrame()
    
def setup_database():
    """Create database tables"""
    engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)
    print("Database tables created successfully")
    
def insert_customers(session, customers_df):
    """Insert customer data into the database"""
    for _, row in customers_df.iterrows():
        customer = Customer(
            customer_id=row['customer_id'],
            name=row['name'],
            email=row['email'],
            registration_date=datetime.strptime(row['registration_date'], '%Y-%m-%d').date()
        )
        session.add(customer)
    
    session.commit()
    print(f"Inserted {len(customers_df)} customers")
        
def insert_products(session, products_df):
    """Insert product data into the database"""
    for _, row in products_df.iterrow():
        product = Product(
            product_name=row['product_name'],
            name=row['name'],
            category=row['category'],
            price=row['price'],
            stock=row['stock']
        )
        session.add(product)
    
    session.commit()
    print(f"Inserted {len(products_df)} products")
        
def insert_orders(session, orders_df, products_df):
    """Insert order data into the database"""
    for _, row in orders_df.iterrow():
        order = Order(
            order_id=row['order_id'],
            customer_id=row['customer_id'],
            order_date=datetime.strftime(row['order_date'], '%Y-%m-%d').date(),
            total_amount=row['total_amount']
        )
        session.add(order)
        
    # Generate random order items for each order
    num_items = random.randint(1, 3)
    products = products_df.sample(num_items)
    
    for _, product in products.iterrow():
        quantity = random.randint(1, 3)
        order_item = OrderItem(
            order_it=row['order_id'],
            product_id=product['product_id'],
            quantity=quantity,
            price=product['price']
        )
        session.add(order_item)
    
    session.commit()
    print(f"Inserted {len(orders_df)} orders with items")
    
def simulate_business_process():
    """Main function to simulate the business process"""
    print("Starting business process simulation...")
    
    # Wait for PostgreSQL to be available
    if not wait_for_postgres():
        return
    
    # Set up database
    setup_database()
    
    # Create session
    session = get_db_session(DB_URL)
    
    
    try:
        # Load data from CSV file
        customers_df = load_csv_data(CUSTOMER_CSV)
        products_df = load_csv_datA(PRODUCTS_CSV)
        orders_df = load_csv_data(ORDERS_CSV)
        
        if customers_df.empty or products_df.empty or orders_df.empty:
            print("One or more CSV files could not be loaded. Exiting.")
            return
        
        # Insert data into the database
        insert_customers(session, customers_df)
        insert_products(session, products_df)
        insert_orders(session, orders_df, products_df)
        
        print("Business process simulation completed successfully")        
        
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        session.rollback()
    except Exception as e:
        print(f"Error during business process simulation: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    simulate_business_process()