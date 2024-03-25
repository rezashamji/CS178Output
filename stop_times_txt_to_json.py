import csv
import json

txt_file_path = 'stop_times.txt'
json_file_path = 'stop_times.json'

stop_times_data = {}

with open(txt_file_path, mode='r', encoding='utf-8') as txtfile:
    reader = csv.DictReader(txtfile)
    for row in reader:
        trip_id = row['trip_id']
        if trip_id not in stop_times_data:
            stop_times_data[trip_id] = []
        stop_time_details = {
            "arrival_time": row['arrival_time'],
            "departure_time": row['departure_time'],
            "stop_id": row['stop_id'],
            "stop_sequence": int(row['stop_sequence']),
            "stop_headsign": row['stop_headsign'],
            "pickup_type": row['pickup_type'],
            "drop_off_type": row['drop_off_type'],
            "timepoint": row['timepoint']
        }
        stop_times_data[trip_id].append(stop_time_details)

for trip_id, times in stop_times_data.items():
    stop_times_data[trip_id] = sorted(times, key=lambda k: k['stop_sequence'])

with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
    json.dump(stop_times_data, jsonfile, indent=4)

print(f"Data has been successfully converted to {json_file_path}.")
