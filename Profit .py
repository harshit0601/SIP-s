import json
from collections import deque

with open('sorted_transactions.json') as file:
    data = json.load(file)

# Function to process transactions and calculate profit and remaining stock value
def process_stock_transactions(transactions):
    stock_transactions = {}

    for txn in transactions:
        scheme_name = txn['schemeName']
        trxn_units = float(txn['trxnUnits'])
        purchase_price = float(txn['purchasePrice'])
        nav_price = float(txn['purchasePrice'])  # Assuming the purchase price as NAV for calculation

        if scheme_name not in stock_transactions:
            stock_transactions[scheme_name] = deque()

        # Push the transaction into the queue (store units, price)
        if trxn_units > 0:
            stock_transactions[scheme_name].append({'units': trxn_units, 'price': purchase_price})
        # Process FIFO sale for sold units
        elif trxn_units < 0:
            units_to_sell = abs(trxn_units)
            total_cost = 0.0
            remaining_units_value = 0.0

            # Process sale by FIFO, pop from the front
            while units_to_sell > 0 and stock_transactions[scheme_name]:
                current_txn = stock_transactions[scheme_name].popleft()
                bought_units = current_txn['units']
                bought_price = current_txn['price']

                if bought_units <= units_to_sell:
                    # If selling all units in this batch
                    total_cost += bought_units * bought_price
                    units_to_sell -= bought_units
                else:
                    # Partially sell units from the current batch
                    total_cost += units_to_sell * bought_price
                    current_txn['units'] -= units_to_sell
                    stock_transactions[scheme_name].appendleft(current_txn)  # Push remaining units back to the front
                    units_to_sell = 0

            remaining_units_value = sum(t['units'] * t['price'] for t in stock_transactions[scheme_name])

            # Calculated profit after the sale: Profit = NAV * sold units - Total cost
            profit = abs(trxn_units) * nav_price - total_cost

            print(f"Sold {abs(trxn_units)} units of {scheme_name}, Total cost: {total_cost}")
            print(f"Remaining units value for {scheme_name}: {remaining_units_value}")
            print(f"Profit after sale: {profit}\n")

    # Print remaining stocks and their value after all transactions
    for scheme, txn_queue in stock_transactions.items():
        remaining_units = sum(t['units'] for t in txn_queue)
        remaining_stock_value = sum(t['units'] * t['price'] for t in txn_queue)
        print(f"Remaining units for {scheme}: {remaining_units}, Remaining stock value: {remaining_stock_value}")

transactions = data['data'][0]['dtTransaction']

process_stock_transactions(transactions)
