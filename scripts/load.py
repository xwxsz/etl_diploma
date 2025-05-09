from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def load_csv_and_insert_to_db():
    spark = SparkSession.builder \
        .appName("Transfrom and Load") \
        .config("spark.jars", "/opt/spark/jars/postgresql-42.6.0.jar") \
        .config("spark.driver.extraClassPath", "/opt/spark/jars/postgresql-42.6.0.jar") \
        .getOrCreate()

    df = spark.read.option("header", True).csv("/host_desktop/eth_p2p_transactions.csv")

    db_url = "jdbc:postgresql://postgres:5432/airflow"
    db_props = {
        "user": "airflow",
        "password": "airflow",
        "driver": "org.postgresql.Driver"
    }

    df = df.withColumn("amount_eth", col("amount_eth").cast("decimal(38,18)")) \
           .withColumn("block_num", col("block_num").cast("bigint")) \
           .withColumn("operation_dttm", col("operation_dttm").cast("timestamp"))

    df_send_receive = df.filter(col("operation_type").isin("send", "receive"))
    df_fee = df.filter(col("operation_type") == "fee")

    df_send_receive.write.jdbc(url=db_url, table="ethereum_transfers.transfer_participant", mode="append", properties=db_props)
    df_fee.write.jdbc(url=db_url, table="ethereum_transfers.fee_data", mode="append", properties=db_props)

    df_send = df_send_receive.filter(col("operation_type") == "send").alias("send")
    df_receive = df_send_receive.filter(col("operation_type") == "receive").alias("receive")
    df_fee = df_fee.alias("fee")

    final_df = df_fee.join(df_send, col("fee.txn_id") == col("send.txn_id")) \
                     .join(df_receive, col("fee.txn_id") == col("receive.txn_id")) \
                     .select(
                         col("fee.txn_id"),
                         col("fee.operation_dttm"),
                         col("send.amount_eth").alias("amount_eth"),
                         col("fee.amount_eth").alias("fee_eth"),
                         col("send.wallet").alias("sender"),
                         col("receive.wallet").alias("receiver"),
                         col("fee.block_num"),
                         col("send.tx_status")
                     )

    final_df.write.jdbc(url=db_url, table="ethereum_transfers.t_fct_transfers", mode="append", properties=db_props)

    spark.stop()
