import json
from datetime import datetime
from collections import defaultdict
from statistics import mean
import calendar

with open('sorted_transactions.json') as file:
    data = json.load(file)

transactions = data['data'][0]['dtTransaction']
scheme_details = data['data'][0]['dtSummary']

monthly_totals = defaultdict(float)

scheme_asset_type = {scheme['scheme']: scheme['assetType'] for scheme in scheme_details}

# Calculate monthly totals (exclude EQUITY and ELSS)
for transaction in transactions:
    trxn_amount = float(transaction['trxnAmount'])
    scheme_code = transaction['scheme']
    
    asset_type = scheme_asset_type.get(scheme_code, "")
    
    # Skip negative amounts and exclude asset types 'EQUITY' or 'ELSS'
    if trxn_amount > 0 and asset_type in ['EQUITY', 'ELSS']:
        trxn_date = datetime.strptime(transaction['trxnDate'], '%d-%b-%Y')
        
        month_year = trxn_date.strftime('%b-%Y')
        
        monthly_totals[month_year] += trxn_amount

sorted_totals = sorted(monthly_totals.items(), key=lambda x: datetime.strptime(x[0], '%b-%Y'))

# List of all months between the first and last available month
def generate_all_months(start_month, end_month):
    start_date = datetime.strptime(start_month, '%b-%Y')
    end_date = datetime.strptime(end_month, '%b-%Y')
    current_date = start_date
    all_months = []
    
    while current_date <= end_date:
        all_months.append(current_date.strftime('%b-%Y'))
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return all_months

first_month = sorted_totals[0][0]
last_month = sorted_totals[-1][0]
all_months = generate_all_months(first_month, last_month)

# Parameters for SIP
# income_bucket_mean = (5 + 10) / 2 * 1e5  

def parse_salary_range(salary_range):
    """
    Parses a salary range input and returns the mean salary.
    Supports input formats like:
    - 'less than 10 lakhs'
    - 'between 10 lakhs to 25 lakhs'
    - '25 lakhs to 30 lakhs'
    - 'more than 50 lakhs'
    """
    salary_range = salary_range.lower().strip()

    if "less than" in salary_range:
        max_value = float(salary_range.split("less than")[1].split()[0])
        mean_salary = max_value / 2  # Taking mean as half the max value
    elif "between" in salary_range:
        values = salary_range.replace("between", "").replace("lakhs", "").split("to")
        min_value = float(values[0].strip())
        max_value = float(values[1].strip())
        mean_salary = (min_value + max_value) / 2
    elif "more than" in salary_range:
        min_value = float(salary_range.split("more than")[1].split()[0])
        mean_salary = min_value * 1.2  # Assuming 20% increase for upper bound assumption
    else:
        # Case for exact range like '25 lakhs to 30 lakhs'
        values = salary_range.replace("lakhs", "").split("to")
        if len(values) == 2:
            min_value = float(values[0].strip())
            max_value = float(values[1].strip())
            mean_salary = (min_value + max_value) / 2
        else:
            raise ValueError("Invalid salary range format")

    return mean_salary * 1e5  # Converting lakhs to actual value in units

# Example usage:
salary_range = "between 10 lakhs to 25 lakhs"

# Call the function and assign the result to income_bucket_mean
income_bucket_mean = parse_salary_range(salary_range)

# Calculate minimum SIP amount profile as 20% of income bucket mean
min_sip_amount_profile = 0.2 * income_bucket_mean

# Output the results
print(f"Income Bucket Mean: {income_bucket_mean}")
print(f"Min SIP Amount Profile: {min_sip_amount_profile}")


min_sip_amount = 10000 
missing_sips = []

# Function to check SIP for each month based on 4 conditions
def check_sip_done(last_6_investments, last_3_investments, current_amount):
    if len(last_6_investments) >= 6:
        condition_1 = current_amount >= 0.8 * mean(last_6_investments)
    else:
        condition_1 = False
    
    if len(last_3_investments) >= 3 and mean(last_3_investments) > 0:
        condition_2 = current_amount >= mean(last_3_investments)
    else:
        condition_2 = False
    
    # Condition 3
    condition_3 = current_amount >= min_sip_amount_profile
    
    # Condition 4
    condition_4 = current_amount >= min_sip_amount
    
    return condition_1 or condition_2 or condition_3 or condition_4

last_6_investments = []
last_3_investments = []

for month in all_months:
    if month in monthly_totals:
        amount = monthly_totals[month]
        # Check if SIP is done for the current month
        sip_done = check_sip_done(last_6_investments, last_3_investments, amount)
        
        if sip_done:
            print(f"SIP done for {month}")
        else:
            print(f"SIP missing for {month}")
            missing_sips.append(month)
        
        last_6_investments.append(amount)
        last_3_investments.append(amount)
        
        if len(last_6_investments) > 6:
            last_6_investments.pop(0)  
        
        if len(last_3_investments) > 3:
            last_3_investments.pop(0)  
    else:
        print(f"SIP missing for {month} (no transaction found)")
        missing_sips.append(month)


