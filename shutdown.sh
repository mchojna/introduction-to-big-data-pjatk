#!/bin/bash
# shutdown.sh

# Stop and remove containers
echo "Stopping and removing containers..."
docker-compose down

# Ask if volumes should be removed
read -p "Do you want to remove all data volumes? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing volumes..."
    docker volume rm $(docker volume ls -q -f name=mini-data-platform)
    echo "Volumes removed."
else
    echo "Volumes preserved."
fi

echo "Shutdown complete."
