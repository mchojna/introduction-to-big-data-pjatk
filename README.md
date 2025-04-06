# Mini Data Platform in Docker Containers

This project implements a mini data platform using Docker containers that simulates a business process, ingests data into PostgreSQL, captures changes with Debezium, streams data through Kafka, processes it in Spark, and stores it in MinIO in Delta format.

## Architecture

The data platform consists of the following components:

- **Business Simulator**: Simulates a business process by reading data from CSV files and inserting it into PostgreSQL.
- **PostgreSQL**: Stores the business data.
- **Debezium**: Captures changes in PostgreSQL and sends them to Kafka.
- **Kafka**: Streams data between components.
- **Schema Registry**: Manages AVRO schemas for Kafka messages.
- **Spark**: Processes data from Kafka and writes it to MinIO.
- **MinIO**: Stores processed data in Delta format.

## Prerequisites

- Docker and Docker Compose
- At least 8GB of RAM available for Docker
- At least 20GB of free disk space

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/mini-data-platform.git
cd mini-data-platform
```

### 2. Start the Data Platform

```bash
chmod +x startup.sh
./startup.sh
```

This script will:

- Create necessary directories
- Create sample CSV files if they don't exist
- Build and start the Docker containers
- Wait for services to start
- Check if all containers are running

### 3. Access the Services

- PostgreSQL: localhost:5432
- Kafka: localhost:29092
- Schema Registry: <http://localhost:8081>
- Kafka Connect: <http://localhost:8083>
- Spark Master UI: <http://localhost:8080>
- MinIO Console: <http://localhost:9001> (login with minioadmin/minioadmin)

### 4. Verify Data Flow

1. Check that data is being inserted into PostgreSQL:

```bash
docker exec -it postgres psql -U postgres -d business_db -c "SELECT * FROM customers LIMIT 5;"
```

2. Check that Debezium is capturing changes:

```bash
docker exec -it kafka-connect curl -s http://localhost:8083/connectors/postgres-connector/status | jq
```

3. Check that data is being written to MinIO:

Access the MinIO Console at <http://localhost:9001> and navigate to the delta-lake bucket.

### 5. Shutdown the Data Platform

```bash
chmod +x shutdown.sh
./shutdown.sh
```

### Backup and Restore

#### Create a Backup

```bash
chmod +x backup.sh
./backup.sh
```

This will create a backup of PostgreSQL and MinIO data in the backups directory.

#### Restore from a Backup

```bash
chmod +x restore.sh
./restore.sh backups/20230101_120000
```

Replace backups/20230101_120000 with the path to your backup directory.

## Project Structure

mini-data-platform/
├── docker-compose.yml
├── startup.sh
├── shutdown.sh
├── backup.sh
├── restore.sh
├── data/
│   ├── customers.csv
│   ├── orders.csv
│   ├── products.csv
├── scripts/
│   ├── business_simulator.py
│   ├── configure_debezium.py
│   ├── data_generator.py
│   ├── health_check.py
│   ├── kafka_consumer.py
│   ├── models.py
│   ├── read_from_minio.py
│   ├── spark_processor.py
├── Dockerfile.simulator
├── Dockerfile.debezium-config
├── Dockerfile.data-generator
├── Dockerfile.kafka-consumer
├── Dockerfile.spark-processor
├── Dockerfile.minio-reader
├── Dockerfile.health-check
├── requirements.txt
├── README.md

## Troubleshooting

### Check Container Logs

```bash
docker-compose logs [service_name]
```

Replace [service_name] with the name of the service you want to check, e.g., postgres, kafka, etc.

### Check Health Status

The health check service monitors the health of all services. You can check its logs to see if any services are unhealthy:

```bash
docker-compose logs health-check
```

### Restart a Service

If a service is not working correctly, you can restart it:

```bash
docker-compose restart [service_name]
```

### Reset the Data Platform

If you want to reset the data platform and start from scratch:

```bash
docker-compose down -v
./startup.sh
```

This will remove all containers and volumes, and start the data platform from scratch.
