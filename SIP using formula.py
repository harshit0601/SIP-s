import json
import numpy as np
from datetime import datetime, timedelta

with open('transaction_detail.json') as f:
    data = json.load(f)

transactions = data['data'][0]['dtTransaction']

profile_min_sip = 10000  
income_bucket_min = 5  
income_bucket_max = 10  

income_bucket_mean = (income_bucket_min + income_bucket_max) / 2
income_threshold = 0.2 * (income_bucket_mean * 100000)  

def parse_date(date_str):
    return datetime.strptime(date_str, '%d-%b-%Y')

two_years_ago = datetime.now() - timedelta(days=730)
recent_transactions = [
    txn for txn in transactions if parse_date(txn['trxnDate']) > two_years_ago
]

investment_amounts = [float(txn['trxnAmount']) for txn in recent_transactions]
investment_dates = [txn['trxnDate'] for txn in recent_transactions]
scheme_names = [txn['schemeName'] for txn in recent_transactions]

# Calculated the SIP threshold using the formula
def calculate_minimum_sip_threshold(investments):
    # Condition 1
    if len(investments) >= 6:
        mean_last_6 = np.mean(investments[-6:])
        threshold_1 = 0.8 * mean_last_6
    else:
        threshold_1 = float('inf')

    # Condition 2
    if len(investments) >= 3:
        mean_last_3 = np.mean(investments[-3:])
        threshold_2 = mean_last_3 if mean_last_3 > 0 else float('inf')
    else:
        threshold_2 = float('inf')

    # Condition 3
    threshold_3 = profile_min_sip

    # Condition 4
    threshold_4 = income_threshold

    return min(threshold_1, threshold_2, threshold_3, threshold_4)

sip_threshold = calculate_minimum_sip_threshold(investment_amounts)

# Here checking SIP status for each transaction
for i, (amount, date, scheme) in enumerate(zip(investment_amounts, investment_dates, scheme_names)):
    if amount >= sip_threshold:
        print(f"SIP done for month: {date}, Scheme: {scheme}, Investment: {amount}")
    else:
        print(f"SIP not done for month: {date}, Scheme: {scheme}, Investment: {amount}") 
