import csv
import json

#adjusting the path for the input txt file
csv_file_path = 'routes.txt'
json_file_path = 'routes.json'

routes_data = {}

with open(csv_file_path, mode='r', encoding='utf-8') as csvfile: #Chat GPT helped with logic behind this open function and how to convert text to json as it does in the for loop below
    reader = csv.DictReader(csvfile)
    for row in reader:
        key = row['route_short_name'] if row['route_short_name'] else row['route_long_name']
        routes_data[key] = {
            "route_id": row['route_id'],
            "agency_id": row['agency_id'],
            "route_long_name": row['route_long_name'],
            "route_type": row['route_type'],
            "route_color": row['route_color'],
            "route_text_color": row['route_text_color'],
            "stops": [],
            "trip_ids": []
        }

with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
    json.dump(routes_data, jsonfile, indent=4)

print(f"Data has been successfully converted to {json_file_path}.")
