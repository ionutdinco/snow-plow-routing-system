from django.conf import settings
from urllib.parse import urlencode
import requests
import json
import datetime
from django.http import JsonResponse


def Directions(*args, **kwargs):
    '''
    Handles directions from Google
    '''

    route = kwargs.get("coords")
    lat_start = kwargs.get("depot_lat")
    long_start = kwargs.get("depot_long")
    origin = f'{lat_start},{long_start}'
    results = []
    ga_routes = []
    origins = []
    destinations = []
    waypts = []

    for i in range(0, len(route)):
        ga_routes.append(route[str(i)])

    for i in range(0, len(route)):
        temp = ga_routes[i]
        coords = temp.rsplit('|', 1)
        waypoints = coords[0]
        waypts.append(waypoints)
        destination = coords[1]
        origins.append(origin)
        destinations.append(destination)

        # print("temp",temp,"\n\norigin:", origin, "\n\ndest:",destination)
        result = {}
        result = requests.get(
            'https://maps.googleapis.com/maps/api/directions/json?',
            params={
                'origin': origin,
                'destination': destination,
                'waypoints': waypoints,
                "key": settings.GOOGLE_MAPS_API_KEY
            })

        directions = result.json()
        # print("\n\ndirections:\n", directions)
        distance = 0
        duration = 0
        route_list = []
        if directions["status"] == "OK":

            routes = directions["routes"][0]["legs"]

            for route in range(len(routes)):
                distance += int(routes[route]["distance"]["value"])
                duration += int(routes[route]["duration"]["value"])

                route_step = {
                    'origin': routes[route]["start_address"],
                    'destination': routes[route]["end_address"],
                    'distance': routes[route]["distance"]["text"],
                    'duration': routes[route]["duration"]["text"],

                    'steps': [
                        [
                            s["distance"]["text"],
                            s["duration"]["text"],
                            s["html_instructions"],

                        ]
                        for s in routes[route]["steps"]]
                }

                route_list.append(route_step)
            data = {
                        "origin": origin,
                        "destination": destination,
                        "distance": f"{round(distance / 1000, 2)} Km",
                        "duration": duration,
                        "route": route_list
                    }
            results.append(data)
            origin = destination
        else:
            print("\n\n\nprobleme")

    return results, origins, destinations, waypts