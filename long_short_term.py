import json
from datetime import datetime

with open('transaction_detail.json') as f:
    data = json.load(f)

transactions = data["data"][0]["dtTransaction"]

# Function to calculate the difference in days between two dates
def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%d-%b-%Y")
    d2 = datetime.strptime(d2, "%d-%b-%Y")
    return (d2 - d1).days

# Classify transactions using FIFO
investment_holdings = {}
results = []

for transaction in transactions:
    trxn_date = transaction['trxnDate']
    trxn_type = transaction['trxnDesc'].lower()
    trxn_units = float(transaction['trxnUnits'])
    
    # If it's a purchase, add it to holdings
    if 'purchase' in trxn_type:
        scheme = transaction['scheme']
        if scheme not in investment_holdings:
            investment_holdings[scheme] = []
        investment_holdings[scheme].append((trxn_date, trxn_units))
    
    # If it's a redemption, apply FIFO and classify as short-term or long-term
    elif 'redemption' in trxn_type:
        scheme = transaction['scheme']
        if scheme in investment_holdings:
            units_to_sell = abs(trxn_units)
            while units_to_sell > 0 and investment_holdings[scheme]:
                purchase_date, purchase_units = investment_holdings[scheme].pop(0)
                sold_units = min(units_to_sell, purchase_units)
                units_to_sell -= sold_units
                
                holding_period = days_between(purchase_date, trxn_date)
                investment_class = "Long-Term" if holding_period > 365 else "Short-Term"
                
                results.append({
                    "Scheme": scheme,
                    "Purchase Date": purchase_date,
                    "Redemption Date": trxn_date,
                    "Units Sold": sold_units,
                    "Holding Period (Days)": holding_period,
                    "Classification": investment_class
                })

for result in results:
    print(result)
