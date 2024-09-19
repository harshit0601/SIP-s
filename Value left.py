import json
from collections import defaultdict
from datetime import datetime

with open('transaction_detail.json') as f:
    data = json.load(f)

remaining_units_by_scheme = defaultdict(list)
total_value_by_scheme = defaultdict(float)

for item in data['data']:
    dt_transaction_list = item.get('dtTransaction', [])

    for transaction in dt_transaction_list:
        scheme_name = transaction.get('schemeName', 'Unknown Scheme')
        trxn_units = float(transaction.get('trxnUnits', 0))
        purchase_price = float(transaction.get('purchasePrice', 0))
        trxn_type_flag = transaction.get('trxnTypeFlag', '')
        trxn_date_str = transaction.get('trxnDate')

        # Only consider purchase and sell transactions
       # if trxn_type_flag in ['FP', 'AP', 'APN', 'FR']:

        # If it is a purchase (positive units)
        if trxn_units > 0:
            remaining_units_by_scheme[scheme_name].append({'units': trxn_units, 'price': purchase_price})
            
        # If it is a sale (negative units)
        elif trxn_units < 0:
            # Process sale with FIFO: remove units from the earliest purchase
            units_to_sell = abs(trxn_units)
                
            while units_to_sell > 0 and remaining_units_by_scheme[scheme_name]:
                    # Access the oldest purchase
                    oldest_purchase = remaining_units_by_scheme[scheme_name][0]
                    if oldest_purchase['units'] <= units_to_sell:
                        # Remove the entire purchase batch
                        units_to_sell -= oldest_purchase['units']
                        remaining_units_by_scheme[scheme_name].pop(0)
                    else:
                        # Reduce the units in the oldest batch
                        oldest_purchase['units'] -= units_to_sell
                        units_to_sell = 0

# Now, calculate the total value of remaining units for each scheme
for scheme, purchases in remaining_units_by_scheme.items():
    total_units_left = 0
    total_value = 0

    for purchase in purchases:
        units_left = purchase['units']
        purchase_price = purchase['price']
        total_units_left += units_left
        total_value += units_left * purchase_price
    
    total_value_by_scheme[scheme] = total_value

    print(f"\nScheme: {scheme}")
    print(f"  Total units left: {total_units_left:.3f}")
    print(f"  Total value of remaining units: {total_value:.2f}")

print("\nFinal results:")
for scheme, total_value in total_value_by_scheme.items():
    print(f"{scheme}: Value of remaining units = {total_value:.2f}")
