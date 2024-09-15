import json

with open('transaction_detail.json') as f:
    data = json.load(f)

transactions = data['data'][0]['dtTransaction']

filtered_transactions = [
    {
        'schemeName': txn['schemeName'],
        'trxnDate': txn['trxnDate']
    }
    for txn in transactions
    if txn['scheme'] in [scheme['scheme'] for scheme in data['data'][0]['dtSummary'] 
                         if scheme['assetType'] in ['EQUITY', 'ELSS']]
]

for txn in filtered_transactions:
    print(f"Scheme Name: {txn['schemeName']}, Transaction Date: {txn['trxnDate']}")

with open('filtered_equity_elss.json', 'w') as f:
    json.dump(filtered_transactions, f, indent=4)
