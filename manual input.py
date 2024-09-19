from datetime import datetime
from collections import defaultdict
from statistics import mean
import json

with open('sorted_transactions.json') as f:
    data = json.load(f)

transactions = data['data'][0]['dtTransaction']
scheme_details = data['data'][0]['dtSummary']

# Function to parse salary range and calculate mean salary
def parse_salary_range(salary_range):
    salary_range = salary_range.lower().strip()
    if "less than" in salary_range:
        max_value = float(salary_range.split("less than")[1].split()[0])
        mean_salary = max_value / 2  
    elif "between" in salary_range:
        values = salary_range.replace("between", "").replace("lakhs", "").split("to")
        min_value = float(values[0].strip())
        max_value = float(values[1].strip())
        mean_salary = (min_value + max_value) / 2
    elif "more than" in salary_range:
        min_value = float(salary_range.split("more than")[1].split()[0])
        mean_salary = min_value * 1.2  # Assuming 20% increase for upper bound assumption
    return mean_salary * 1e5

# Function to generate all months between two dates
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

# Function to check SIP based on the provided conditions
def check_sip_done(last_6_investments, last_3_investments, current_amount, min_sip_amount_profile, min_sip_amount=10000):
    condition_1_value = mean(last_6_investments) * 0.8 if len(last_6_investments) >= 6 else None
    condition_1 = current_amount >= condition_1_value if condition_1_value else False
    condition_2_value = mean(last_3_investments) if len(last_3_investments) >= 3 else None
    condition_2 = current_amount >= condition_2_value if condition_2_value else False
    condition_3 = current_amount >= min_sip_amount_profile
    condition_4 = current_amount >= min_sip_amount
    return condition_1 or condition_2 or condition_3 or condition_4

# Main function to calculate SIP data
def calculate_sip_data(salary_range):
    monthly_totals = defaultdict(float)
    scheme_asset_type = {scheme['scheme']: scheme['assetType'] for scheme in scheme_details}

    # Calculate the minimum SIP amount profile based on the provided salary range
    income_bucket_mean = parse_salary_range(salary_range)
    min_sip_amount_profile = 0.2 * income_bucket_mean

    # Calculate total SIP per month
    for transaction in transactions:
        trxn_amount = float(transaction['trxnAmount'])
        trxn_date = datetime.strptime(transaction['trxnDate'], '%d-%b-%Y')
        month_year = trxn_date.strftime('%b-%Y')
        monthly_totals[month_year] += trxn_amount

    # Sort the transactions by month and year
    sorted_totals = sorted(monthly_totals.items(), key=lambda x: datetime.strptime(x[0], '%b-%Y'))
    
    # Get the first transaction month
    first_month = sorted_totals[0][0]
    
    # Get the current month
    today = datetime.today()
    current_month = today.strftime('%b-%Y')

    # Generate all months from first transaction to current month
    all_months = generate_all_months(first_month, current_month)

    # SIP calculation logic for each month
    last_6_investments = []
    last_3_investments = []
    sip_data = []

    # Count variables for SIP done/not done
    sip_done_count = 0
    sip_not_done_count = 0

    for month in all_months:
        if month in monthly_totals:
            amount = monthly_totals[month]
            sip_done = check_sip_done(last_6_investments, last_3_investments, amount, min_sip_amount_profile)
        else:
            amount = 0
            sip_done = False
        
        if sip_done:
            sip_done_count += 1
        else:
            sip_not_done_count += 1

        sip_data.append({
            "month": month,
            "amount": amount,
            "sip_done": sip_done
        })

        # Update investment history
        if amount > 0:
            last_6_investments.append(amount)
            last_3_investments.append(amount)
            if len(last_6_investments) > 6:
                last_6_investments.pop(0)
            if len(last_3_investments) > 3:
                last_3_investments.pop(0)

    # Calculate active months (from first transaction date to the current date, inclusive)
    active_months = len(all_months)  # Now includes the current month

    return {
        "active_months": active_months,
        "sip_done_count": sip_done_count,
        "sip_not_done_count": sip_not_done_count,
        "sip_data": sip_data
    }

if __name__ == '__main__':
    salary_range = input("Please enter your salary range (e.g., 'between 10 lakhs to 25 lakhs'): ")
    result = calculate_sip_data(salary_range)

    print(f"\nTotal active months: {result['active_months']}")
    print(f"Total months SIP done: {result['sip_done_count']}")
    print(f"Total months SIP not done: {result['sip_not_done_count']}")
    print("\nMonth-wise SIP data:")
    for sip in result['sip_data']:
        status = "SIP Done" if sip['sip_done'] else "SIP Not Done"
        print(f"  {sip['month']} - Amount: {sip['amount']} - {status}")
