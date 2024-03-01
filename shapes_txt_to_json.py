import csv
import json

# Adjusting the file path for the input TXT file
txt_file_path = 'shapes.txt'  # The input file in TXT format
json_file_path = 'shapes.json'  # The output file in JSON format

# Placeholder for shapes data
shapes_data = {}

with open(txt_file_path, mode='r', encoding='utf-8') as txtfile:
    reader = csv.DictReader(txtfile)
    for row in reader:
        shape_id = row['shape_id']
        if shape_id not in shapes_data:
            shapes_data[shape_id] = []
        shapes_data[shape_id].append({
            "shape_pt_lat": float(row['shape_pt_lat']),
            "shape_pt_lon": float(row['shape_pt_lon']),
            "shape_pt_sequence": int(row['shape_pt_sequence'])
        })

# Sorting the points by sequence within each shape_id
for shape_id, points in shapes_data.items():
    shapes_data[shape_id] = sorted(points, key=lambda k: k['shape_pt_sequence'])

# Convert to JSON
with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
    json.dump(shapes_data, jsonfile, indent=4)

print(f"Data has been successfully converted to {json_file_path}.")
