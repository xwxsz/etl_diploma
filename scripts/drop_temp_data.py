import psycopg2

def drop_temp_tables():
    conn = psycopg2.connect(
        host='postgres',
        port=5432,
        dbname='airflow',
        user='airflow',
        password='airflow'
    )

    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS ethereum_transfers.fee_data;")
        cur.execute("DROP TABLE IF EXISTS ethereum_transfers.transfer_participant;")
        conn.commit()

    conn.close()
