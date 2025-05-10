import requests
import csv
import os
from datetime import datetime, timedelta, timezone
import pytz 

API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_URL = 'https://api.etherscan.io/api'
OUTPUT_FILE = '/host_desktop/eth_p2p_transactions.csv'
MAX_TRANSACTIONS = 10000

def get_block_by_timestamp(timestamp, closest='after'):
    params = {
        'module': 'block',
        'action': 'getblocknobytime',
        'timestamp': timestamp,
        'closest': closest,
        'apikey': API_KEY
    }
    response = requests.get(ETHERSCAN_URL, params=params)
    data = response.json()
    return int(data['result'])

def get_block_transactions(block_number):
    params = {
        'module': 'proxy',
        'action': 'eth_getBlockByNumber',
        'tag': hex(block_number),
        'boolean': 'true',
        'apikey': API_KEY
    }
    response = requests.get(ETHERSCAN_URL, params=params)
    data = response.json()
    result = data.get('result', {})
    transactions = result.get('transactions', [])
    timestamp = int(result.get('timestamp', '0'), 16) if result.get('timestamp') else None
    return transactions, timestamp

def save_to_csv(transactions, filename):
    if not transactions:
        return False

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'txn_id', 'operation_type', 'operation_dttm', 
            'amount_eth', 'wallet', 'block_num',
            'gas_used', 'nonce', 'tx_status'
        ])

        for tx in transactions:
            utc_time = datetime.strptime(tx['parsed_timestamp'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
            msk_time = utc_time.astimezone(pytz.timezone('Europe/Moscow'))
            msk_timestamp_str = msk_time.strftime('%Y-%m-%d %H:%M:%S')

            txn_id = tx['hash']
            block_num = int(tx['blockNumber'], 16)
            amount_eth = int(tx['value'], 16) / 10**18
            gas_used = int(tx['gas'], 16)
            gas_price = int(tx['gasPrice'], 16)
            fee_eth = (gas_used * gas_price) / 10**18
            tx_status = 'success'
            nonce = int(tx['nonce'], 16)

            writer.writerow([
                txn_id, 'send', msk_timestamp_str,
                amount_eth, tx['from'], block_num,
                gas_used, nonce, tx_status
            ])
            writer.writerow([
                txn_id, 'receive', msk_timestamp_str,
                amount_eth, tx['to'], block_num,
                gas_used, nonce, tx_status
            ])
            writer.writerow([
                txn_id, 'fee', msk_timestamp_str,
                fee_eth, tx['from'], block_num,
                gas_used, nonce, tx_status
            ])

def main():
    #Часовой пояс MSK
    msk_tz = pytz.timezone('Europe/Moscow')
    
    #Текущее время по MSK
    now_msk = datetime.now(msk_tz)
    
    #Границы вчершнего дня по MSK
    yesterday_msk = now_msk - timedelta(days=1)
    start_of_day_msk = yesterday_msk.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day_msk = yesterday_msk.replace(hour=23, minute=59, second=59, microsecond=0)
    
    #Перевод границ из MSK в UTC для запроса к API
    start_ts = int(start_of_day_msk.astimezone(timezone.utc).timestamp())
    end_ts = int(end_of_day_msk.astimezone(timezone.utc).timestamp())

    print(f"Выгрузка данных за {yesterday_msk.date()} (MSK)")
    print(f"Диапазон времени в UTC: {start_ts} - {end_ts}")

    start_block = get_block_by_timestamp(start_ts, 'after')
    end_block = get_block_by_timestamp(end_ts, 'before')

    transactions = []
    for block_num in range(start_block, end_block + 1):
        txs, block_ts = get_block_transactions(block_num)
        if not block_ts:
            continue

        utc_time = datetime.utcfromtimestamp(block_ts)
        timestamp_str = utc_time.strftime('%Y-%m-%d %H:%M:%S')

        filtered = [
            {**tx, 'parsed_timestamp': timestamp_str}
            for tx in txs
            if tx.get('to') and int(tx['value'], 16) > 0
        ]

        transactions.extend(filtered)
        print(f"Блок {block_num}: {len(filtered)} P2P транзакций (из {len(txs)} всего)")

        if len(transactions) >= MAX_TRANSACTIONS:
            print(f"Достигнут лимит в {MAX_TRANSACTIONS} транзакций")
            break

    transactions = transactions[:MAX_TRANSACTIONS]

    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    save_to_csv(transactions, OUTPUT_FILE)

if __name__ == "__main__":
    main()
