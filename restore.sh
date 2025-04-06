#!/bin/bash
# restore.sh

# Check if backup directory is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_directory>"
    exit 1
fi

BACKUP_DIR=$1

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo "Backup directory $BACKUP_DIR does not exist."
    exit 1
fi

# Restore PostgreSQL data
echo "Restoring PostgreSQL data..."
cat $BACKUP_DIR/postgres_backup.sql | docker exec -i postgres psql -U postgres -d business_db

# Restore MinIO data
echo "Restoring MinIO data..."
docker run --rm -v $(pwd)/$BACKUP_DIR:/backup --network mini-data-platform_data_platform_network minio/mc \
    /bin/sh -c "mc config host add minio http://minio:9000 minioadmin minioadmin && mc mirror /backup/minio minio/delta-lake"

echo "Restore completed successfully from $BACKUP_DIR"
