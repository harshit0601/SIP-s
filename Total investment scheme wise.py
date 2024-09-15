import json
from collections import defaultdict

# Load the transaction data
with open('transaction_detail.json') as f:
    data = json.load(f)

transactions = data["data"][0]["dtTransaction"]

# Dictionary to store total investment per scheme
scheme_investment = defaultdict(float)

# Loop through transactions and filter only purchase transactions
for transaction in transactions:
    trxn_type = transaction['trxnDesc'].lower()  # Convert transaction description to lowercase for uniformity
    trxn_amount = float(transaction['trxnAmount'])  # Transaction amount
    
    # Consider only purchases and positive amounts
    if 'purchase' in trxn_type and trxn_amount > 0:
        scheme_name = transaction['schemeName'].strip().lower()  # Normalize scheme names by stripping spaces and converting to lowercase
        scheme_investment[scheme_name] += trxn_amount  # Accumulate the investment for the scheme

# Check if all schemes are captured
print(f"Total distinct schemes: {len(scheme_investment)}")

# Print the total invested amount for each scheme
for scheme, total_invested in scheme_investment.items():
    print(f"Scheme: {scheme}, Total Investment: {total_invested}")
