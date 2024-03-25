import json

def main():
    # Load the necessary files
    with open('updated_routes_with_stops_and_trips.json', 'r') as file:
        routes_data = json.load(file)

    with open('stops.json', 'r') as file:
        stops_data = json.load(file)

    with open('trips.json', 'r') as file:
        trips_data = json.load(file)

    with open('stop_times.json', 'r') as file:
        stop_times_data = json.load(file)

    #map trip ids to route ids from trips data
    trip_to_route = {trip["trip_id"]: trip["route_id"] for trip in trips_data}

    #map stop ids to names from stops data
    stop_id_to_name = {stop["stop_id"]: stop["stop_name"] for stop in stops_data}

    #route id to stop id mapping
    route_to_stops = {route["route_id"]: set() for route in trips_data}

    #update route_to_stops using stop_times_data
    for trip_id, stops in stop_times_data.items():
        route_id = trip_to_route.get(trip_id)
        if route_id in route_to_stops:
            for stop_time in stops:
                route_to_stops[route_id].add(stop_time["stop_id"])

    #routes_data with stop names
    for route in routes_data.values():
        route_id = route["route_id"]
        if route_id in route_to_stops:
            route["stops"] = [stop_id_to_name[stop_id] for stop_id in route_to_stops[route_id] if stop_id in stop_id_to_name]

    #new file
    output_file_path = 'final_updated_routes_with_stops.json'
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(routes_data, file, indent=4)

    print(f"Updated routes data with stops saved to {output_file_path}.")

if __name__ == "__main__":
    main()
