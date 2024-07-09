import datetime
import folium
import json
import math

from folium.plugins.timeline import Timeline, TimelineSlider
from folium.plugins import TimestampedGeoJson

# Configure the variables below as well as on lines 69-71 for the desired map
# The values set here will generate a map centered on the US with zoom level
# such that the lower 48 are visible.
# The filter distance limit is large enough to include anything in that same area.

# file should be in the same directory as this script file, set the name here
file_name = 'reviews.json'
# if you wish to filter out reviews beyond a certain radius from a particular point
# enter the point coordinates and distance here
limit_center_lat = 33.76906041450119
limit_center_lng = -84.39328701822208
limit_distance = 10000
# central point for the map default display, map can be moved and zoomed
map_center_lat = 39.39743427480445
map_center_lng = -97.2449760357087
# smaller number is a bigger view, larger number is closer in
zoom_level = 5


def haversine(lat1, lon1, lat2, lon2):
    R = 6372800  # Earth radius in meters
    conv_metric = 1000

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2

    distance = 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a)) / conv_metric
    return distance

def produce_map():
    with open(file_name, encoding='utf8') as f:
        data = json.load(f)
    m = folium.Map(location=(map_center_lat, map_center_lng), zoom_start=zoom_level)

    count = 0
    r_data = {"type": "FeatureCollection", "name":"today reviews", "features": []}

    for d in data:
        if d['type'] != 'NEW':
            continue
        if haversine(limit_center_lat, limit_center_lng, d['lat'], d['lng']) <= limit_distance:
            timestamp = datetime.datetime.utcfromtimestamp(int(d['ts'])/1000)
            
            single = { "type": "Feature", "id": count, "properties": { "times": [timestamp.strftime("%Y-%m-%dT%H:%M:%S")], 'style': {'color': ''},
                    'icon': 'circle',
                    'iconstyle': {
                        'fillOpacity': 0.8,
                        'stroke': 'true',
                        'radius': 5
                    }}, "geometry": { "type": "Point", "coordinates": [ d['lng'],d['lat'] ] } }
            r_data['features'].append(single)
            count += 1

    # https://www.digi.com/resources/documentation/digidocs/90001488-13/reference/r_iso_8601_duration_format.htm
    # period is the amount of time between each step or tick in the time slider
    # duration is the total amount of time it will cover
    # The default here will display the most recent 24 hours in 1 minute increments
    # transition_time is how long between each tick when the slider auto-plays in milliseconds
    TimestampedGeoJson(r_data,
                       period='PT1M',
                       duration='P1DT',
                       transition_time=50).add_to(m)    

    m.save("index.html")

produce_map()
