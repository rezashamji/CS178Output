from flask import Flask, render_template, jsonify, request
import folium
import json
import requests
from datetime import datetime, timedelta

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

def fetch_trip_updates():
    # URL for the GTFS Realtime trip updates feed
    trip_updates_url = "https://passio3.com/harvard/passioTransit/gtfs/realtime/tripUpdates.json"
    try:
        # Make a GET request to fetch the trip updates
        response = requests.get(trip_updates_url)
        response.raise_for_status()  # Raises an exception for 4XX or 5XX status codes
        # Parse the JSON response
        trip_updates = response.json()
        return trip_updates
    except requests.RequestException as e:
        # Handle any errors that occur during the request
        print(f"Error fetching trip updates: {e}")
        return None
    
def extract_trip_ids_from_updates(trip_updates):
    trip_ids = []
    if trip_updates and 'entity' in trip_updates:
        for entity in trip_updates['entity']:
            if 'trip_update' in entity and 'trip' in entity['trip_update']:
                trip_id = entity['trip_update']['trip'].get('trip_id')
                if trip_id:
                    trip_ids.append(trip_id)
    return trip_ids


def match_trips_to_routes(valid_trip_ids, routes_data):
    matching_routes = []
    for route_id, route_info in routes_data.items():
        for trip_id in route_info.get('trip_ids', []):
            if trip_id in valid_trip_ids:
                matching_routes.append(route_id)
                break  # Stop searching this route if a match is found
    return matching_routes

from datetime import datetime, timezone

def calculate_eta_for_stop(trip_updates, stop_id):
    etas = {}
    for entity in trip_updates['entity']:
        trip_update = entity.get('trip_update', {})
        trip_id = trip_update.get('trip', {}).get('trip_id')
        for stop_time_update in trip_update.get('stop_time_update', []):
            if stop_time_update.get('stop_id') == stop_id:
                arrival = stop_time_update.get('arrival', {})
                arrival_time = arrival.get('time')
                if arrival_time:
                    # Convert arrival time from UNIX timestamp to a datetime object
                    arrival_datetime = datetime.fromtimestamp(arrival_time, tz=timezone.utc)
                    # Calculate ETA as the difference between arrival time and now
                    eta = (arrival_datetime - datetime.now(timezone.utc)).total_seconds()
                    etas[trip_id] = eta  # Store ETA in seconds
    return etas



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
    return render_template('index12.html', map=map_html, stop_names=stop_names, shapes_data=shapes_data, stops_data=stops_data)


def get_route_name_for_trip(trip_id):
    # Loop through routes data to find the route containing the trip_id
    for route_id, route_info in final_updated_routes_with_stops_data.items():
        if trip_id in route_info.get('trip_ids', []):
            return route_info.get('route_long_name', 'Unknown Route') #Return the route name if found
    return 'Unknown Route'

# Route to serve live bus data
@app.route('/get_bus_data')
def get_bus_data():
    # Fetch live bus data from the server
    vehicle_positions = fetch_data("https://passio3.com/harvard/passioTransit/gtfs/realtime/vehiclePositions.json")
    bus_data = []
    if vehicle_positions and 'entity' in vehicle_positions:
        for entity in vehicle_positions['entity']:
            vehicle = entity.get('vehicle', {})
            position = vehicle.get('position', {})
            lat = position.get('latitude')
            lon = position.get('longitude')
            vehicle_id = vehicle.get('vehicle', {}).get('id')
            trip_id = vehicle.get('trip', {}).get('trip_id')
            route_name = get_route_name_for_trip(trip_id) #Get the route name for the trip_id
            if lat and lon:
                bus_data.append({
                    'latitude': lat,
                    'longitude': lon,
                    'route_name': route_name })
        return jsonify(bus_data)  # Serialize data to JSON and return

@app.route('/get_schedule', methods=['POST'])
def get_schedule():
    data = request.json
    print("Received schedule request data:", data)  # Log the incoming data

    start_stop_name = data['start_stop']
    destination_stop_name = data['destination_stop']

    # Fetching stop IDs based on names
    start_stop_id = next((stop['stop_id'] for stop in stops_data if stop['stop_name'] == start_stop_name), None)
    destination_stop_id = next((stop['stop_id'] for stop in stops_data if stop['stop_name'] == destination_stop_name), None)

    print(f"Start stop ID: {start_stop_id}, Destination stop ID: {destination_stop_id}")

    valid_routes = []

    # Find routes that pass through both the starting stop and the destination stop
    for route_id, route_details in final_updated_routes_with_stops_data.items():
        if start_stop_name in route_details['stops'] and destination_stop_name in route_details['stops']:
            valid_routes.append(route_id)

    print(f"Valid routes: {valid_routes}")

    # Find departure times for each valid route from the starting stop
    schedules = []
    for route_id in valid_routes:
        # Find corresponding trip IDs for the route
        trip_ids = final_updated_routes_with_stops_data[route_id]['trip_ids']

        # Extract departure times for each trip from the starting stop
        departure_times = []
        for trip_id in trip_ids:
            if trip_id in stop_times_data:
                for stop_time in stop_times_data[trip_id]:
                    if stop_time['stop_id'] == start_stop_id:
                        # Check if departure time is in 12-hour format or 24-hour format
                        try:
                            departure_time = datetime.strptime(stop_time['departure_time'], '%I:%M:%S %p').strftime('%H:%M:%S')
                        except ValueError:
                            departure_time = stop_time['departure_time']
                        departure_times.append(departure_time)

        # Add the route and its departure times to the schedules list
        schedules.append({
            'route_name': final_updated_routes_with_stops_data[route_id]['route_long_name'],
            'departure_times': sorted(departure_times)  # Sort the departure times
        })

    print(f"Schedules: {schedules}")

    return jsonify(schedules)


# Helper function to parse time string and calculate the difference
def time_diff(scheduled_str, current_dt):
    scheduled_time = datetime.strptime(scheduled_str.split()[0], '%H:%M:%S').replace(
        year=current_dt.year, month=current_dt.month, day=current_dt.day)
    if scheduled_time < current_dt:
        scheduled_time += timedelta(days=1)
    return (scheduled_time - current_dt).seconds // 60

def extract_trip_ids_from_updates(trip_updates):
    trip_ids = []
    if 'entity' in trip_updates:
        for entity in trip_updates['entity']:
            if 'vehicle' in entity and 'trip' in entity['vehicle']:
                trip_id = entity['vehicle']['trip'].get('trip_id')
                if trip_id:
                    trip_ids.append(trip_id)
    return trip_ids


@app.route('/search_routes', methods=['POST'])
def search_routes():
    data = request.json
    current_time = datetime.utcnow()  # Assuming your times are in UTC
    start_stop_name = data['start_stop']
    destination_stop_name = data['destination_stop']

    # Find stop IDs for the given names
    start_stop_id = next((stop['stop_id'] for stop in stops_data if stop['stop_name'] == start_stop_name), None)
    destination_stop_id = next((stop['stop_id'] for stop in stops_data if stop['stop_name'] == destination_stop_name), None)

    valid_real_time_trip_ids = extract_trip_ids_from_updates(fetch_trip_updates())

    # Initialize response list
    response = []

    for route_id, route_details in final_updated_routes_with_stops_data.items():
        if start_stop_name in route_details['stops'] and destination_stop_name in route_details['stops']:
            for trip_id in route_details['trip_ids']:
                if trip_id in valid_real_time_trip_ids:
                    # Get the ETA for this trip
                    eta_seconds = calculate_eta_for_stop(fetch_trip_updates(), start_stop_id).get(trip_id)
                    readable_eta = f"{eta_seconds // 60} min {eta_seconds % 60} sec" if eta_seconds else "Not Available"

                    # Now find the scheduled stop time closest to the current time for this trip
                    scheduled_stop_times = [st['arrival_time'] for st in stop_times_data.get(trip_id, []) if st['stop_id'] == start_stop_id]
                    if scheduled_stop_times:
                        closest_scheduled_time = min(scheduled_stop_times, key=lambda t: abs(current_time - datetime.strptime(t, "%H:%M:%S")))
                        time_to_next_scheduled = time_diff(closest_scheduled_time, current_time)
                    else:
                        time_to_next_scheduled = "Not Available"

                    response.append({
                        "route_name": route_details['route_long_name'],
                        "eta": readable_eta,
                        "scheduled_time": time_to_next_scheduled
                    })

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
