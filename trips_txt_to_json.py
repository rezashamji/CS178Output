import csv
import json

# File paths for the input TXT file and the output JSON file
txt_file_path = 'trips.txt'
json_file_path = 'trips.json'

# Placeholder for the trips data
trips_data = []

with open(txt_file_path, mode='r', encoding='utf-8') as txtfile:
    # Assuming the trips.txt file has headers as the first row
    reader = csv.DictReader(txtfile)
    for row in reader:
        trip_details = {
            "route_id": row['route_id'],
            "service_id": row['service_id'],
            "trip_id": row['trip_id'],
            "trip_headsign": row.get('trip_headsign', ''),  # Using .get() for optional fields
            "trip_short_name": row.get('trip_short_name', ''),
            "direction_id": row.get('direction_id', ''),
            "block_id": row.get('block_id', ''),
            "shape_id": row['shape_id'],
            "wheelchair_accessible": int(row['wheelchair_accessible']),
            "bikes_allowed": int(row['bikes_allowed'])
        }
        trips_data.append(trip_details)

# Convert to JSON and write to the output file
with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
    json.dump(trips_data, jsonfile, indent=4)

print(f"Data has been successfully converted to {json_file_path}.")
