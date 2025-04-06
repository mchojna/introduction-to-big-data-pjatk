#!/bin/bash
# startup.sh

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker and try again."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Create necessary directories
mkdir -p data
mkdir -p scripts

# Check if CSV files exist
if [ ! -f "data/customers.csv" ] || [ ! -f "data/products.csv" ] || [ ! -f "data/orders.csv" ]; then
    echo "CSV files not found. Creating sample CSV files..."
    
    # Create customers.csv
    echo "customer_id,name,email,registration_date" > data/customers.csv
    echo "1,John Doe,john.doe@example.com,2023-01-01" >> data/customers.csv
    echo "2,Jane Smith,jane.smith@example.com,2023-01-02" >> data/customers.csv
    echo "3,Bob Johnson,bob.johnson@example.com,2023-01-03" >> data/customers.csv
    echo "4,Alice Brown,alice.brown@example.com,2023-01-04" >> data/customers.csv
    echo "5,Charlie Davis,charlie.davis@example.com,2023-01-05" >> data/customers.csv
    
    # Create products.csv
    echo "product_id,name,category,price,stock" > data/products.csv
    echo "101,Laptop,Electronics,999.99,50" >> data/products.csv
    echo "102,Smartphone,Electronics,499.99,100" >> data/products.csv
    echo "103,Headphones,Electronics,99.99,200" >> data/products.csv
    echo "104,Coffee Maker,Home,49.99,75" >> data/products.csv
    echo "105,Blender,Home,39.99,60" >> data/products.csv
    
    # Create orders.csv
    echo "order_id,customer_id,order_date,total_amount" > data/orders.csv
    echo "1001,1,2023-02-01,1099.98" >> data/orders.csv
    echo "1002,2,2023-02-02,499.99" >> data/orders.csv
    echo "1003,3,2023-02-03,139.98" >> data/orders.csv
    echo "1004,1,2023-02-04,49.99" >> data/orders.csv
    echo "1005,4,2023-02-05,539.98" >> data/orders.csv
fi

# Build and start the containers
echo "Starting the data platform..."
docker-compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 30

# Check if all containers are running
if [ $(docker-compose ps -q | wc -l) -ne $(grep -c "container_name:" docker-compose.yml) ]; then
    echo "Some containers failed to start. Please check the logs with 'docker-compose logs'."
    exit 1
fi

echo "Data platform started successfully!"
echo "You can access the following services:"
echo "- PostgreSQL: localhost:5432"
echo "- Kafka: localhost:29092"
echo "- Schema Registry: http://localhost:8081"
echo "- Kafka Connect: http://localhost:8083"
echo "- Spark Master UI: http://localhost:8080"
echo "- MinIO Console: http://localhost:9001"
