
from flask import Flask, render_template
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

# Function to fetch data from a given URL
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
    map_html = """
    <div id="map" style="height: 600px;"></div>
    <script>
        var map = L.map('map').setView([42.373611, -71.109733], 13);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'Map data &copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
            maxZoom: 18,
        }).addTo(map);

        // Display routes
        var shapesData = """ + json.dumps(shapes_data) + """;
        Object.values(shapesData).forEach(function(shape_points) {
            var line_coordinates = shape_points.map(function(point) {
                return [point['shape_pt_lat'], point['shape_pt_lon']];
            });
            L.polyline(line_coordinates, {color: 'green', weight: 2.5, opacity: 1}).addTo(map);
        });

        // Display stops
        var stopsData = """ + json.dumps(stops_data) + """;
        stopsData.forEach(function(stop) {
            L.marker([stop['stop_lat'], stop['stop_lon']]).addTo(map)
                .bindPopup(stop['stop_name']);
        });

        // Fetch and display vehicle positions
        fetch("https://passio3.com/harvard/passioTransit/gtfs/realtime/vehiclePositions.json")
            .then(response => response.json())
            .then(function(vehicle_positions) {
                if (vehicle_positions && vehicle_positions.entity) {
                    vehicle_positions.entity.forEach(function(entity) {
                        var vehicle = entity.vehicle || {};
                        var position = vehicle.position || {};
                        var lat = position.latitude;
                        var lon = position.longitude;
                        var vehicle_id = vehicle.id;
                        if (lat && lon) {
                            L.marker([lat, lon], {icon: L.icon({iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png'})})
                                .addTo(map)
                                .bindPopup('Vehicle ID: ' + vehicle_id);
                        }
                    });
                }
            });
    </script>
    """

    # Get list of stop names for dropdowns
    stop_names = [stop['stop_name'] for stop in stops_data]

    return render_template('index.html', map=map_html, stop_names=stop_names)

if __name__ == '__main__':
    app.run(debug=True)