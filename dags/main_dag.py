from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from pendulum import timezone

from scripts.extract_data import main as run_extract_script
from scripts.load import load_csv_and_insert_to_db
from scripts.drop_temp_data import drop_temp_tables

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1, tzinfo=timezone("Europe/Moscow")),
    'retries': 0,
}

with DAG(
    dag_id='main',
    default_args=default_args,
    schedule_interval="10 0 * * *",  # каждый день в 00:10 msk
    catchup=False,
    tags=['eth', 'p2p'],
) as dag:

    extract_task = PythonOperator(
        task_id='extract_eth_data',
        python_callable=run_extract_script
    )

    load_to_db_task = PythonOperator(
        task_id='load_to_postgres',
        python_callable=load_csv_and_insert_to_db
    )

    drop_temp_tables_task = PythonOperator(
        task_id='drop_temp_tables',
        python_callable=drop_temp_tables
    )
    
    extract_task >> load_to_db_task >> drop_temp_tables_task
