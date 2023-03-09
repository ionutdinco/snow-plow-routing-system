import requests, json


def apiDirectionsDistance(lat_start, long_start, lat_end, long_end):

    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
    r = requests.get(url + 'origins=' + f'{lat_start},{long_start}' +
                     '&destinations=' + f'{lat_end},{long_end}' +
                     '&mode=' + 'car' +
                     '&key=' + 'AIzaSyCglz6glPyxb2DjZVpbmH1wvvK1dXXQFgo')
    x = r.json()
    #print(x)
    return x['rows'][0]['elements'][0]['distance']['value']

if __name__ == "__main__":
    apiDirectionsDistance(47.736262675288614, 26.64070234460174, 47.736262675288614, 26.74070234460174)


# def GAThreads(G, clusters_partition):
#
#     threads = []
#     for cluster in clusters_partition:
#         population_size = len(clusters_partition[cluster])
#         nodes = clusters_partition[cluster]
#
#         thread_solve_tsp = threading.Thread(target=thread_function, args=(population_size, nodes))
#         threads.append(thread_solve_tsp)
#         thread_solve_tsp.start()
#
#     for thread in threads:
#         thread.join()
#     coord = []
#     for x in final_routes[0]:
#         coord.append(G.nodes[x])
#     return json.dumps(coord)


# def thread_function(population_size, nodes):
#     global final_routes
#     population = []
#     print(len(nodes))
#     for index in range(100):
#         population.append(createRoute(nodes.copy()))
#
#     for i in range(0, 400):
#         population = nextGeneration(population, 30, 0.01)
#         bestRouteIndex = rankRoutes(population)[0][0]
#         bestRoute = population[bestRouteIndex]
#         final_routes.append(bestRoute)
#         # print("\n\n\n\n**************************")
#         # print(len(bestRoute))
#         # print(bestRoute)
#         # print(Individual(bestRoute).routeDistance())
#         # print("\n\n\n\n**************************")
#     print("\n\n\n\n**************************")
#     print(len(bestRoute))
#     print(bestRoute)
#     print(Individual(bestRoute).routeDistance())
#     print("\n\n\n\n**************************")
#     container_nodes = []
#     # for i in range(0, len(bestRoute) - 1):
#     #     distance = nx.shortest_path_length(initialG,bestRoute[i],bestRoute[i+1], weight='length')
#     #     print(distance)
#     #     if d < 10.0:
#     #         container_nodes.append(bestRoute[i+1])
#     # for rl in container_nodes:
#     #     bestRoute.remove(el)
