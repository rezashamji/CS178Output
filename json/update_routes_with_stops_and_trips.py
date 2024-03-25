import json

with open('routes.json', 'r', encoding='utf-8') as file:
    routes_data = json.load(file)

with open('stops.json', 'r', encoding='utf-8') as file:
    stops_data = json.load(file)

with open('trips.json', 'r', encoding='utf-8') as file:
    trips_data = json.load(file)

trip_id_to_route_id = {trip['trip_id']: trip['route_id'] for trip in trips_data}

for route in routes_data.values():
    route_trip_ids = [trip_id for trip_id, r_id in trip_id_to_route_id.items() if r_id == route['route_id']]
    route_stops_ids = set()
    for trip_id in route_trip_ids:
        for stop in stops_data:
            if trip_id in stop.get('trip_ids', []): 
                route_stops_ids.add(stop['stop_id'])
    route['trip_ids'] = route_trip_ids
    route['stops'] = list(route_stops_ids)

updated_routes_json_path = 'updated_routes_with_stops_and_trips.json'

with open(updated_routes_json_path, 'w', encoding='utf-8') as file:
    json.dump(routes_data, file, indent=4)

print(f"Routes data successfully updated with stops and trips and saved to {updated_routes_json_path}.")
