import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType

def create_spark_connection():
    """Create Spark session and connection."""
    try:
        spark_conn = SparkSession.builder \
            .appName('KafkaToHDFS') \
            .config('spark.hadoop.hadoop.security.authentication', 'simple') \
            .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
            .config('spark.jars.packages', "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
            .getOrCreate()

        spark_conn.sparkContext.setLogLevel("ERROR")
        logging.info("Spark connection created successfully!")
        print("connected successfully")
        return spark_conn
    except Exception as e:
        logging.error(f"Couldn't create the spark session due to exception: {e}")
        print("error")
        return None

def connect_to_kafka(spark_conn):
    """Read streaming data from Kafka."""
    try:
        kafka_df = spark_conn.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "broker:29092") \
            .option("subscribe", "users_created") \
            .option("failOnDataLoss", "false")  \
            .load()
        logging.info("Kafka DataFrame created successfully")
        return kafka_df

    except Exception as e:
        logging.error(f"Kafka DataFrame could not be created: {e}", exc_info=True)
        print("error")
        return None

def create_selection_df(kafka_df):
    """Transform the Kafka DataFrame to extract JSON fields."""
    schema = StructType([
        StructField("id", StringType(), True),
        StructField("first_name", StringType(), True),
        StructField("last_name", StringType(), True),
        StructField("gender", StringType(), True),
        StructField("address", StringType(), True),
        StructField("post_code", StringType(), True),
        StructField("email", StringType(), True),
        StructField("username", StringType(), True),
        StructField("registered_date", StringType(), True),
        StructField("phone", StringType(), True),
        StructField("picture", StringType(), True)
    ])

    selection_df = kafka_df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")
    
    return selection_df

def write_to_hdfs(selection_df):
    """Write the transformed data to HDFS in Parquet format."""
    try:
        streaming_query = selection_df.writeStream \
            .outputMode("append") \
            .format("parquet") \
            .option("path", "hdfs://namenode:9000/user/hdfs/created_users/") \
            .option("checkpointLocation", "hdfs://namenode:9000/user/hdfs/checkpoints/created_users") \
            .start()

        logging.info("Writing data to HDFS")
        print("Writing data to HDFS")
        streaming_query.awaitTermination()
    except Exception as e:
        logging.error(f"Failed to write to HDFS: {e}", exc_info=True)
        print("Failed to write to HDFS")
if __name__ == "__main__":
    # Step 1: Create Spark session
    spark_conn = create_spark_connection()
    if spark_conn:
        # Step 2: Connect to Kafka and get the streaming DataFrame
        kafka_df = connect_to_kafka(spark_conn)
        if kafka_df:
            # Step 3: Transform the Kafka data to extract useful fields
            selection_df = create_selection_df(kafka_df)
            # Step 4: Write the selected data to HDFS
            write_to_hdfs(selection_df)
