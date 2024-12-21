import logging
from pyspark.sql import SparkSession

def create_spark_connection():
    try:
        spark = SparkSession.builder \
            .appName('SparkToElasticSearch') \
            .config("spark.es.nodes", "elasticsearch") \
            .config("spark.es.port", "9200") \
            .config("spark.jars", "/es/elasticsearch-spark-20_2.12-7.13.1.jar") \
            .config("spark.jars.packages", "org.apache.httpcomponents:httpclient:4.5.14") \
            .config("spark.es.index.auto.create", "true") \
            .getOrCreate()
        spark.sparkContext.setLogLevel("ERROR")
        logging.info("Spark connection created successfully!")
        return spark
    except Exception as e:
        logging.error("Failed to create Spark session", exc_info=True)
        return None

def read_from_hdfs(spark):
    hdfs_path = "hdfs://namenode:9000/user/hdfs/created_users/*.parquet"
    try:
        df = spark.read.format("parquet").load(hdfs_path)
        logging.info("DataFrame loaded successfully from HDFS.")
        df.printSchema()
        print(df.count())
        return df
    except Exception as e:
        logging.error("Error while reading data from HDFS", exc_info=True)
        return None

def write_to_elasticsearch(df):
    try:
        df.write.format("org.elasticsearch.spark.sql") \
            .mode("append") \
            .option("es.nodes", "elasticsearch") \
            .option("es.port", "9200") \
            .option("es.nodes.discovery", "false") \
            .option("es.nodes.wan.only", "true") \
            .option("es.index.auto.create", "true") \
            .option("es.mapping.id", "id") \
            .option("es.resource", "index_users") \
            .save()
        logging.info("DataFrame written successfully to Elasticsearch.")
    except Exception as e:
        logging.error("Error while writing to Elasticsearch", exc_info=True)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    spark = create_spark_connection()
    if spark:
        df = read_from_hdfs(spark)
        if df:
            write_to_elasticsearch(df)