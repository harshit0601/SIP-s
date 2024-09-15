import json
from collections import defaultdict

with open('transaction_detail.json') as file:
    data = json.load(file)
transactions = data['data'][0]['dtTransaction']

funds_per_year = defaultdict(set)

# Loop through transactions and filter by year, only counting purchases
for transaction in transactions:
    if transaction['trxnDesc'].lower().startswith("purchase"):
        year = transaction['trxnDate'].split("-")[-1]
        funds_per_year[year].add(transaction['schemeName'])

for year in range(2019, 2025):
    year_str = str(year)
    print(f"Year: {year_str}, Number of funds bought: {len(funds_per_year[year_str])}")
