import sys
from munkres import Munkres
import numpy
import networkx as nx
from abc import ABC, abstractmethod

class Vertex:

    def __init__(self, id, roundabout):
        self.id = id
        self.roundabout = roundabout

    def __eq__(self, another):
        return hasattr(another, 'id') and self.id == another.id

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return '(' + str(self.id) + ', ' + str(self.roundabout) + ')'

class ModelDataOSM:

    def __init__(self):
        self.adjVertices = {}
        self.vertices = {}
        self.startNodeId = 0
        self.length = 0

    def __str__(self):
        print("dVert",self.adjVertices)
        print("--------------------------------------\n")
        print("vert",self.vertices)
        print("--------------------------------------\n")
        for key, val in self.adjVertices.items():
            print(key)
            for el, b in val:
                print("\t", el, " ", b)
            print("\n--------------")

    def initAdj(self, adj):
        self.adjVertices = adj

    def initStartNode(self, id):
        self.startNodeId = id

    def addVertex(self, vertexId):
        self.adjVertices[vertexId] = []

    def getVertex(self, id):
        for vertex in self.adjVertices.items():
            if vertex[0].id == id:
                return vertex[0]

    def addEdge(self, id1, roundabout1, id2, roundabout2, lanes, length):
        print("addEdge:", lanes)
        v1 = Vertex(id1, roundabout1)
        if not id1 in self.vertices.keys():
            self.vertices[id1] = v1
            self.addVertex(id1)
        # else:
        #     print("from object:", self.vertices[id1])
        #     print("adjj:", self.adjVertices[id2])
        arcs = int(lanes) // 2
        while arcs > 0:
            self.adjVertices[id1].append((id2, int(length)))
            self.length += int(length)
            arcs -= 1

    def addOnewayEdge(self, id1, roundabout1, id2, roundabout2, lanes, length):
        arcs = int(lanes)
        if arcs > 2:
            arcs = 2
        print("addOnewayEdge:", lanes)
        v1 = Vertex(id1, roundabout1)
        if not id1 in self.vertices.keys():
            self.vertices[id1] = v1
            self.addVertex(id1)

        while arcs > 0:
            self.adjVertices[id1].append((id2, int(length)))
            self.length += int(length)
            arcs -= 1

    def popEdge(self, v, pred):
        print("adjV------>\n",self.adjVertices[v])
        adjs = self.adjVertices[v][0]
        if pred == None:
            self.adjVertices[v].remove(adjs)
            return adjs[0]
        else:
            for tupleNode in self.adjVertices[v]:
                if tupleNode[0] != pred:
                    adjs = tupleNode[0]
                    self.adjVertices[v].remove(tupleNode)
                    return adjs
            del(self.adjVertices[v][0])
            return pred

    def getNextVertex(self, v1, visited):
        adjs = self.adjVertices[v1]
        if pred == None:
            return adjs[0][0]
        else:
            first_match = next(
                (item[0] for item in adjs if not visited[item[0]]),
                None
            )
            return first_match

    def dfsTraversel(self, visited, node, graphTranspose):
        visited[node] = True
        if graphTranspose is not None:
            for entity in graphTranspose.adjVertices[node]:
                if not visited[entity]:
                    self.dfsTraversel(visited, entity, graphTranspose)
        else:
            for entity in self.adjVertices[node]:
                if not visited[entity[0]]:
                    self.dfsTraversel(visited, entity[0], None)

    def getTranspose(self):
        trG = ModelDataOSM()
        trG.initAdj({key: [] for key in self.adjVertices})
        for key in self.adjVertices:
            for el, len in self.adjVertices[key]:
                trG.adjVertices[el].append(key)
        return trG

    def test(self):
        v1 = Vertex(1767, False)
        self.addVertex(v1);
        self.adjVertices[v1].append((v1, True))
        if v1 not in self.adjVertices.keys():
            v2 = Vertex(1767, False)
            self.addVertex(v2)
        print('vertexes->', self.adjVertices.keys())

    def checkStronglyConnected(self) -> bool:
        visited = {i: False for i in self.adjVertices}
        self.dfsTraversel(visited, self.startNodeId, None)
        if any(visited[i] == False for i in visited.keys()):
            return False
        graphTranspose = self.getTranspose()
        visited = {i: False for i in self.adjVertices}
        self.dfsTraversel(visited, self.startNodeId, graphTranspose)
        print("visited:\n", visited)
        if any(visited[i] == False for i in visited.keys()):
            return False
        return True

    def checkImbalancedNodes(self) -> tuple:
        inDegrees = {i: 0 for i in self.adjVertices.keys()}
        outDegrees = {i: 0 for i in self.adjVertices.keys()}

        for key, value in self.adjVertices.items():
            outDegrees[key] = len(value)
            for el, length in value:
                inDegrees[el] += 1

        imbalancedNodes = {i: outDegrees[i] - inDegrees[i] for i in self.adjVertices.keys()}
        print("imb------>", imbalancedNodes)
        negativeVertex = []
        pozitiveVertex = []
        for key, val in imbalancedNodes.items():
            for i in range(abs(val)):
                if val < 0:
                    negativeVertex.append(key)
                else:
                    pozitiveVertex.append(key)
        print("\n\nLen neg:", len(negativeVertex))
        print("\n\nLen poz:", len(pozitiveVertex))
        return (negativeVertex, pozitiveVertex)

    def getDist(self, source, dest):
        if source is dest:
            return 0
        elem = self.adjVertices[source]
        for adj, length in elem:
            if adj == dest:
                print(length)
                return length
        return sys.maxsize

    def computeShortestPaths(self) -> tuple:
        distanceMatrix = {i: {j: int(self.getDist(i, j)) for j in self.adjVertices.keys()} for i in self.adjVertices.keys()}
        shortesPathMatrix = {i: {j: 0 for j in self.adjVertices.keys()} for i in self.adjVertices.keys()}

        for k in self.adjVertices.keys():
            for i in self.adjVertices.keys():
                for j in self.adjVertices.keys():
                    if i==j:
                        continue
                    elif distanceMatrix[i][j] > (distanceMatrix[i][k] + distanceMatrix[k][j]):
                         distanceMatrix[i][j] = (distanceMatrix[i][k] + distanceMatrix[k][j])
                         shortesPathMatrix[i][j] = k
        f = open("myfile.txt", "w")
        f.write(str(distanceMatrix))
        return (distanceMatrix, shortesPathMatrix)

    def reconstructShortestPath(self, source, dest, shortesPathMatrix) -> list:
        resultPath = [dest]
        while shortesPathMatrix[source][dest] != 0:
            resultPath.insert(0, shortesPathMatrix[source][dest])
            dest = shortesPathMatrix[source][dest]
        resultPath.insert(0, source)
        return resultPath

    def addAdditionalPaths(self, imbalancedNodes, shortesPaths):
        negativeDeltaNodes, pozitivDeltaNodes = imbalancedNodes
        distanceMatrix, shortesPathMatrix = shortesPaths
        matrix = [[0 for j in range(len(pozitivDeltaNodes))] for i in range(len(negativeDeltaNodes))]
        for i in range(len(negativeDeltaNodes)):
            for j in range(len(pozitivDeltaNodes)):
                matrix[i][j] = distanceMatrix[negativeDeltaNodes[i]][pozitivDeltaNodes[j]]

        m = Munkres()
        indexes = m.compute(matrix)
        for row, column in indexes:
            value = matrix[row][column]
            print(f'\n({row}, {column}) -> {value}')
            print(f'{negativeDeltaNodes[row]}, {pozitivDeltaNodes[column]}')
            path = self.reconstructShortestPath(negativeDeltaNodes[row], pozitivDeltaNodes[column], shortesPathMatrix)
            print(path)
            for i in range(len(path) - 1):
                print("before:", self.adjVertices[path[i]])
                self.adjVertices[path[i]].append((path[i + 1], distanceMatrix[path[i]][path[i + 1]]))
                print("after:", self.adjVertices[path[i]])
            #     if value != sum(path_elem) - test

    def computeRoutingPath(self):
        tour = []
        stack = [self.startNodeId, None]
        backtrack = False
        while len(stack) > 1:
            if not backtrack:
                stack.insert(0, self.popEdge(stack[0], stack[1]))
                print("stack:", stack)
                if stack[0] == stack[len(stack) - 2]:
                    if len(tour) > 0:
                        cyclePoint = tour.index(stack[0]) + 1
                        tour = tour[0:cyclePoint] + stack[:-1] + tour[cyclePoint + len(stack) - 2:]
                    else:
                        tour = stack[:-1]
                    backtrack = True
            else:
                stack.pop(0)
                if stack[0] is not None and len(self.adjVertices[stack[0]]) > 0:
                    backtrack = False
                    stack = [stack[0], None]
        return tour

    def run(self):
        print("\n\ncount:", len(self.adjVertices))
        connect = self.checkStronglyConnected()
        if connect:
            self.addAdditionalPaths(self.checkImbalancedNodes(), self.computeShortestPaths())
            print(self.checkStronglyConnected())
            self.checkImbalancedNodes()
            print("\ntour\n",self.computeRoutingPath())

class BalanceModelDataOSMFactory:

    def __init__(self, G, modelDataOSMPartitions, modelDataOSMGraph, roundabouts):
        self.G = G
        self.modelDataOSMPartitions = modelDataOSMPartitions
        self.modelDataOSMGraph = modelDataOSMGraph
        self.roundabouts = roundabouts

    def __str__(self):
        for model in self.balanceClustersModel:
            print(model.__str__())

    def get_roundabout_node(self, model):
        for vertex_id, roundabout in model.vertices.items():
            if roundabout:
                return vertex_id
        return None

    def check_end_road_vertex(self, node, model, visited):
        if len(model.adjVertices[node]) == len(self.G[node]):
            return True
        for adj_tuple in model.adjVertices[node]:
            if model.vertices[adj_tuple[0]].roundabout:
                return true
        return False

    def getNearestRoundabout(self, node, model):
        nearest_roundabout, global_length = None, sys.maxsize
        nodes = nx.nodes(self.G)
        for id in self.roundabouts:
            if id not in model.vertices.keys():
                current_length = math.sqrt((pow(nodes[id]['x'] - nodes[node]['x'], 2) + pow(
                    nodes[id]['y'] - nodes[node]['y'], 2)))
                if current_length < global_length : nearest_roundabout = id
        return nearest_roundabout

    def completePartitionTwowayStreet(self, node, current_osm_model):
        neighbours = nx.all_neighbors(self.G, node)
        current_node = next ((x for x in neighbours if x not in current_osm_model.vertices.keys()), None)
        if current_node:
            nearest_roundabout = model.getNearestRoundabout(current_node, model)
            arrival_path = nx.bidirectional_dijkstra(self.G, current_node, nearest_roundabout, weight='length')
            departure_path = nx.bidirectional_dijkstra(self.G, nearest_roundabout, current_node, weight='length')
            for path_type in [arrival_path, departure_path]:
                for i in range(len(path_type) - 1):
                    length = self.G[path_type[i]][path_type[i+1]][0]['length']
                    current_osm_model.adjVertices[path_type[i]].append((path_type[i+1], length))
                    current_osm_model.vertices[path_type[i]] = self.modelDataOSMGraph.vertices[path_type[i]]
        else:
            print("impossible")

    def completePartitionOnewayStreet(self, nodes, osm_model):
        for node in nodes:
            nearest_roundabout = osm_model.getNearestRoundabout(node, osm_model)
            departure_path = nx.bidirectional_dijkstra(self.G, nearest_roundabout, node, weight='length')
            for i in range(len(departure_path) - 1):
                length = self.G[departure_path[i]][departure_path[i + 1]][0]['length']
                osm_model.adjVertices[departure_path[i]].append((departure_path[i + 1], length))
                osm_model.vertices[path_type[i]] = self.modelDataOSMGraph.vertices[path_type[i]]

    def solveIncompletPaths(self, nodes, current_osm_model):
        one_ways_streets = []
        for node in nodes:
            if not self.G[node[0]][node[1]][0]['oneway']:
                self.completePartitionTwowayStreet(node[1], current_osm_model)
            else:
                one_ways_streets.append(node)
        self.completePartitionOnewayStreet(one_ways_streets, current_osm_model)

    def balanceAllModels(self):
        for model in self.modelDataOSMPartitions:
            visited = {x: False for x in model.vertices}
            start_node = get_roundabout_node(model)
            stack = [start_node, None]
            backtrack = False
            incomplete_path_nodes = []
            while len(stack) > 1:
                if not backtrack:
                    visited[stack[0]] = True
                    next_vertex = model.getNextVertex(stack[0], visited)
                    if next_vertex:                                               # has neighbour
                        stack.insert(0, next_vertex)
                        print("stack:", stack)
                    elif self.check_end_road_vertex(stack[0], model, visited):    # end of road or road cicle
                        backtrack = True
                    else:                                                         # incomplete path
                        incomplete_path_nodes.append((stack[1], stack[0]))
                        backtrack = True
                else:
                    stack.pop(0)
                    new_way = next(
                        (True for item in model.adj[stack[0]] if not visited[item]),
                        False
                    )
                    if stack[0] is not None and new_way:
                        backtrack = False
            self.solveIncompletPaths(incomplete_path_nodes, model)
            for el, state in visited.items():
                if not state:
                    del model.vertices[el]
                    del model.adjVertices[el]

            

if __name__ == "__main__":
    print("ffff")
