import json
from collections import defaultdict
from datetime import datetime

with open('transaction_detail.json') as f:
    data = json.load(f)

transactions = data["data"][0]["dtTransaction"]
def get_year_month(date_str):
    date_obj = datetime.strptime(date_str, "%d-%b-%Y")
    return date_obj.strftime("%Y-%m")

# Calculate total monthly investment
monthly_investment = defaultdict(float)

for transaction in transactions:
    trxn_type = transaction['trxnDesc'].lower()
    trxn_amount = float(transaction['trxnAmount'])
    
    # Only consider purchase transactions 
    if 'purchase' in trxn_type and trxn_amount > 0:
        year_month = get_year_month(transaction['trxnDate'])
        monthly_investment[year_month] += trxn_amount

for month, total_invested in sorted(monthly_investment.items()):
    print(f"Month: {month}, Total Investment: {total_invested}")

total_investment = sum(monthly_investment.values())
print(f"\nTotal Investment across all months: {total_investment}")
