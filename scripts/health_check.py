import os
import time
import json
import requests
import socket
import psycopg2
from confluent_kafka import Consumer
from confluent_kafka.admin import AdminClient

def check_postgres():
    """Check if PostgreSQL is healthy"""
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="business_db",
            user="postgres",
            password="postgres"
        )
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        next_id = result[0] + 1 if result else 1
        cur.close()
        conn.close()
        return result[0] == 1
    except Exception as e:
        print(f"PostgreSQL health check failed: {e}")
        return False

def check_kafka():
    """Check if Kafka is healthy"""
    try:
        admin_client = AdminClient({"bootstrap.servers": "kafka:9092"})
        topics = admin_client.list_topics(timeout=10)
        return topics is not None
    except Exception as e:
        print(f"Kafka health check failed: {e}")
        return False

def check_schema_registry():
    """Check if Schema Registry is healthy"""
    try:
        response = requests.get("http://schema-registry:8081/subjects")
        return response.status_code == 200
    except Exception as e:
        print(f"Schema Registry health check failed: {e}")
        return False

def check_kafka_connect():
    """Check if Kafka Connect is healthy"""
    try:
        response = requests.get("http://kafka-connect:8083/connectors")
        return response.status_code == 200
    except Exception as e:
        print(f"Kafka Connect health check failed: {e}")
        return False

def check_debezium_connector():
    """Check if Debezium connector is healthy"""
    try:
        response = requests.get("http://kafka-connect:8083/connectors/postgres-connector/status")
        if response.status_code == 200:
            status = response.json()
            connector_state = status.get("connector", {}).get("state", "")
            return connector_state == "RUNNING"
        return False
    except Exception as e:
        print(f"Debezium connector health check failed: {e}")
        return False

def check_spark():
    """Check if Spark is healthy"""
    try:
        response = requests.get("http://spark:8080")
        return response.status_code == 200
    except Exception as e:
        print(f"Spark health check failed: {e}")
        return False

def check_minio():
    """Check if MinIO is healthy"""
    try:
        response = requests.get("http://minio:9000/minio/health/live")
        return response.status_code == 200
    except Exception as e:
        print(f"MinIO health check failed: {e}")
        return False

def run_health_checks():
    """Run all health checks and report results"""
    checks = {
        "PostgreSQL": check_postgres,
        "Kafka": check_kafka,
        "Schema Registry": check_schema_registry,
        "Kafka Connect": check_kafka_connect,
        "Debezium Connector": check_debezium_connector,
        "Spark": check_spark,
        "MinIO": check_minio
    }
    
    results = {}
    all_healthy = True
    
    for name, check_func in checks.items():
        try:
            is_healthy = check_func()
            results[name] = "Healthy" if is_healthy else "Unhealthy"
            if not is_healthy:
                all_healthy = False
        except Exception as e:
            results[name] = f"Error: {str(e)}"
            all_healthy = False
    
    print("=== Health Check Results ===")
    for name, status in results.items():
        print(f"{name}: {status}")
    print("============================")
    
    return all_healthy

if __name__ == "__main__":
    print("Starting health check service...")
    
    # Wait for all services to start
    time.sleep(180)
    
    # Run health checks periodically
    while True:
        all_healthy = run_health_checks()
        
        if not all_healthy:
            print("WARNING: Some services are unhealthy!")
        
        # Wait before next check
        time.sleep(60)
