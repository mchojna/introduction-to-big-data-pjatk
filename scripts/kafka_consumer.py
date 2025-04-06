import os
import json
import time
from confluent_kafka import Consumer
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError

def create_avro_consumer():
    """Create an AVRO consumer"""
    config = {
        "bootstrap.servers": "kafka:9002",
        "group.id": "kafka-consumer-group",
        "auto.offset.reset": "earliest",
        "schema.registry.url": "http://schema-registry:8081"
    }
    
    return AvroConsumer(config)

def consume_messages(topics):
    """Consume messages from Kafka topics"""
    consumer = create_avro_consumer()
    consumer.subscribe(topics)
    
    try:
        while True:
            try:
                msg = consumer.poll(1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue
                
                print(f"Topic: {msg.topic()}, Partition: {msg.partition()}, Offset: {msg.offset()}")
                print(f"Key: {msg.key()}")
                print(f"Value: {json.dumps(msg.value(), indent=2)}")
                print("-" * 50)
            
            except SerializerError as e:
                print(f"Message deserialization failed: {e}")
        
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    # Wait for topics to be created
    time.sleep(90)
    
    # Topics to consume from
    topics = [
        "business.public.customer",
        "business.public.products",
        "business.public.orders",
        "business.public.order_items"
    ]
    
    consume_messages(topics)