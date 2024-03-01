from flask import Flask, render_template
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

# - The TripUpdates feed and the VehiclePositions feed both reference a trip_id, which references a route_id in trips.txt, which references a route_id in routes.txt.
# - The VehiclePositions feed shows exactly where the vehicle is and what trip it is on.
# - The TripUpdates feed shows the ETA for each stop in each active trip (and in some cases, the next trip).
# - Each entity in the TripUpdates feed represents a vehicle in the VehiclePositions feed and this relationship is established with the trip_id. TripUpdateFeed.entity.trip_update.trip_id == VehiclePositionFeed.entity.vehicle.trip.trip_id


def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()  # Parse response as JSON
        if isinstance(data, str):
            # If data is a string, parse it into a dictionary
            data = json.loads(data)
        return data
    except Exception as e:
        print("Error fetching data:", e)
        return None

    

@app.route('/')
def index():
    # Initialize map centered at Harvard's location
    m = folium.Map(location=[42.373611, -71.109733], zoom_start=12)

    # Display vehicle positions
    vehicle_positions_url = "https://passio3.com/harvard/passioTransit/gtfs/realtime/vehiclePositions.json"
    vehicle_positions = fetch_data(vehicle_positions_url)
    vehicle_positions = fetch_data(vehicle_positions_url)
    if vehicle_positions:
        # Assuming vehicle_positions is supposed to be a list of dictionaries
        for vehicle in vehicle_positions:
            # Make sure that 'vehicle' is a dictionary before trying to use `.get()`
            if isinstance(vehicle, dict):
                lat = vehicle.get('latitude') 
                lon = vehicle.get('longitude')
    # Display stops
    for stop in stops_data:
        folium.Marker(
            location=[stop['stop_lat'], stop['stop_lon']],
            popup=f"{stop['stop_name']}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    # Display routes
    for shape_id, shape_points in shapes_data.items():
        line_coordinates = [(point['shape_pt_lat'], point['shape_pt_lon']) for point in shape_points]
        folium.PolyLine(line_coordinates, color='green', weight=2.5, opacity=1).add_to(m)

    # Return the HTML template and embed the map
    return render_template('index.html', map=m._repr_html_())

if __name__ == '__main__':
    app.run(debug=True)
