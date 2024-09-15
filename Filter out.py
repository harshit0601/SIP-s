import json

with open('transaction_detail.json') as f:
    data = json.load(f)

transactions = data['data'][0]['dtTransaction']

filtered_transactions = [
    txn  
    for txn in transactions
    if txn['scheme'] in [scheme['scheme'] for scheme in data['data'][0]['dtSummary'] 
                         if scheme['assetType'] not in ['EQUITY', 'ELSS']]
]

for txn in filtered_transactions:
    print(json.dumps(txn, indent=4))
    
with open('filtered_non_equity_elss.json', 'w') as f:
    json.dump(filtered_transactions, f, indent=4)  
