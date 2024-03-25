from flask import Flask, render_template, jsonify, request
import folium
import json
import requests
from datetime import datetime, timezone

app = Flask(__name__)

#the four following files were text files that were converted to JSON files for easier use, organization, and objects
with open('routes.json', 'r') as f:
    routes_data = json.load(f)

with open('stops.json', 'r') as f:
    stops_data = json.load(f)

with open('shapes.json', 'r') as f:
    shapes_data = json.load(f)

with open('stop_times.json', 'r') as f:
    stop_times_data = json.load(f)

#created a json file which is the routes.json file with enhancements
#(stop_id array and trip_id *using trips.json which is made from trips text file* array for each bus populated)
#called final_updated_routes_with_stops
with open('final_updated_routes_with_stops.json', 'r') as f:
    final_updated_routes_with_stops_data = json.load(f)

def fetch_data(url):
        response = requests.get(url)
        data = response.json()
        return data

def fetch_trip_updates():
    #URL for the GTFS realtime trip updates feed
    trip_updates_url = "https://passio3.com/harvard/passioTransit/gtfs/realtime/tripUpdates.json"
    #fetch the trip updates
    response = requests.get(trip_updates_url)
    #parse JSON response
    trip_updates = response.json()
    return trip_updates

#gets the trip ids from the trip update files    
def trip_ids_from_trip_updates(trip_updates):
    trip_ids = []
    if trip_updates and 'entity' in trip_updates:
        for entity in trip_updates['entity']:
            if 'trip' in entity['trip_update'] and 'trip_update' in entity:
                trip_id = entity['trip_update']['trip'].get('trip_id')
                if trip_id:
                    trip_ids.append(trip_id)
    return trip_ids

#Chat GPT helped with the logic of how to iterativly check each stop_id in order to calculate the ETA
#gets the live eta for estimated time of arrival to the start stop
def calculate_stop_eta(trip_updates, stop_id):
    etas = {}
    for entity in trip_updates['entity']:
        trip_update = entity.get('trip_update', {})
        trip_id = trip_update.get('trip', {}).get('trip_id')
        for stop_update in trip_update.get('stop_time_update', []):
            if stop_update.get('stop_id') == stop_id:
                arrival = stop_update.get('arrival', {})
                arrival_time = arrival.get('time')
                if arrival_time:
                    #convert arrival time from UNIX to datetime object
                    arrival_datetime = datetime.fromtimestamp(arrival_time, tz=timezone.utc)
                    #ETA = difference between arrival time and now
                    eta = (arrival_datetime - datetime.now(timezone.utc)).total_seconds()
                    etas[trip_id] = eta #eta is stored in seconds
    return etas


@app.route('/')
def index():
    #map centered at Harvard's location
    m = folium.Map(location=[42.373611, -71.109733], zoom_start=12, tiles='CartoDB.Positron')

    #display routes using shapes.json (shapes text file converted to json)
    for shape_id, shape_details in shapes_data.items():
        coordinates = [(point['shape_pt_lat'], point['shape_pt_lon']) for point in shape_details]
        folium.PolyLine(coordinates, color='green').add_to(m)

    #display stops using stops.json (stops text file converted to json)
    for stop in stops_data:
        folium.Marker(
            location=[stop['stop_lat'], stop['stop_lon']],
            popup=f"{stop['stop_name']}",
            icon=folium.Icon(color='blue', icon='info-sign') #stops are colored blue
        ).add_to(m)

    #live data of vehicle positions
    vehicle_positions = fetch_data("https://passio3.com/harvard/passioTransit/gtfs/realtime/vehiclePositions.json")

    #displays vehicle positions on the map
    if vehicle_positions and 'entity' in vehicle_positions:
        for entity in vehicle_positions['entity']:
            vehicle = entity.get('vehicle', {})
            position = vehicle.get('position', {})
            lat = position.get('latitude')
            lon = position.get('longitude')
            route_id = vehicle.get('trip', {}).get('route_id')
            vehicle_id = vehicle.get('vehicle', {}).get('id')
            if lat and lon:
                folium.Marker(
                    [lat, lon],
                    popup=f"Vehicle ID: {vehicle_id}, Route ID: {route_id}",
                    icon=folium.Icon(color='red', icon='bus') #busses are displayed as red on the map
                ).add_to(m)

    map_html = m._repr_html_()

    #stop names for dropdown
    stop_names = [stop['stop_name'] for stop in stops_data]

    #rendering all the data necessary to be shown on UI
    return render_template('index_draft.html', map=map_html, stop_names=stop_names, shapes_data=shapes_data, stops_data=stops_data)


def get_route(trip_id):
    #loop through routes to find route containing the trip_id given
    for route_id, route_details in final_updated_routes_with_stops_data.items():
        if trip_id in route_details.get('trip_ids', []):
            return route_details.get('route_long_name', 'Unknown Route') #if it is found, return route name
    return 'Unknown Route' #else return 'Unknown Route'

#route for live bus data
@app.route('/get_bus_data')
def get_bus_data():
    #live bus data
    vehicle_positions = fetch_data("https://passio3.com/harvard/passioTransit/gtfs/realtime/vehiclePositions.json")
    bus_information = []
    if vehicle_positions and 'entity' in vehicle_positions:
        for entity in vehicle_positions['entity']:
            vehicle = entity.get('vehicle', {})
            position = vehicle.get('position', {})
            lat = position.get('latitude')
            lon = position.get('longitude')
            trip_id = vehicle.get('trip', {}).get('trip_id')
            vehicle_id = vehicle.get('vehicle', {}).get('id')
            route_name = get_route(trip_id) #route name for the respective trip_id
            if lat and lon:
                bus_information.append({
                    'latitude': lat, 
                    'longitude': lon,
                    'route_name': route_name }) #lat, lon, route_name appended to bus information
        return jsonify(bus_information) #return data as jsonify data so it is compatible

#route for SHOW SCHEDULE button - shows all busses and all the times each day that they will leave the inputted starting point to get to the inputted stop destination
@app.route('/get_schedule', methods=['POST'])
def get_schedule():
    data = request.json
    print("Received schedule request data:", data)  # Log the incoming data
    start_stop_name = data['start_stop']
    destination_stop_name = data['destination_stop']
    #stop ids based off of name
    start_stop_id = next((stop['stop_id'] for stop in stops_data if stop['stop_name'] == start_stop_name), None)
    destination_stop_id = next((stop['stop_id'] for stop in stops_data if stop['stop_name'] == destination_stop_name), None)
    print(f"Start stop ID: {start_stop_id}, Destination stop ID: {destination_stop_id}")

    valid_routes = []
    #filters for routes that go through starting stop and destination stop
    for route_id, route_details in final_updated_routes_with_stops_data.items():
        if start_stop_name in route_details['stops'] and destination_stop_name in route_details['stops']:
            valid_routes.append(route_id)
    print(f"Valid routes: {valid_routes}")

    #departure times for each valid route from starting stop
    schedules = []
    for route_id in valid_routes:
        #finds respective trip id
        trip_ids = final_updated_routes_with_stops_data[route_id]['trip_ids']
        #departure times for each trip from starting stop
        departure_times = []
        for trip_id in trip_ids:
            if trip_id in stop_times_data:
                for stop_time in stop_times_data[trip_id]:
                    if stop_time['stop_id'] == start_stop_id:
                        #checks format of time (12 or 24 hour)
                        try:
                            departure_time = datetime.strptime(stop_time['departure_time'], '%I:%M:%S %p').strftime('%H:%M:%S')
                        except ValueError:
                            departure_time = stop_time['departure_time']
                        departure_times.append(departure_time)
        #adds route and departure times to schedules
        schedules.append({
            'route_name': final_updated_routes_with_stops_data[route_id]['route_long_name'],
            'departure_times': sorted(departure_times)  #makes sure departure times are sorted
        })
    print(f"Schedules: {schedules}")

    return jsonify(schedules)

def get_next_bus(departure_times, current_time, eta_seconds):
    #all times datetime objects for easy comparison within function
    current_time_datetime = datetime.strptime(current_time, '%H:%M:%S')
    departure_times_datetime = [datetime.strptime(time, '%H:%M:%S') for time in departure_times]
    
    #Chat GPT helped translate my hope to create two possibilities of "future_times" based off of the condition eta_seconds < 0, into the conditional logic below
    #eta_seconds < 0 mean that the bus has departed, the bus has left
    if eta_seconds < 0:
        future_times = [time for time in departure_times_datetime if time > current_time_datetime] #future_times only consists of times which are greater than the current time if eta_seconds < 0
    else:
        #if bus hasn't departed, include time closest to current_time even if it's in the "past" because this means that the bus is late
        future_times = [time for time in departure_times_datetime if time >= current_time_datetime]

    if not future_times:
        return "No more buses today"
    
    #closest "future" time (some cases in the "past")
    next_bus_time = future_times[0]
    return next_bus_time.strftime('%H:%M:%S') #Chat GPT also helped understand how to use this syntax with datetime objects so I can easily compare times

@app.route('/search_routes', methods=['POST'])
def search_routes():
    data = request.json
    print("Received search data:", data)
    start_stop_name = data['start_stop']
    destination_stop_name = data['destination_stop']

    start_stop_id = next((stop['stop_id'] for stop in stops_data if stop['stop_name'] == start_stop_name), None)
    destination_stop_id = next((stop['stop_id'] for stop in stops_data if stop['stop_name'] == destination_stop_name), None)
    print(f"Start stop ID: {start_stop_id}, Destination stop ID: {destination_stop_id}")

    valid_trip_ids = []

    #loop through all trips in a respective stop_id
    for trip_id, stops in stop_times_data.items():
        stop_ids = [stop['stop_id'] for stop in stops]
        #check both start and destination stops are in trip
        if start_stop_id in stop_ids and destination_stop_id in stop_ids:
            valid_trip_ids.append(trip_id)


    #real_time_udpates
    trip_updates = fetch_trip_updates()
    real_time_trip_ids = trip_ids_from_trip_updates(trip_updates) 

    #eta for starting stop
    etas = calculate_stop_eta(trip_updates, start_stop_id)

    #filter so valid_trip_ids only have trips which show up in the live updates
    valid_live_trip_ids = [trip_id for trip_id in valid_trip_ids if trip_id in real_time_trip_ids]
    routes_with_etas = {}
    for route_id, route_details in final_updated_routes_with_stops_data.items():
        for trip_id in route_details['trip_ids']:
            if trip_id in valid_live_trip_ids:
                route_name = route_details['route_long_name']
                eta_seconds = etas.get(trip_id)
                if eta_seconds is not None:
                    if eta_seconds < routes_with_etas[route_name] or route_name not in routes_with_etas:
                        routes_with_etas[route_name] = eta_seconds  #earliest ETA
    
    response = []
    for route_long_name, eta_seconds in routes_with_etas.items():
        #get key for respective route_long_name
        route_key = next((key for key, value in final_updated_routes_with_stops_data.items() if value['route_long_name'] == route_long_name), None)
        if route_key is None:
            continue  #if there is no key, go to the next route
        
        if eta_seconds < 0:
            readable_eta = "Bus has departed"
        else:
            eta_minutes = int(eta_seconds // 60)
            eta_seconds_remainder = int(eta_seconds % 60)
            readable_eta = f"{eta_minutes} min {eta_seconds_remainder} sec" #get eta into mins and seconds
        
        #static times from stop_times.json
        static_arrival_times = []
        for trip_id in final_updated_routes_with_stops_data[route_key]['trip_ids']:
            if trip_id in stop_times_data:
                static_arrival_times += [stop['arrival_time'] for stop in stop_times_data[trip_id] if stop['stop_id'] == start_stop_id]
        
        #sorted times and removed duplicates
        static_arrival_times = sorted(set(static_arrival_times))
        current_time = datetime.now().strftime('%H:%M:%S')

        #get next bus arrival time
        next_bus_arrival = get_next_bus(static_arrival_times, current_time, eta_seconds)

        #now response has route name, ETA, and static arrival time of the next bus
        response.append({"route_name": route_long_name, "eta": readable_eta, "scheduled_arrival": next_bus_arrival, "eta_seconds": eta_seconds, })

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)