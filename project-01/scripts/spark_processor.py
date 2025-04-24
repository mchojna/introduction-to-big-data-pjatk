import os
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp, window, count, sum
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType

def create_spark_session():
    """Create a Spark session with the necessary configurations"""
    return (SparkSession.builder
                .appName("KafkaSparkProcessor")
                .master("spark://spark:7077")
                .config(
                    "spark.jars.packages",
                    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1,"
                    "org.apache.kafka:kafka-clients:3.3.1,"
                    "io.confluent:kafka-avro-serializer:7.3.0,"
                    "org.apache.spark:spark-avro_2.12:3.3.1,"
                    "io.delta:delta-core_2.12:2.2.0"
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
    
def define_schemas():
    """Define schemas for the Kafka messages"""
    # Customer schema
    customer_schema = StructType(
        [
            StructField("customer_id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("email", StringType(), True),
            StructField("registration_date", StringType(), True)
        ]
    )
    
    # Product schema
    product_schema = StructType(
        [
            StructField("product_id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("category", StringType(), True),
            StructField("price", DoubleType(), True),
            StructField("stock", IntegerType(), True)
        ]
    )
    
    # Order schema
    order_schema = StructType(
        [
                   StructField("order_id", IntegerType(), True),
            StructField("customer_id", IntegerType(), True),
            StructField("order_date", StringType(), True),
            StructField("total_amount", DoubleType(), True)
        ]
    )
    
    # Order item schema
    order_item_schema = StructType(
        [
                    StructField("id", IntegerType(), True),
            StructField("order_id", IntegerType(), True),
            StructField("product_id", IntegerType(), True),
            StructField("quantity", IntegerType(), True),
            StructField("price", DoubleType(), True)
        ]
    )
    
    return {
        "customer": customer_schema,
        "product": product_schema,
        "order": order_schema,
        "order_item": order_item_schema
    }
    
def read_from_kafka(spark, topic, schema):
    """Read data from Kafka topic and parse it according to the schema"""
    return (
        spark
            .readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", "kafka:9092")
            .option("subscribe", topic)
            .option("startingOffsets", "earliest")
            .load()
            .selectExpr("CAST(value AS STRING) as json_value")
            .select(from_json(col("json_value"), schema).alias("data"))
            .select("data.*")
    )
    
def process_customers(spark, schemas):
    """Process customer data from Kafka and write to MinIO in Delta format"""
    customers_df = read_from_kafka(spark, "business.public.customers", schemas["customer"])
    
    # Convert registration_date to timestamp
    customers_df = customers_df.withColumn(
        "registration_date",
        to_timestamp(col("registration_date"), "yyyy-MM-dd")
    )
    
    # Write to console for debugging
    console_query = (
        customers_df
            .writeStream
            .outputMode("append")
            .format("console")
            .start()
    )
    
    # Write to MinIO in Delta format
    delta_query = (
        customers_df
            .writeStream
            .outputMode("append")
            .format("delta")
            .option("checkpointLocation", "s3a://delta-lake/checkpoints/customers")
            .start("s3a://delta-lake/customers")
    )
    
    return [console_query, delta_query]

def process_products(spark, schemas):
    """Process product data from Kafka and write to MinIO in Delta format"""
    products_df = read_from_kafka(spark, "business.public.products", schemas["product"])
    
    # Write to console for debugging
    console_query = (
        products_df
            .writeStream
            .outputMode("append")
            .format("console")
            .start()
    )
    
    # Write to MinIO in Delta format
    delta_query = (
        products_df
            .writeStream
            .outputMode("append")
            .format("delta")
            .option("checkpointLocation", "s3a://delta-lake/checkpoints/products")
            .start("s3a://delta-lake/products")
    )
        
    return [console_query, delta_query]

def process_orders(spark, schemas):
    """Process order data from Kafka and write to MinIO in Delta format"""
    orders_df = read_from_kafka(spark, "business.public.orders", schemas["order"])
    
    # Convert order_data to timestamp
    order_df = orders_df.withColumn(
        "order_date",
        to_timestamp(col("order_date"), "yyyy-MM-dd")
    )
       
    # Write to console for debugging
    console_query = (
        orders_df
             .writeStream
             .outputMode("append")
             .format("console")
             .start()
    )
    
    # Write to MinIO in Delta format
    delta_query = (
        order_df
            .writeStream
            .outputMode("append")
            .format("delta")
            .option("checkpointLocation", "s3a://delta-lake/checkpoints/orders")
            .start("s3a://delta-lake/orders")
    )
    
    return [console_query, delta_query]

def process_order_items(spark, schemas):
    """Process order item data from Kafka and write to MinIO in Delta format"""
    order_items_df = read_from_kafka(spark, "business.public.order_items", schemas["order_item"])
    
    # Write to console for debugging
    console_query = (
        order_items_df
             .writeStream
             .outputMode("append")
             .format("console")
             .start()
    )
    
    # Write to MinIO in Delta format
    delta_query = (
        order_items_df
            .writeStream
            .outputMode("append")
            .format("delta")
            .option("checkpointLocation", "s3a://delta-lake/checkpoints/order_items")
            .start("s3a://delta-lake/order_items")
    )
    
    return [console_query, delta_query]

def analyze_orders_by_window(spark, schemas):
    """Analyze orders by time window and write results to MinIO in Delta format"""
    orders_df = read_from_kafka(spark, "business.public.orders", schemas["order"])
    
    # Convert order_date to timestamp
    orders_df = orders_df.withColumn(
        "order_date",
        to_timestamp(col("order_date"), "yyyy-MM-dd")
    )
    
    # Group by 1-day windows and calculate metrics
    windowed_orders = (
        orders_df
            .withWatermark("order_date", "1 day")
            .groupBy(window(col("order_date"), "1 day"))
            .agg(
                count("order_id").alias("order_count"),
                sum("total_amount").alias("total_sales")
            )
    )
    
    # Write to console for debugging
    console_query = (
        windowed_orders
        .writeStream
        .outputMode("complete")
        .format("console")
        .option("truncate", "false")
        .start()
    )
    
    # Write to MinIO in Delta format
    delta_query = (
        windowed_orders
            .writeStream
            .outputMode("complete")
            .format("delta")
            .option("checkpointLocation", "s3a://delta-lake/checkpoints/order_metrics")
            .start("s3a://delta-lake/order_metrics")
    )
    
    return [console_query, delta_query]


def main():
    """Main function to start the Spark processing"""
    print("Startng Spark processor...")
    
    # Wait for Kafka and other services to be ready
    time.sleep(120)
    
    # Create Spark session
    spark = create_spark_session()
    print(f"Spark version: {spark.version}")
    
    # Defines schemas for Kafka messages
    schemas = define_schemas()
    
    # Process data from Kafka topics and write to MinIO in Delta format
    all_queries = []
    all_queries.extend(process_customers(spark, schemas))
    all_queries.extend(process_products(spark, schemas))
    all_queries.extend(process_orders(spark, schemas))
    all_queries.extend(process_order_items(spark, schemas))
    all_queries.extend(analyze_orders_by_window(spark, schemas))
    
    # Wait for all queries to terminate
    for query in all_queries:
        query.awaitTermination()


if __name__ == "__main__":
    main()
