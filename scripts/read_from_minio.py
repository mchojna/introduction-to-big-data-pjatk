from pyspark.sql import SparkSession

def create_spark_session():
    """Create a Spark session with the necessary configurations"""
    return(
        SparkSession
            .builder
            .appName("ReadFromMinIO")
            .master("spark://spark:7077")
            .config(
                "spark.jars.packages",
                "io.delta:delta-core_2.12:2.2.0,"
                "org.apache.hadoop:hadoop-aws:3.3.1"
            )
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
            .config("spark.hadoop.fs.s3a.access.key", "minioadmin")
            .config("spark.hadoop.fs.s3a.secret.key", "minioadmin")
            .config("spark.hadoop.fs.s3a.path.style.access", "true")
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
            .getOrCreate()
    )

def read_from_delta(spark, path):
    """Read data from a Delta table in MinIO"""
    try:
        df = spark.read.format("delta").load(path)
        print(f"Readig from {path}")
        df.show(truncate=False)
        print(f"Schema for {path}")
        df.printSchema()
        print(f"Countr for {path}: {df.count()}")
        return df
    except Exception as e:
        print(f"Error readig from {path}: {e}")
        return None

def main():
    """Main function to read data from MinIO"""
    print("Starting MinIO reader...")
    
    # Create Spark session
    spark = create_spark_session()
    
    # Paths to Delta tables in MinIO
    paths = [
        "s3a://delta-lake/customers",
        "s3a://delta-lake/products",
        "s3a://delta-lake/orders",
        "s3a://delta-lake/order_items",
        "s3a://delta-lake/order_metrics"
    ]
    
    # Read data from each Delta table
    for path in paths:
        read_from_delta(spark, path)
    
    # Stop the Spark session
    spark.stop()
    
if __name__ == "__main__":
    main()
