import json
from datetime import datetime

with open('transaction_detail.json') as file:
    data = json.load(file)

transactions = data['data'][0]['dtTransaction']

sorted_transactions = sorted(transactions, key=lambda x: datetime.strptime(x['trxnDate'], '%d-%b-%Y'))

data['data'][0]['dtTransaction'] = sorted_transactions

with open('sorted_transactions.json', 'w') as output_file:
    json.dump(data, output_file, indent=4)
