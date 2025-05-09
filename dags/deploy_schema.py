from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from scripts.schema import create_schema_and_table

with DAG(
    dag_id="deploy_schema",
    start_date=datetime(2023, 1, 1),
    catchup=False,
    schedule_interval=None,
    tags=["init", "schema"]
) as dag:

    deploy_task = PythonOperator(
        task_id="create_schema_and_table",
        python_callable=create_schema_and_table
    )


