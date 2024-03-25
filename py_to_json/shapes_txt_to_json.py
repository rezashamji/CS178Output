import csv
import json

txt_file_path = 'shapes.txt'
json_file_path = 'shapes.json'

shapes_data = {}

with open(txt_file_path, mode='r', encoding='utf-8') as txtfile: #Chat GPT helped with logic behind this open function and how to convert text to json as it does in the for loop below
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

for shape_id, points in shapes_data.items():
    shapes_data[shape_id] = sorted(points, key=lambda k: k['shape_pt_sequence'])

with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
    json.dump(shapes_data, jsonfile, indent=4)

print(f"Data has been successfully converted to {json_file_path}.")
