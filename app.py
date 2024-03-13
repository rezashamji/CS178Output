# from flask import Flask, render_template
# import folium
# import json
# import requests

# app = Flask(__name__)

# # Load JSON Data
# with open('routes.json', 'r') as f:
#     routes_data = json.load(f)

# with open('stops.json', 'r') as f:
#     stops_data = json.load(f)

# with open('shapes.json', 'r') as f:
#     shapes_data = json.load(f)

# # Function to fetch data from a given URL
# def fetch_data(url):
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         # Raise exception for HTTP errors
#         data = response.json()
#         # Parse response as JSON
#         if isinstance(data, str):
#             # If data is a string, parse it into a dictionary
#             data = json.loads(data)
#         return data
#     except Exception as e:
#         print("Error fetching data:", e)
#         return None
    
# @app.route('/')
# def index():
#     # Initialize map centered at Harvard's location
#     m = folium.Map(location=[42.373611, -71.109733], zoom_start=100, tiles='CartoDB.Positron')
    
#     # Display routes
#     for shape_id, shape_points in shapes_data.items():
#         line_coordinates = [(point['shape_pt_lat'], point['shape_pt_lon']) for point in shape_points]
#         folium.PolyLine(line_coordinates, color='green', weight=2.5, opacity=1).add_to(m)
    
#     # Display stops
#     for stop in stops_data:
#         folium.Marker(
#             location=[stop['stop_lat'], stop['stop_lon']],
#             popup=f"{stop['stop_name']}",
#             icon=folium.Icon(color='blue', icon='info-sign')
#         ).add_to(m)
        
#     # Fetch and display vehicle positions
#     vehicle_positions = fetch_data("https://passio3.com/harvard/passioTransit/gtfs/realtime/vehiclePositions.json")
    
#     if vehicle_positions and 'entity' in vehicle_positions:
#         for entity in vehicle_positions['entity']:
#             vehicle = entity.get('vehicle', {})
#             position = vehicle.get('position', {})
#             lat = position.get('latitude')
#             lon = position.get('longitude')
#             vehicle_id = vehicle.get('vehicle', {}).get('id')
#             if lat and lon:
#                 folium.Marker(
#                     [lat, lon],
#                     popup=f"Vehicle ID: {vehicle_id}",
#                     icon=folium.Icon(color='red', icon='bus')
#                 ).add_to(m)
                
#     # Calculate bounds based on route coordinates
#     bounds = m.get_bounds()
#     # Zoom map to bounds
#     m.fit_bounds(bounds)
    
#     # Get list of stop names for dropdowns
#     stop_names = [stop['stop_name'] for stop in stops_data]
    
#     # Render the map
#     map_html = m._repr_html_()
    
#     # Render the template with map and dropdowns
#     return render_template('index.html', map=map_html, stop_names=stop_names)

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template
import folium
import json
import requests
import threading
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
        response.raise_for_status()
        # Raise exception for HTTP errors
        data = response.json()
        # Parse response as JSON
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
    m = folium.Map(location=[42.373611, -71.109733], zoom_start=15, tiles='CartoDB.Positron')

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

    # Fetch and display vehicle positions
    vehicle_positions = fetch_data("https://passio3.com/harvard/passioTransit/gtfs/realtime/vehiclePositions.json")

    if vehicle_positions and 'entity' in vehicle_positions:
        for entity in vehicle_positions['entity']:
            vehicle = entity.get('vehicle', {})
            position = vehicle.get('position', {})
            lat = position.get('latitude')
            lon = position.get('longitude')
            vehicle_id = vehicle.get('vehicle', {}).get('id')
            if lat and lon:
                folium.Marker(
                    [lat, lon],
                    popup=f"Vehicle ID: {vehicle_id}",
                    icon=folium.Icon(color='red', icon='bus')
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
    return render_template('index.html', map=map_html, stop_names=stop_names)

if __name__ == '__main__':
    app.run(debug=True)