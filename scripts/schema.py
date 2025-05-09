from pyspark.sql import SparkSession

def create_schema_and_table():
    spark = SparkSession.builder \
        .appName("DeployEthereumSchema") \
        .config("spark.jars", "/opt/spark/jars/postgresql-42.6.0.jar") \
        .config("spark.driver.extraClassPath", "/opt/spark/jars/postgresql-42.6.0.jar") \
        .config("spark.executor.extraClassPath", "/opt/spark/jars/postgresql-42.6.0.jar") \
        .getOrCreate()

    url = "jdbc:postgresql://postgres:5432/airflow"
    properties = {
        "user": "airflow",
        "password": "airflow",
        "driver": "org.postgresql.Driver"
    }

    ddl_statements = [
        "CREATE SCHEMA IF NOT EXISTS ethereum_transfers",
        """
        CREATE TABLE IF NOT EXISTS ethereum_transfers.t_fct_transfers (
            txn_id VARCHAR,
            operation_dttm TIMESTAMP,
            amount_eth DECIMAL(38,18),
            fee_eth DECIMAL(38,18),
            sender VARCHAR,
            receiver VARCHAR,
            block_num BIGINT,
            tx_status VARCHAR
        )
        """
    ]

    conn = spark._sc._jvm.java.sql.DriverManager.getConnection(url, properties["user"], properties["password"])
    stmt = conn.createStatement()

    for sql in ddl_statements:
        stmt.execute(sql.strip())

    stmt.close()
    conn.close()

    spark.stop()

