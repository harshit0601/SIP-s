import json
from collections import defaultdict

with open('transaction_detail.json') as f:
    data = json.load(f)

transactions = data["data"][0]["dtTransaction"]

scheme_investment = defaultdict(float) 

for transaction in transactions:
    trxn_amount = float(transaction['trxnAmount'])  
    
    # Consider only purchases and positive amounts
    if  trxn_amount > 0:
        scheme_name = transaction['schemeName'].strip().lower()  
        scheme_investment[scheme_name] += trxn_amount  

# Check if all schemes are captured
print(f"Total distinct schemes: {len(scheme_investment)}")

# Print the total invested amount for each scheme
for scheme, total_invested in scheme_investment.items():
    print(f"Scheme: {scheme}, Total Investment: {total_invested}")
