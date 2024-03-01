import csv
import json

# Adjusting the file path for the input TXT file
csv_file_path = 'routes.txt'  # Updated file path with .txt extension
json_file_path = 'routes.json'

# Placeholder for routes data
routes_data = {}

with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Assuming route_short_name is unique and used as key; otherwise, use route_id
        key = row['route_short_name'] if row['route_short_name'] else row['route_long_name']
        routes_data[key] = {
            "route_id": row['route_id'],
            "agency_id": row['agency_id'],
            "route_long_name": row['route_long_name'],
            "route_type": row['route_type'],
            "route_color": row['route_color'],
            "route_text_color": row['route_text_color'],
            # Placeholder for stops and trips, assuming they would be added from another source
            "stops": [],
            "trip_ids": []
        }

# Convert to JSON
with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
    json.dump(routes_data, jsonfile, indent=4)

print(f"Data has been successfully converted to {json_file_path}.")
