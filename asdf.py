from datetime import datetime
import pytz

# Assume your API returns times in UTC
utc_zone = pytz.utc

# If you know the specific timezone of your trip updates, replace 'America/New_York' with it
local_zone = pytz.timezone('America/New_York')

# Current time in UTC
current_time_utc = datetime.now(pytz.utc)

# Convert current time to local timezone
current_time_local = current_time_utc.astimezone(local_zone)

print("Current Time in UTC:", current_time_utc)
print("Current Time in Local Timezone:", current_time_local)

# Example Unix timestamp from your trip updates
unix_timestamp = 1710978483  # This is an example; use your actual data here

# Convert Unix timestamp to datetime in UTC
time_utc = datetime.utcfromtimestamp(unix_timestamp).replace(tzinfo=pytz.utc)

# Convert to local timezone if needed
time_local = time_utc.astimezone(local_zone)

print("Time from Trip Update in UTC:", time_utc)
print("Time from Trip Update in Local Timezone:", time_local)

