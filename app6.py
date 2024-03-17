from flask import Flask, request, render_template, jsonify  # Import jsonify to serialize data to JSON
import folium
import json
import requests

app = Flask(__name__)

# Load JSON Data
with open('routes.json', 'r') as f:
    routes_data = json.load(f)

with open('stops.json', 'r') as f:
    stops_data = json.load(f)

with open('shapes.json', 'r') as f:
    shapes_data = json.load(f)


# Preprocess stops data for quick lookup by name
stops_lookup = {stop['stop_name']: stop for stop in stops_data}

# Load and preprocess stop_times.json data
with open('stop_times.json', 'r') as f:
    stop_times_data = json.load(f)


# Load and preprocess stop_times.json data
with open('trips.json', 'r') as f:
    trips_data = json.load(f)

# Load and preprocess stop_times.json data
with open('routes.json', 'r') as f:
    routes_data = json.load(f)

# Organize stop_times by trip_id and sort by stop_sequence
stop_times_by_trip = {}

for trip_id, stop_times_list in stop_times_data.items():
    # Here, trip_id is the key (e.g., "670294"), and stop_times_list is the list of stops for that trip
    stop_times_by_trip[trip_id] = stop_times_list  # In this case, you already have the correct structure


for trip_id in stop_times_by_trip:
    stop_times_by_trip[trip_id].sort(key=lambda x: x['stop_sequence'])

trips_lookup = {trip['trip_id']: trip for trip in trips_data}


# Transforming routes_data to be keyed by route_id
routes_lookup = {route_details['route_id']: route_details for route_details in routes_data.values()}
def find_routes_between_stops_with_realtime(start_stop_name, end_stop_name):
    start_stop_id = stops_lookup[start_stop_name]['stop_id']
    end_stop_id = stops_lookup[end_stop_name]['stop_id']

    # Fetch real-time vehicle positions
    vehicle_positions_data = fetch_data("https://passio3.com/harvard/passioTransit/gtfs/realtime/vehiclePositions.json")

    if not vehicle_positions_data or 'entity' not in vehicle_positions_data:
        print("Could not fetch vehicle positions or no data available.")
        return []

    vehicle_positions = vehicle_positions_data['entity']
    

    # Filter vehicles that are on a trip passing through both start and end stops
    vehicles_on_route = []
    for vehicle in vehicle_positions:
        trip_id = vehicle['trip_id']

        # Assuming stop_times_by_trip contains stop sequences for each trip
        if trip_id not in stop_times_by_trip:
            continue

        stop_sequence = stop_times_by_trip[trip_id]
        start_indices = [i for i, stop in enumerate(stop_sequence) if stop['stop_id'] == start_stop_id]
        end_indices = [i for i, stop in enumerate(stop_sequence) if stop['stop_id'] == end_stop_id]

        # Check if there is a vehicle currently between the start and end stops
        current_stop_sequence = vehicle['current_stop_sequence']
        if any(start_index < current_stop_sequence < end_index for start_index in start_indices for end_index in end_indices):
            vehicles_on_route.append(vehicle)

    # Aggregate route information for each vehicle
    route_info_list = []
    for vehicle in vehicles_on_route:
        trip_id = vehicle['trip_id']
        route_id = trips_lookup[trip_id]['route_id']
        route_info = routes_lookup[route_id]
        
        # You might want to calculate the expected time of arrival (ETA) at the starting stop
        # This is a simplified example and would require more logic for accurate ETAs
        eta_at_start_stop = "Calculating..."

        route_info_list.append({
            'route_name': route_info.get('route_long_name', 'Unknown route'),
            'vehicle_id': vehicle['vehicle_id'],
            'eta_at_start_stop': eta_at_start_stop
        })

    return route_info_list


# New route to get possible routes between two stops
@app.route('/find_routes')
def get_possible_routes():
    start_stop_name = request.args.get('start')
    end_stop_name = request.args.get('end')

    if not start_stop_name or not end_stop_name:
        return jsonify({'error': 'Please specify both a starting and ending stop.'}), 400

    if start_stop_name not in stops_lookup or end_stop_name not in stops_lookup:
        return jsonify({'error': 'Invalid stop name(s).'}), 404

    routes = find_routes(start_stop_name, end_stop_name)
    return jsonify(routes)

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
    m = folium.Map(location=[42.373611, -71.109733], zoom_start=100, tiles='CartoDB.Positron')

    # Display routes
    for shape_id, shape_points in shapes_data.items():
        line_coordinates = [(point['shape_pt_lat'], point['shape_pt_lon']) for point in shape_points]
        folium.PolyLine(line_coordinates, color='green', weight=2.5, opacity=1).add_to(m)

    # Display stops
    for stop in stops_data:
        folium.Marker(
            location=[stop['stop_lat'], stop['stop_lon']],
            popup=f"{stop['stop_name']}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    # Calculate bounds based on route coordinates
    bounds = m.get_bounds()
    # Zoom map to bounds
    m.fit_bounds(bounds)

    # Get list of stop names for dropdowns
    stop_names = [stop['stop_name'] for stop in stops_data]

    # Render the map
    map_html = m._repr_html_()
    # Render the template with map and dropdowns
    return render_template('index6.html', map=map_html, stop_names=stop_names)

# Route to serve live bus data
@app.route('/get_bus_data')
def get_bus_data():
    # URL for the real-time vehicle positions JSON
    url = "https://passio3.com/harvard/passioTransit/gtfs/realtime/vehiclePositions.json"
    
    try:
        # Fetch the real-time data
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        vehicle_positions = response.json()
        
        # List to hold processed vehicle data
        processed_vehicles = []

        for entity in vehicle_positions.get('entity', []):
            vehicle = entity.get('vehicle')
            if not vehicle:
                continue  # Skip if no vehicle data is present
            
            # Extract relevant information from each vehicle
            vehicle_id = vehicle.get('vehicle', {}).get('id')
            trip_id = vehicle.get('trip', {}).get('trip_id')
            stop_id = vehicle.get('stop_id')
            latitude = vehicle.get('position', {}).get('latitude')
            longitude = vehicle.get('position', {}).get('longitude')
            current_stop_sequence = vehicle.get('current_stop_sequence')
            
            # Map the trip_id to its route_id (assuming trips_lookup exists)
            route_id = trips_lookup.get(trip_id, {}).get('route_id', 'Unknown')
            # Optional: Look up the stop name using stop_id
            stop_name = stops_lookup.get(stop_id, {}).get('stop_name', 'Unknown')
            
            processed_vehicles.append({
                'vehicle_id': vehicle_id,
                'trip_id': trip_id,
                'route_id': route_id,
                'stop_id': stop_id,
                'stop_name': stop_name,
                'latitude': latitude,
                'longitude': longitude,
                'current_stop_sequence': current_stop_sequence
            })

        return jsonify(processed_vehicles)
    except Exception as e:
        print(f"Error fetching real-time vehicle data: {e}")
        return jsonify([])  # Return an empty list in case of error

if __name__ == '__main__':
    app.run(debug=True)