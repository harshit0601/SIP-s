import json
from collections import defaultdict
from datetime import datetime
with open('transaction_detail.json') as f:
    data = json.load(f)

units_scheme_year = defaultdict(lambda: defaultdict(float))
total_units = 0
for item in data['data']:
    dt_transaction_list = item.get('dtTransaction', [])

    for transaction in dt_transaction_list:
        scheme_name = transaction.get('schemeName', 'Unknown Scheme')
        trxn_units = float(transaction.get('trxnUnits', 0))
        trxn_date_str = transaction.get('trxnDate')
        trxn_year = datetime.strptime(trxn_date_str, '%d-%b-%Y').year

        # Add or subtract the units to the scheme-wise and year-wise dictionary
        units_scheme_year[scheme_name][trxn_year] += trxn_units

        # Keep a running total of all units (positive and negative)
        total_units += trxn_units

print("Total units scheme-wise and year-wise (including both positive and negative units):")
for scheme, years in units_scheme_year.items():
    scheme_total = 0
    print(f"\nScheme: {scheme}")
    for year, units in years.items():
        print(f"  Year: {year}, Total units: {units:.3f}")
        scheme_total += units
    print(f"Total units for {scheme}: {scheme_total:.3f}")

print(f"\nGrand total units across all schemes and years: {total_units:.3f}")
