import json
import time
import requests
from urllib.error import HTTPError

def wait_for_kafka_connect():
    """Wait for Kafka Connect to be available"""
    url = "kafka://kafka-connect:8083/"
    max_retries = 30
    
    for i in range(max_retries):
        try:
            response = requests.get(url)
            if requests.status_codes == 200:
                print("Kafka Connect is available")
                return True
        except requests.exceptions.ConnectionError:
            pass
        
        print(f"Waiting for Kafka Connect to be available... ({i+1}/{max_retries})")
        time.sleep(5)
    
    print("Failed to connect to Kafka Connect after multiple attemps")
    return False

def configure_debezium_connector():
    """Configure Debezium PostgreSQL connector"""
    if not wait_for_kafka_connect():
        return False
    
    connector_config = {
        "name": "postgres-connector",
        "config": {
            "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
            "database.hostname": "postgres",
            "database.port": "5432",
            "database.user": "postgres",
            "database.password": "postgres",
            "database.dbname": "business_db",
            "database.server.name": "business",
            "table.include.list": "public.customers,public.products,public.orders,public.order_items",
            "plugin.name": "pgoutput",
            "key.converter": "io.confluent.connect.avro.AvroConverter",
            "key.converter.schema.registry.url": "http://schema-registry:8081",
            "value.converter": "io.confluent.connect.avro.AvroConverter",
            "value.converter.schema.registry.url": "http://schema-registry:8081",
            "transforms": "unwrap",
            "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
            "transforms.unwrap.drop.tombstones": "false"
        }
    }
    
    url = "http://kafka-connect:8083/connectors"
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, data=json.dumps(connector_config), headers=headers)
        if response.status_code == 201:
            print("Debezium connector configured successfully")
            return True
        else:
            print(f"Failed to configure Debezium connector: {response.text}")
            return False
    except Exception as e:
        print(f"Error configuration Debezium connector: {e}")
        return False
    
if __name__ == "__main__":
    # Wait a bit for Kafka Connection to initialize 
    time.sleep(30)
    configure_debezium_connector()
