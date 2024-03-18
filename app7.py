
from flask import Flask, render_template, jsonify, request
import folium
import json
import requests

app = Flask(__name__)

# Load JSON Data
with open('routes.json', 'r') as f:
    routes_data = json.load(f)


with open('final_updated_routes_with_stops.json', 'r') as f:
    final_updated_routes_with_stops_data = json.load(f)

with open('stops.json', 'r') as f:
    stops_data = json.load(f)

with open('shapes.json', 'r') as f:
    shapes_data = json.load(f)

with open('stop_times.json', 'r') as f:
    stop_times_data = json.load(f)

# Function to fetch data from a given URL
def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        # Raise exception for HTTP errors
        data = response.json()
        return data
    except Exception as e:
        print("Error fetching data:", e)
        return None

@app.route('/')
def index():
    # Initialize map centered at Harvard's location
    m = folium.Map(location=[42.373611, -71.109733], zoom_start=12, tiles='CartoDB.Positron')
    
    # Display routes
    for shape_id, shape_points in shapes_data.items():
        line_coordinates = [(point['shape_pt_lat'], point['shape_pt_lon']) for point in shape_points]
        folium.PolyLine(line_coordinates, color='green').add_to(m)

    # Display stops
    for stop in stops_data:
        folium.Marker(
            location=[stop['stop_lat'], stop['stop_lon']],
            popup=f"{stop['stop_name']}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    # Fetch live bus data and display buses
    vehicle_positions = fetch_data("https://passio3.com/harvard/passioTransit/gtfs/realtime/vehiclePositions.json")

    if vehicle_positions and 'entity' in vehicle_positions:
        for entity in vehicle_positions['entity']:
            vehicle = entity.get('vehicle', {})
            position = vehicle.get('position', {})
            lat = position.get('latitude')
            lon = position.get('longitude')
            vehicle_id = vehicle.get('vehicle', {}).get('id')
            route_id = vehicle.get('trip', {}).get('route_id')
            if lat and lon:
                folium.Marker(
                    [lat, lon],
                    popup=f"Vehicle ID: {vehicle_id}, Route ID: {route_id}",
                    icon=folium.Icon(color='red', icon='bus')
                ).add_to(m)

    # Render the map
    map_html = m._repr_html_()

    # Get list of stop names for dropdowns
    stop_names = [stop['stop_name'] for stop in stops_data]

    # Pass shapes_data to the template
    return render_template('index7.html', map=map_html, stop_names=stop_names, shapes_data=shapes_data)


# Route to serve live bus data
@app.route('/get_bus_data')
def get_bus_data():
    # Fetch live bus data from the server
    vehicle_positions = fetch_data("https://passio3.com/harvard/passioTransit/gtfs/realtime/vehiclePositions.json")
    if vehicle_positions and 'entity' in vehicle_positions:
        # Extract necessary data (latitude and longitude) from vehicle positions
        bus_data = [{'latitude': entity['vehicle']['position']['latitude'],
                     'longitude': entity['vehicle']['position']['longitude']}
                    for entity in vehicle_positions['entity']]
        return jsonify(bus_data)  # Serialize data to JSON and return
    else:
        return jsonify([])  # Return empty list if no bus data is available
#@app.route('/search_routes', methods=['POST'])
#def search_routes():
    data = request.json
    print("Received search data:", data)  # Log the incoming search data

    start_stop_name = data['start_stop']
    destination_stop_name = data['destination_stop']

    print(f"Searching routes from '{start_stop_name}' to '{destination_stop_name}'")

    # Assuming stops_data is loaded from 'stops.json' and contains details for each stop
    start_stop_id = next((stop['stop_id'] for stop in stops_data if stop['stop_name'] == start_stop_name), None)
    destination_stop_id = next((stop['stop_id'] for stop in stops_data if stop['stop_name'] == destination_stop_name), None)

    print(f"Start stop ID: {start_stop_id}")
    print(f"Destination stop ID: {destination_stop_id}")

    # Validate trip sequences using the 'stop_times.json'
    valid_trip_ids = []

    # After loading final_updated_routes_with_stops_data
    print(f"Loaded {len(final_updated_routes_with_stops_data)} routes with stops and trip IDs")


    for trip_id, stops in stop_times_data.items():
        print(f"Checking trip {trip_id}: stop IDs sequence is { [stop['stop_id'] for stop in stops] }")
        stop_ids = [stop['stop_id'] for stop in stops]
        if start_stop_id in stop_ids and destination_stop_id in stop_ids:
            start_index = stop_ids.index(start_stop_id)
            destination_index = stop_ids.index(destination_stop_id)
            if destination_index > start_index:
                valid_trip_ids.append(trip_id)

    print(f"Valid trip IDs: {valid_trip_ids}")

    # Map the valid trip_ids to their corresponding route_ids from the updated routes data
    valid_routes = list(set(route_details['route_long_name']
                            for route_id, route_details in final_updated_routes_with_stops_data.items()
                            if any(trip_id in valid_trip_ids for trip_id in route_details['trip_ids'])))

    print(f"Valid routes: {valid_routes}")

    return jsonify(valid_routes)
@app.route('/search_routes', methods=['POST'])
def search_routes():
    data = request.json
    print("Received search data:", data)  # Log the incoming search data

    start_stop_name = data['start_stop']
    destination_stop_name = data['destination_stop']

    # Fetching stop IDs based on names
    start_stop_id = next((stop['stop_id'] for stop in stops_data if stop['stop_name'] == start_stop_name), None)
    destination_stop_id = next((stop['stop_id'] for stop in stops_data if stop['stop_name'] == destination_stop_name), None)

    print(f"Start stop ID: {start_stop_id}, Destination stop ID: {destination_stop_id}")

    valid_trip_ids = []

    # Loop through all trips in stop_times_data
    for trip_id, stops in stop_times_data.items():
        stop_ids = [stop['stop_id'] for stop in stops]
        # Check if both start and destination stops are part of the trip
        if start_stop_id in stop_ids and destination_stop_id in stop_ids:
            valid_trip_ids.append(trip_id)

    print(f"Valid trip IDs: {valid_trip_ids}")

    # Find corresponding routes for the valid trip IDs
    valid_routes = list(set(
        route_details['route_long_name']
        for route_id, route_details in final_updated_routes_with_stops_data.items()
        if any(trip_id in valid_trip_ids for trip_id in route_details['trip_ids'])
    ))

    print(f"Valid routes: {valid_routes}")

    return jsonify(valid_routes)

if __name__ == '__main__':
    app.run(debug=True)

