import os
import time
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_models import Customer, Product, Order, OrderItem

# Database connection parameters
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "business_db")

# Database connection URL
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_session():
    """Create a database session"""
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    return Session()

def generate_customer(session):
    """Generate a new customer"""
    # Get the highest customer id
    result = session.query(Customer).order_by(Customer.customer_id.desc()).first()
    next_id = result.customer_id + 1 if result else 1
    
    # Generate a new customer
    customer = Customer(
        customer_id=next_id,
        name=f"Customer{next_id}",
        email=f"customer{next_id}@example.com",
        registration_date=datetime.now().date()
    )
    
    session.add(customer)
    session.commit()
    print(f"Generated new customer: {customer}")
    return


def generate_order(session):
    customers = session.query(Customer).all()
    if not customers:
        print("No customers found")
        return
    
    customer = random.choice(customers)
    
    # Get the highest order_id
    result = session.query(Order).order_by(Order.order_id.desc()).first()
    next_id = result.order_id + 1 if result else 1
    
    # Get random products
    products = session.query(Product).all()
    if not products:
        print("No products found")
        return

    # Select 1-3 random products
    selected_products = random.sample(products, min(random.randint(1, 3), len(products)))
    
    # Calculated total amount
    total_amount = sum(product.price * random.randint(1, 3) for product in selected_products)
    
    # Create order
    order = Order(
        order_id=next_id,
        customer_id=customer.customer_id,
        order_date=datetime.now().date(),
        total_amount=total_amount
    )
    
    session.add(order)
    session.flush() # Flush to get the order_id
    
    # Create order items
    for product in selected_products:
        quantity = random.randint(1, 3)
        order_item = OrderItem(
            order_id=order.order_id,
            product_id=product.product_id,
            quantity=quantity,
            price=product.price
        )
        session.add(order_item)
        
    session.commit()
    print(f"Generated new order: {order} with {len(selected_products)} items")
    
def update_product_stock(session):
    """Update stock for a random product"""
    # Get a random product
    products = session.query(Product).all()
    if not products:
        print("No products found")
        return
    
    product = random.choice(products)
    
    # Update stock
    old_stock = product.stock
    product.stock = max(0, product.stock + random.randint(-10, 20))
    
    session.commit()
    print(f"Update product {product.name} stock: {old_stock} -> {product.stock}")
    
def generate_data_continuously():
    """Generate data continuously with random intervals"""
    print("Starting continuous data generation...")
    
    while True:
        try:
            session = get_session()
            
            # Randomly choose an action to perform
            action = random.choice(["customer", "order", "product", "order", "product"])
            
            if action == "customer":
                generate_customer(session)
            elif action == "order":
                generate_order(session)
            elif action == "product":
                update_product_stock(session)
                
            # Close connection
            session.close()
            
            # wait for a random interval (2-10 seconds)
            wait_time = random.randint(2, 10)
            print(f"Waiting {wait_time} seconds before next action...")
            time.sleep(wait_time)
            
        except Exception as e:
            print(f"Error generating data: {e}")
            time.sleep(5) # Wait before retrying
            
if __name__ == "__main__":
    # Wait for the database to be ready
    time.sleep(60)
    
    # Generate data continuously
    generate_data_continuously()
