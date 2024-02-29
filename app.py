# - The TripUpdates feed and the VehiclePositions feed both reference a trip_id, which references a route_id in trips.txt, which references a route_id in routes.txt.
# - The VehiclePositions feed shows exactly where the vehicle is and what trip it is on.
# - The TripUpdates feed shows the ETA for each stop in each active trip (and in some cases, the next trip).
# - Each entity in the TripUpdates feed represents a vehicle in the VehiclePositions feed and this relationship is established with the trip_id. TripUpdateFeed.entity.trip_update.trip_id == VehiclePositionFeed.entity.vehicle.trip.trip_id

from flask import Flask, render_template
import folium
import requests

app = Flask(__name__)

# Function to fetch data from the provided URLs
def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()  # Parse response as JSON
    except Exception as e:
        print("Error fetching data:", e)
        return None

# Route for rendering the map
@app.route('/')
def index():
    # Initialize map
    m = folium.Map(location=[42.373611, -71.109733], zoom_start=12)
    # NITHYA -- set this to Harvard's location?

   # Fetch and display vehicle positions
    vehicle_positions_url = "https://passio3.com/harvard/passioTransit/gtfs/realtime/vehiclePositions.json"
    vehicle_positions = fetch_data(vehicle_positions_url)
    print(vehicle_positions)  # Debug print to check the content of vehicle_positions
    if isinstance(vehicle_positions, list):  
        for vehicle in vehicle_positions:
            print(vehicle)  # Debug print to check the content of each vehicle
            if isinstance(vehicle, dict): 
                lat = vehicle.get('latitude') 
                lon = vehicle.get('longitude')
                if lat is not None and lon is not None:
                    folium.Marker([lat, lon], popup=f"Vehicle ID: {vehicle.get('vehicle_id')}").add_to(m)



    return render_template('index.html', map = m)

if __name__ == '__main__':
    app.run(debug=True)

