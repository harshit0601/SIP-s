import json
from collections import deque, defaultdict
from datetime import datetime

with open('transaction_detail.json') as file:
    data = json.load(file)

transactions = data['data'][0]['dtTransaction']

def process_yearly_stock_transactions(transactions):
    stock_deques = {}
    purchase_prices = {}
    remaining_units_value = {}
    yearly_investment = {}
    total_yearly_investment = defaultdict(float)  

    for txn in transactions:
        scheme_name = txn['schemeName']
        trxn_units = float(txn['trxnUnits'])
        purchase_price = float(txn['purchasePrice'])
        nav_price = float(txn['purchasePrice'])  
        trxn_date = txn['trxnDate']

        year = datetime.strptime(trxn_date, "%d-%b-%Y").year

        if scheme_name not in stock_deques:
            stock_deques[scheme_name] = deque()
            purchase_prices[scheme_name] = []
            remaining_units_value[scheme_name] = 0.0
            yearly_investment[scheme_name] = {}

        if year not in yearly_investment[scheme_name]:
            yearly_investment[scheme_name][year] = 0.0

        # If stocks are bought, add to the deque and record investment
        if trxn_units > 0:
            stock_deques[scheme_name].append(trxn_units)
            purchase_prices[scheme_name].append(purchase_price)
            remaining_units_value[scheme_name] += trxn_units * nav_price

            # Add the total purchase value to yearly investment for the scheme
            yearly_investment[scheme_name][year] += trxn_units * purchase_price

            # Add to total investment across all schemes for the year
            total_yearly_investment[year] += trxn_units * purchase_price

        # If stocks are sold, process FIFO sale
        elif trxn_units < 0:
            units_to_sell = abs(trxn_units)
            total_cost = 0.0

            # Calculate cost price for the stocks sold using FIFO
            while units_to_sell > 0 and stock_deques[scheme_name]:
                bought_units = stock_deques[scheme_name][0]
                bought_price = purchase_prices[scheme_name][0]

                if bought_units <= units_to_sell:
                    total_cost += bought_units * bought_price
                    units_to_sell -= bought_units
                    stock_deques[scheme_name].popleft()
                    purchase_prices[scheme_name].pop(0)
                else:
                    total_cost += units_to_sell * bought_price
                    stock_deques[scheme_name][0] -= units_to_sell
                    units_to_sell = 0

            remaining_units_value[scheme_name] -= abs(trxn_units) * nav_price

    # Calculate remaining stocks and their value at the end of each year
    for scheme, remaining_units in stock_deques.items():
        remaining_stock_value = sum(u * p for u, p in zip(remaining_units, purchase_prices[scheme]))
        remaining_units_sum = sum(remaining_units)
        print(f"Remaining units for {scheme} at the end of the year: {remaining_units_sum}, Remaining stock value: {remaining_stock_value}")

    for scheme, yearly_data in yearly_investment.items():
        for year, investment in yearly_data.items():
            print(f"Year: {year}, Scheme: {scheme}, Total investment in scheme: {investment}")

    for year, total_investment in total_yearly_investment.items():
        print(f"Total investment in all schemes for the year {year}: {total_investment}")

process_yearly_stock_transactions(transactions)
