import json
import requests
import math
import queue
import random
import sys
import os
from scipy import spatial
from networkx.algorithms import approximation as approx
import pandas as pd
import operator
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import numpy
import threading
from shapely.geometry import Point
import logging as lg
from osmnx.utils import log
import time
from scipy.spatial import cKDTree
from sklearn.neighbors import BallTree
from enum import Enum
import ModelDataOSM
import ConfigModelOSM

# import snowplowrouting.MapDataTools.APIDirections as dir

initialG = None
distance_matrix = None
distance_matrix_api = {}
final_routes = []
real_start_node = -1
temp_start_node = -1
dist_real_temp = 0
temp_start_nodes = []

class ConfigType(Enum):
    PrimS = "PrimaryStreets"
    PrimSecS = "PrimarySecondaryStreets"
    CountyS = "CountyStreets"

def apiDirectionsDistance(origins, destinations):
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
    r = requests.get(url + 'origins=' + origins +
                     '&destinations=' + destinations +
                     '&mode=' + 'car' +
                     '&key=' + 'AIzaSyCglz6glPyxb2DjZVpbmH1wvvK1dXXQFgo')
    x = r.json()
    return x

def check_valid_vertex(neighbours, partition) -> bool:
    if len(partition) == 0:
        return True
    for neighbour in neighbours:
        if neighbour in partition:
            return True
    return False

def get_shorthest_path_centroid(G, node, centroids, clusters_partition, maxElements, centroids_coords, subpartition_complete):
    min_length = sys.maxsize
    closer_centroid = None

    nodes = nx.nodes(G)
    neighbours = list(nx.all_neighbors(G, node))
    for centroid in centroids:
        current_length = math.sqrt((pow(centroids_coords[centroid]['x'] - nodes[node]['x'], 2) + pow(centroids_coords[centroid]['y'] - nodes[node]['y'], 2)))
        valid_vertex = check_valid_vertex(neighbours, clusters_partition[centroid])
        if current_length < min_length and (len(clusters_partition[centroid]) < maxElements or subpartition_complete) and valid_vertex:
            min_length = current_length
            closer_centroid = centroid
    return closer_centroid

def geo_coords_sum(G, nodes_partition):
    nodes = nx.nodes(G)
    xj = 0
    yj = 0

    for node_id in nodes_partition:
        xj += nodes[node_id]["x"]
        yj += nodes[node_id]["y"]

    return xj, yj

def update_centroid_pos(G, xj, yj, centroid, centroids_predecesor, pos, centroids_coords):
    if xj == centroids_coords[centroid]['x'] and yj == centroids_coords[centroid]['y']:
        return centroid
    for old_centroid in centroids_predecesor:
        if xj == centroids_coords[old_centroid]['x'] and yj == centroids_coords[old_centroid]['y']:
            return centroid
    centroids_predecesor[pos] = centroid
    new_centroid = random.randint(11111111, 99999999)
    centroids_coords[new_centroid] = {'x': xj, 'y': yj}
    return new_centroid

def add_shortest_path_from_start_node(G, clusters):
    global initialG, temp_start_node, dist_real_temp, temp_start_nodes

    dest_node = None
    pos = 0
    for centroid in clusters:
        global_min_length = sys.maxsize
        for element in clusters[centroid]:
            try:
                len = nx.shortest_path_length(initialG, temp_start_node, element, weight='length')
            except:
                len = sys.maxsize
            if len < global_min_length:
                global_min_length = len
                dest_node = element
        temp_start_nodes.append(dest_node)
    print("Start nodes:", temp_start_nodes)

def showPartition(G, partition, nodesId):
    for id in list(nodesId):
        if id not in partition:
            G.remove_node(id)
    try:
        ox.plot_graph(G)
    except:
        return

clusters_count_values = lambda clusters_partition: len([id_node for cluster in clusters_partition.values() for id_node in cluster])

def clustering_kmeans_approach(G, nr_vehicles, distribution_margin):
    nodesId = nx.nodes(G)
    clusters_partition = None
    centroids = random.sample(nodesId, nr_vehicles)
    centroids_coords = {centroid:{ "x": nodesId[centroid]["x"], "y": nodesId[centroid]["y"]} for centroid in centroids.copy()}
    centroids_predecesor, maxElements = centroids.copy(), math.ceil(len(nodesId) / nr_vehicles)
    subpartition_complete = over = visited_vertex = False
    ready = dead_lock = 0
    network_vertexes, visited_nodes = list(nodesId), {node: False for node in list(nodesId)}
    random.shuffle(network_vertexes)
    while not over:
        clusters_partition = {centroid: [] for centroid in centroids}
        for node in network_vertexes:
            centroid = get_shorthest_path_centroid(G, node, centroids, clusters_partition, maxElements, centroids_coords, subpartition_complete)
            if centroid:
                clusters_partition[centroid].append(node)
                visited_nodes[node] = True
                dead_lock = 0
            else:
                network_vertexes.append(node)
            dead_lock += 1
            if dead_lock >= len(nodesId):
                break
        clusters_elements = clusters_count_values(clusters_partition)
        if clusters_elements >= len(nodesId) - distribution_margin:
            # print(clusters_elements)
            subpartition_complete = True
        print(clusters_elements)
        if not subpartition_complete:
            pos = 0
            for centroid in centroids.copy():
                xj, yj = geo_coords_sum(G, clusters_partition[centroid])
                Xj = xj / abs(len(clusters_partition[centroid]))
                Yj = yj / abs(len(clusters_partition[centroid]))
                osm_id = update_centroid_pos(G, Xj, Yj, centroid, centroids_predecesor, pos, centroids_coords)
                pos += 1
                if centroid != osm_id:
                    centroids.remove(centroid)
                    centroids.append(osm_id)
                else:
                    ready += 1
        else:
            keys = [k for k, v in visited_nodes.items() if v == False]
            for k in keys:
                centroid = get_shorthest_path_centroid(G, k, centroids, clusters_partition, maxElements,
                                                       centroids_coords, subpartition_complete)
                if centroid:
                    clusters_partition[centroid].append(k)
                else:
                    keys.append(k)
        if ready == nr_vehicles or clusters_count_values(clusters_partition) == len(nodesId):
            over = True
        else:
            ready = 0
            network_vertexes, visited_nodes = list(nodesId), {node: False for node in list(nodesId)}
            random.shuffle(network_vertexes)

    # for centroid, partition in clusters_partition.items():
    #     showPartition(G.copy(), partition, nodesId)

    for p in clusters_partition:
        print(clusters_partition[p])

    # add_shortest_path_from_start_node(G, clusters_partition)
    return clusters_partition

def configArea(county, city):
    G = None
    file_name = county.lower() + '-' + city.lower() + '.osm'
    dir_path = os.path.abspath('.')
    file_path = dir_path + '/' + file_name
    try:
        G = ox.load_graphml(file_path)
        print("exista***********")
    except:
        print("nu exista***********")
        query = {'county': county, 'city': city}
        G = ox.graph_from_place(query, network_type='drive')
        ox.save_graphml(G, file_name)
    return G

def getRoundaboutList(G, config_mode):
    edges = numpy.copy(G.edges)

    if config_mode == 'PrimaryStreets':
        for edge in edges:
            x, y, z = edge
            if G[x][y][0]["highway"] != "primary" or 'junction' not in G[x][y][0]:
                G.remove_edge(x, y)

    if config_mode == 'PrimarySecondaryStreets':
        for edge in edges:
            x, y, z = edge
            if G[x][y][0]["highway"] != "primary" and G[x][y][0]["highway"] != "secondary" or 'junction' not in G[x][y][0]:
                G.remove_edge(x, y)
    G.remove_nodes_from(list(nx.isolates(G)))
    H = G.to_undirected()
    junctionList = list(nx.connected_components(H))
    roundaboutDict = {i: junctionList[i] for i in range(len([x for x in junctionList]))}
    return (roundaboutDict, G.nodes)

def getPartitionGraph(G, partition):
    for id in list(nx.nodes(G)):
        if id not in partition:
            G.remove_node(id)
    try:
        ox.plot_graph(G)
    except:
        print("error")
    return G

def prepareG(G, config_mode):
    G = configArea("Botosani", "Botosani")
    roundaboutDict, roundaboutNodes = getRoundaboutList(G.copy(), 'PrimarySecondaryStreets')
    print(roundaboutDict)

if __name__ == "__main__":
    start_node = {"x": 47.736262675288614, "y": 26.64070234460174};
    # routing(start_node["x"], start_node["y"],
    #         6, "Botosani", "Botosani", "PrimarySecondaryStreets")
    G = configArea("Botosani", "Botosani")
    roundaboutDict, roundaboutNodes = getRoundaboutList(G.copy(), 'PrimarySecondaryStreets')
    print(roundaboutDict)
    prepareG(G.copy(), 'PrimarySecondaryStreets', roundaboutDict, roundaboutNodes)


# class Individual:
#     def __init__(self, chromosome) -> None:
#         self.route = chromosome
#         self.fitness = 0.0
#         self.distance = 0
#
#     def __lt__(self, other):
#         return self.fitness < other.fitness
#
#     def __gt__(self, other):
#         return self.fitness > other.fitness
#
#     def routeDistance(self):
#         if self.distance == 0:
#             pathDistance = 0
#             for i in range(0, len(self.route)):
#                 fromCity = self.route[i]
#                 toCity = None
#                 if i + 1 < len(self.route):
#                     toCity = self.route[i + 1]
#                 else:
#                     toCity = self.route[0]
#                 try:
#                     inner_distance = distance_matrix[fromCity][toCity]
#                     pathDistance += inner_distance
#                 except:
#                     pathDistance += 200000
#             self.distance = pathDistance
#         return self.distance
#
#     def routeFitness(self):
#         if self.fitness == 0.0:
#             dist = float(self.routeDistance())
#             if dist != 0.0:
#                 self.fitness = 1 / float(self.routeDistance())
#         return self.fitness
#
#
# def createRoute(cityList):
#     global temp_start_nodes
#     start_node = None
#     for node in temp_start_nodes:
#         if node in cityList:
#             start_node = node
#             index = cityList.index(node)
#             cityList.pop(index)
#             break
#
#     route = random.sample(cityList, len(cityList))
#     route.insert(0, start_node)
#     return route
#
#
# def rankRoutes(population):
#     fitnessResults = {}
#     for i in range(0, len(population)):
#         fitnessResults[i] = Individual(population[i]).routeFitness()
#     return sorted(fitnessResults.items(), key=operator.itemgetter(1), reverse=True)
#
#
# def selection(popRanked, eliteSize):
#     selectionResults = []
#     df = pd.DataFrame(numpy.array(popRanked), columns=["Index", "Fitness"])
#     df['cum_sum'] = df.Fitness.cumsum()
#     df['cum_perc'] = 100 * df.cum_sum / df.Fitness.sum()
#
#     for i in range(0, eliteSize):
#         selectionResults.append(popRanked[i][0])
#     for i in range(0, len(popRanked) - eliteSize):
#         pick = 100 * random.random()
#         for i in range(0, len(popRanked)):
#             if pick <= df.iat[i, 3]:
#                 selectionResults.append(popRanked[i][0])
#                 break
#     return selectionResults
#
#
# def matingPool(population, selectionResults):
#     matingpool = []
#     for i in range(0, len(selectionResults)):
#         index = selectionResults[i]
#         matingpool.append(population[index])
#     return matingpool
#
#
# def orderedCrossover(parent1, parent2):
#     child = []
#     childP1 = []
#     childP2 = []
#
#     geneA = int(random.randint(1, len(parent1) - 1))
#     geneB = int(random.randint(1, len(parent1) - 1))
#
#     startGene = min(geneA, geneB)
#     endGene = max(geneA, geneB)
#
#     for i in range(startGene, endGene):
#         childP1.append(parent1[i])
#
#     childP2 = [x for x in parent2 if x not in childP1]
#     child = childP2 + childP1
#     return child
#
#
# def CrossoverPopulation(matingpool, eliteSize):
#     children = []
#     length = len(matingpool) - eliteSize
#     pool = random.sample(matingpool, len(matingpool))
#
#     for i in range(0, eliteSize):
#         children.append(matingpool[i])
#
#     for i in range(0, length):
#         child = orderedCrossover(pool[i], pool[len(matingpool) - i - 1])
#         children.append(child)
#     return children
#
#
# def mutate(individual, mutationRate):
#     for swapped in range(1, len(individual) - 1):
#         if (random.random() < mutationRate):
#             swapWith = random.randint(1, len(individual) - 1)
#
#             node1 = individual[swapped]
#             node2 = individual[swapWith]
#
#             individual[swapped] = node2
#             individual[swapWith] = node1
#     return individual
#
#
# def mutatePopulation(population, mutationRate):
#     mutatedPop = []
#
#     for ind in range(0, len(population)):
#         mutatedInd = mutate(population[ind], mutationRate)
#         mutatedPop.append(mutatedInd)
#     return mutatedPop
#
#
# def update_distances(population):
#     global distance_matrix, distance_matrix_api
#     origins = ""
#     origins_id = []
#     destinations = ""
#     destinations_id = []
#     counter = 0
#     for route in population:
#         for i in range(0, len(route)):
#             fromCity = route[i]
#             toCity = None
#             if i + 1 < len(route):
#                 toCity = route[i + 1]
#             else:
#                 toCity = route[0]
#             try:
#                 distance = distance_matrix[fromCity][toCity]
#             except:
#                 if counter == 0:
#                     origins = "{},{}".format(str(initialG.nodes[fromCity]["y"]), str(initialG.nodes[fromCity]["x"]))
#                     destinations = "{},{}".format(str(initialG.nodes[toCity]["y"]), str(initialG.nodes[toCity]["x"]))
#                     origins_id.append(fromCity)
#                     destinations_id.append(toCity)
#                 else:
#                     origins = "|".join([origins, "{},{}".format(str(initialG.nodes[fromCity]["y"]),
#                                                                 str(initialG.nodes[fromCity]["x"]))])
#                     destinations = "|".join([destinations, "{},{}".format(str(initialG.nodes[toCity]["y"]),
#                                                                           str(initialG.nodes[toCity]["x"]))])
#                     origins_id.append(fromCity)
#                     destinations_id.append(toCity)
#                 counter += 1
#                 if counter == 10:
#                     distances = apiDirectionsDistance(origins, destinations)
#                     i = 0
#                     for line in distances['rows']:
#                         j = 0
#                         for column in line['elements']:
#                             try:
#                                 distance_matrix[origins_id[i]]
#                                 distance_matrix[origins_id[i]][destinations_id[j]] = column['distance']['value']
#                                 # print(column['distance']['value'])
#                             except:
#                                 distance_matrix[origins_id[i]] = {}
#                                 distance_matrix[origins_id[i]][destinations_id[j]] = column['distance']['value']
#                             j += 1
#                         i += 1
#                         # dist[origins_id[i]][destinations_id[j]] = column['distance']['value']
#                     counter = 0
#                     origins = ""
#                     destinations = ""
#
#
# def nextGeneration(currentGen, eliteSize, mutationRate):
#     update_distances(currentGen)
#     popRanked = rankRoutes(currentGen)
#     selectionResults = selection(popRanked, eliteSize)
#     matingpool = matingPool(currentGen, selectionResults)
#     children = CrossoverPopulation(matingpool, eliteSize)
#     nextGeneration = mutatePopulation(children, mutationRate)
#     return nextGeneration
#
#
# def GA(G, clusters_partition):
#     global final_routes
#     progress = []
#     for cluster in clusters_partition:
#         population_size = len(clusters_partition[cluster])
#         nodes = clusters_partition[cluster]
#         population = []
#         route_progress = []
#         for index in range(100):
#             population.append(createRoute(nodes.copy()))
#         route_progress.append(1 / rankRoutes(population)[0][1])
#
#         for i in range(0, 500):
#             population = nextGeneration(population, 30, 0.01)
#             route_progress.append(1 / rankRoutes(population)[0][1])
#         print(rankRoutes(population))
#         progress.append(route_progress)
#         bestRouteIndex = rankRoutes(population)[0][0]
#         bestRoute = population[bestRouteIndex]
#         final_routes.append(bestRoute)
#         print("\n\n\n\n**************************")
#         print(Individual(bestRoute).routeDistance())
#
#
#
#
# def routing(lat_start, long_start, nr_vehicles, county, city, config_mode):
#     G = prepare_data(configArea(county, city), lat_start, long_start, config_mode)
#     clusters_partition = clustering_kmeans(G, nr_vehicles)
#     GA(G, clusters_partition)
#
#     routes = []
#     driver_route = {}
#     for route in final_routes:
#         route_points = []
#         counter = 0
#         lap = 0
#         for node in route:
#             route_points.append("{},{}".format(str(G.nodes[node]["y"]), str(G.nodes[node]["x"])))
#             counter += 1
#             if counter == 24:
#                 waypoints = route_points[0]
#                 for i in range(1, len(route_points)):
#                     waypoints = "|".join([waypoints, route_points[i]])
#                 driver_route[lap] = waypoints
#                 lap += 1
#                 counter = 0
#                 route_points = []
#         routes.append(driver_route)
#
#     return routes


# def get_shorthest_path_centroid(G, node, centroids, clusters_partition, maxElements, centroids_coords):
#     min_length = sys.maxsize
#     second_min_length = sys.maxsize
#     closer_centroid = None
#     second_closer_centroid = None
#     out_node = None
#     nodes = nx.nodes(G)
#
#     for centroid in centroids:
#         current_length = math.sqrt((pow(centroids_coords[centroid]['x'] - nodes[node]['x'], 2) + pow(centroids_coords[centroid]['y'] - nodes[node]['y'], 2)))
#         if current_length < min_length:
#             second_closer_centroid = closer_centroid
#             second_min_length = min_length
#             min_length = current_length
#             closer_centroid = centroid
#         elif current_length < second_min_length:
#             second_closer_centroid = centroid
#             second_min_length = current_length
#     partition = clusters_partition[closer_centroid]
#     if len(partition) >= maxElements:
#         max_key = max(partition, key=partition.get)
#         if min_length < partition[max_key]:
#             out_node = max_key
#             del partition[max_key]
#         else:
#             print("centroids", second_closer_centroid)
#             return (second_closer_centroid, second_min_length, out_node)
#         print("daaaaaaaaa")
#     print(centroids)
#     return (closer_centroid, min_length, out_node)