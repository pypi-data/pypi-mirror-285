from garmin import login, get_activities
from mapping import create_map

"""Example: Plot all runs from June 2024 onto a leaflet.js map."""

# Login to Garmin Connect with OAuth2
garmin_client = login()

# Create a new empty leaflet.js map
running_map = create_map()

# Get data for all runs in June 2024
activites = get_activities(garmin_client, "running", "2024-06-01", "2024-06-30")
for activity in activites:
    activity.plot(running_map)

# Write the leaflet.js map to disk
running_map.save("runs.html")