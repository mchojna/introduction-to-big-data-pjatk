import json
import time
import requests

def get_connector_status():
    """Get the status of the Debezium connector"""
    url = "http://kafka-connect:8083/connectors/postgres-connector/status"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            status = response.json()
            print(f"Connector status: {json.dumps(status, indent=2)}")
            return status
        else:
            print(f"Failed to get connector status: {response.text}")
            return None
    except Exception as e:
        print(f"Error getting connector status: {e}")
        return None
    
def get_topics():
    """Get the list of Kafka topics"""
    url = "http://kafka-connect:8083/topics"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            topics = response.json()
            print(f"Kafka topics: {json.dumps(topics, indent=2)}")
            return topics
        else:
            print(f"Failed to get topics: {response.text}")
            return None
    except Exception as e:
        print(f"Error getting topics: {e}")
        return None

if __name__ == "__main__":
    # Wait for the connector to be fully initialized
    time.sleep(60)
    
    # Check connector status
    connector_status = get_connector_status()
    
    # Check topics
    topics = get_topics()
    
    # Check if the connector is running and topics are created
    if connector_status and "tasks" in connector_status:
        for task in connector_status["tasks"]:
            if task["state"] == "RUNNING":
                print("Debezium connector is running successfully")
            else:
                print(f"Debezium connector task is in state: {task['state']}")
