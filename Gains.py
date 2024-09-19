import json
import requests
from collections import defaultdict
from datetime import datetime
from statistics import mean
from thefuzz import process
from typing import List, Dict, Optional

# Constants for fetching NAV
MFAPI_BASE_URL = 'https://api.mfapi.in/mf/search?q='
TIMEOUT = 5  # Timeout for the HTTP requests in seconds
MAX_SEARCH_WORDS = 10  # Limit on how many words from the input are used in search

# Function to find the closest scheme using fuzzy matching
def find_closest_scheme(input_scheme: str, schemes: List[Dict]) -> Optional[Dict]:
    scheme_names = [scheme['schemeName'] for scheme in schemes]
    closest_match = process.extractOne(input_scheme, scheme_names)
    if closest_match:
        for scheme in schemes:
            if scheme['schemeName'] == closest_match[0]:
                return scheme
    return None

# Fetch the list of schemes based on the search query
def fetch_schemes(search_string: str) -> List[Dict]:
    url = MFAPI_BASE_URL + search_string
    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data from API: {e}")
        return []

# Get the scheme ID for fetching NAV
def get_scheme_id(scheme_name: str) -> Optional[int]:
    search_word_count = MAX_SEARCH_WORDS
    while search_word_count > 0:
        search_words = scheme_name.split(' ')[:search_word_count]
        search_string = '%20'.join(search_words)
        schemes = fetch_schemes(search_string)

        if schemes:
            closest_match = find_closest_scheme(scheme_name, schemes)
            if closest_match:
                scheme_code = closest_match['schemeCode']
                return scheme_code

        search_word_count -= 1
    print(f"No matching scheme found for: {scheme_name}")
    return None

# Fetch the current NAV for the scheme
def fetch_current_nav(scheme_name: str) -> Optional[float]:
    scheme_code = get_scheme_id(scheme_name)
    if scheme_code:
        try:
            scheme_data = requests.get(f'https://api.mfapi.in/mf/{scheme_code}', timeout=TIMEOUT).json()
            return float(scheme_data['data'][-1]['nav'])  # Get the latest NAV
        except requests.exceptions.RequestException as e:
            print(f"Error fetching NAV for {scheme_name}: {e}")
    return None


with open('transaction_detail.json') as f:
    data = json.load(f)

# Part 1: Load JSON and calculate remaining units and total value
remaining_units_by_scheme = defaultdict(list)
total_value_by_scheme = defaultdict(float)

for item in data['data']:
    dt_transaction_list = item.get('dtTransaction', [])
    for transaction in dt_transaction_list:
        scheme_name = transaction.get('schemeName', 'Unknown Scheme')
        trxn_units = float(transaction.get('trxnUnits', 0))
        purchase_price = float(transaction.get('purchasePrice', 0))

        # If it is a purchase (positive units)
        if trxn_units > 0:
            remaining_units_by_scheme[scheme_name].append({'units': trxn_units, 'price': purchase_price})
        # If it is a sale (negative units)
        elif trxn_units < 0:
            units_to_sell = abs(trxn_units)
            while units_to_sell > 0 and remaining_units_by_scheme[scheme_name]:
                oldest_purchase = remaining_units_by_scheme[scheme_name][0]
                if oldest_purchase['units'] <= units_to_sell:
                    units_to_sell -= oldest_purchase['units']
                    remaining_units_by_scheme[scheme_name].pop(0)
                else:
                    oldest_purchase['units'] -= units_to_sell
                    units_to_sell = 0

# Calculate total units and value for each scheme
for scheme, purchases in remaining_units_by_scheme.items():
    total_units_left = 0
    total_value = 0
    for purchase in purchases:
        units_left = purchase['units']
        purchase_price = purchase['price']
        total_units_left += units_left
        total_value += units_left * purchase_price

    total_value_by_scheme[scheme] = {'units_left': total_units_left, 'total_value': total_value}

# Part 2: Calculate gain using current NAV and total value
print("\nCalculating gains...")

for scheme, details in total_value_by_scheme.items():
    units_left = details['units_left']
    total_value = details['total_value']

    # Fetch the current NAV using the scheme name
    current_nav = fetch_current_nav(scheme)

    if current_nav:
        current_value = units_left * current_nav
        gain = total_value - current_value 

        print(f"\nScheme: {scheme}")
        print(f"  Current NAV: {current_nav}")
        print(f"  Units Left: {units_left}")
        print(f"  Invested Value: {total_value:.2f}")
        print(f"  Current Value: {current_value:.2f}")
        print(f"  Gain: {gain:.2f}")
    else:
        print(f"\nScheme: {scheme} - Current NAV not found.")
