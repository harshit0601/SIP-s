import json
import csv

file_path = 'transaction_detail.json'
with open(file_path, 'r') as f:
    data = json.load(f)

csv_output_path = 'transaction_details.csv'

summary_headers = set()
transaction_headers = set()

for item in data['data']:
    # Update the headers for dtSummary and dtTransaction
    if 'dtSummary' in item:
        for summary in item['dtSummary']:
            summary_headers.update(summary.keys())

    if 'dtTransaction' in item:
        for transaction in item['dtTransaction']:
            transaction_headers.update(transaction.keys())

# Combine headers from both dtSummary and dtTransaction
all_headers = list(summary_headers.union(transaction_headers))

with open(csv_output_path, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=all_headers)
    writer.writeheader()

    for item in data['data']:
        dt_summary_list = item.get('dtSummary', [])
        dt_transaction_list = item.get('dtTransaction', [])

        # Create a mapping of dtSummary based on scheme to ensure correct pairing
        summary_mapping = {summary['scheme']: summary for summary in dt_summary_list}

        # Write rows to CSV by matching transactions to the correct summary
        for transaction in dt_transaction_list:
            row = {}

            # Find the matching summary using the scheme 
            summary = summary_mapping.get(transaction['scheme'], {})

            row.update(summary)
            row.update(transaction)

            writer.writerow(row)

print(f"Data successfully written to {csv_output_path}")
