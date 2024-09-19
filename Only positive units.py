import json
from collections import defaultdict
from datetime import datetime

with open('transaction_detail.json') as f:
    data = json.load(f)

# Dictionary to store units bought scheme-wise and year-wise
units_scheme_year = defaultdict(lambda: defaultdict(float))
total_units = 0

for item in data['data']:
    dt_transaction_list = item.get('dtTransaction', [])

    for transaction in dt_transaction_list:
        scheme_name = transaction.get('schemeName', 'Unknown Scheme')
        trxn_units = float(transaction.get('trxnUnits', 0))
        trxn_type_flag = transaction.get('trxnTypeFlag', '')

        # Only consider positive unit values (i.e., purchases), ignore negative values
        if trxn_units > 0 :  
            trxn_date_str = transaction.get('trxnDate')
            trxn_year = datetime.strptime(trxn_date_str, '%d-%b-%Y').year

            # Add the units to the scheme-wise and year-wise dictionary
            units_scheme_year[scheme_name][trxn_year] += trxn_units
            total_units += trxn_units

print("Units bought scheme-wise and year-wise (positive units only):")
for scheme, years in units_scheme_year.items():
    print(f"\nScheme: {scheme}")
    for year, units in years.items():
        print(f"  Year: {year}, Units bought: {units:.3f}")

print(f"\nTotal units bought across all schemes and years: {total_units:.3f}")
 