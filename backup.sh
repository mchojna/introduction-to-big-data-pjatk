#!/bin/bash
# backup.sh

# Create backup directory
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup PostgreSQL data
echo "Backing up PostgreSQL data..."
docker exec postgres pg_dump -U postgres -d business_db > $BACKUP_DIR/postgres_backup.sql

# Backup MinIO data
echo "Backing up MinIO data..."
docker run --rm -v $(pwd)/$BACKUP_DIR:/backup --network mini-data-platform_data_platform_network minio/mc \
    /bin/sh -c "mc config host add minio http://minio:9000 minioadmin minioadmin && mc mirror minio/delta-lake /backup/minio"

echo "Backup completed successfully to $BACKUP_DIR"
