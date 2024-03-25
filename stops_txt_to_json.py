import csv
import json

txt_file_path = 'stops.txt' 
json_file_path = 'stops.json' 

stops_data = []

with open(txt_file_path, mode='r', encoding='utf-8') as txtfile:
    reader = csv.DictReader(txtfile)
    for row in reader:
        stop_details = {
            "stop_id": row['stop_id'],
            "stop_code": row['stop_code'],
            "stop_name": row['stop_name'],
            "stop_desc": row['stop_desc'],
            "stop_lat": float(row['stop_lat']),
            "stop_lon": float(row['stop_lon']),
            "stop_url": row['stop_url'],
            "location_type": int(row['location_type']),
            "stop_timezone": row['stop_timezone'],
            "wheelchair_boarding": int(row['wheelchair_boarding']),
            "platform_code": row['platform_code']
        }
        stops_data.append(stop_details)

with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
    json.dump(stops_data, jsonfile, indent=4)

print(f"Data has been successfully converted to {json_file_path}.")
