import sys
from munkres import Munkres
import numpy
import networkx as nx
from abc import ABC, abstractmethod
import ModelDataOSM

class ConfigRoutingMode(ABC):

    @abstractmethod
    def config(self, G, config_mode, roundaboutDict, roundaboutNodes):
        pass

    def mapToModelMultiDiGraph(self, G, roundaboutDict, roundaboutNodes, modelDataOSM = ModelDataOSM()):
        st = 0
        xt = 0
        for edge in numpy.copy(G.edges):
            xt += 1
            x, y, z = edge
            if 'junction' in G[x][y][0]:
                continue
            n1 = False
            n2 = False
            lanes = ''
            if 'name' not in G[x][y][0]:
                print("\n\nno-name\n\n")
                G[x][y][0]['lanes'] = 2
            if 'lanes' in G[x][y][0]:
                if type(G[x][y][0]['lanes']) == list:
                    lanes = checkLanes(G, G[x][y][0]['name'], G[x][y][0]['oneway'])
                else:
                    lanes = G[x][y][0]['lanes']
            else:
                lanes = checkLanes(G, G[x][y][0]['name'], G[x][y][0]['oneway'])
            if x in roundaboutNodes:
                n1 = True
                roundaboutNode = [k for k, v in roundaboutDict.items() if x in v][0]
                modelDataOSM.addOnewayEdge(roundaboutNode, True, x, False, '1', '10')
                modelDataOSM.addOnewayEdge(x, False, y, False, lanes, G[x][y][0]['length'])
            if y in roundaboutNodes:
                n2 = True
                roundaboutNode, roundaboutSet = [(k, v) for k, v in roundaboutDict.items() if y in v][0]
                modelDataOSM.addOnewayEdge(y, False, roundaboutNode, True, '1', '10')
                modelDataOSM.addOnewayEdge(x, False, y, False, lanes, G[x][y][0]['length'])
            if n1 or n2:
                continue
            else:
                if G[x][y][0]['oneway']:
                    modelDataOSM.addOnewayEdge(x, False, y, False, lanes, G[x][y][0]['length'])
                else:
                    st = y
                    modelDataOSM.addEdge(x, False, y, False, lanes, G[x][y][0]['length'])
                    print("x->", x, "  y->", y)
        print("xxxxx------->", xt)
        modelDataOSM.initStartNode(st)
        return modelDataOSM

    def getCoords(G, roundaboutSet):
        x = y = 0
        nodes = nx.nodes(G)
        for node in roundaboutSet:
            x += nodes[node]["x"]
            y += nodes[node]["y"]
        return (x / len(roundaboutSet), y / len(roundaboutSet))

    def addRoundabouts(G, oldG, roundaboutNodes, roundaboutDict):
        for edge in numpy.copy(G.edges):
            x, y, z = edge
            if x in roundaboutNodes:
                roundaboutNode, roundaboutSet = [(k, v) for k, v in roundaboutDict.items() if x in v][0]
                coords_x, coords_y = getCoords(oldG, roundaboutSet)
                G.add_node(roundaboutNode, x=coords_x, y=coords_y)
                G.add_edge(roundaboutNode, x, length=10)
            if y in roundaboutNodes:
                roundaboutNode, roundaboutSet = [(k, v) for k, v in roundaboutDict.items() if y in v][0]
                coords_x, coords_y = getCoords(oldG, roundaboutSet)
                G.add_node(roundaboutNode, x=coords_x, y=coords_y)
                G.add_edge(y, roundaboutNode, length=10)

    def checkLanes(G, name, oneway):
        for edge in numpy.copy(G.edges):
            x, y, z = edge
            if 'name' in G[x][y][0]:
                if G[x][y][0]['name'] == name:
                    if 'lanes' in G[x][y][0]:
                        return G[x][y][0]['lanes']
        if 'oneway' in G[x][y][0]:
            if G[x][y][0]['oneway'] == 'True':
                return '2';
            else:
                return '1';


class PrimaryStreetsConfigMode(ConfigRoutingMode):
    def config(self, G, roundaboutDict, roundaboutNodes):
        for edge in numpy.copy(G.edges):
            x, y, z = edge
            if G[x][y][0]["highway"] != "primary" or 'junction' in G[x][y][0]:
                G.remove_edge(x, y)
        G.remove_nodes_from(list(nx.isolates(G)))
        return mapToModelMultiDiGraph(G, roundaboutDict, roundaboutNodes)

class PrimarySecondaryStreetsConfigMode(ConfigRoutingMode):
    def config(self, G, config_mode, roundaboutDict, roundaboutNodes):
        oldG = G.copy()
        for edge in numpy.copy(G.edges):
            x, y, z = edge
            if G[x][y][0]["highway"] != "primary" and G[x][y][0]["highway"] != "secondary" and G[x][y][0][
                "highway"] != "primary_link" and G[x][y][0]["highway"] != "secondary_link" or 'junction' in G[x][y][0]:
                G.remove_edge(x, y)
        G.remove_nodes_from(list(nx.isolates(G)))
        addRoundabouts(G, oldG, roundaboutNodes, roundaboutDict)
        ox.plot_graph(G)
        clusters = clustering_kmeans_approach(G, 4, 10)
        models = []
        return;
        for centroid, partition in clusters.items():
            graph = getPartitionGraph(G.copy(), partition)
            models.append(mapToModelMultiDiGraph(graph, roundaboutDict, roundaboutNodes))
        return
        modelDataOSMGraph = mapToModelMultiDiGraph(G.copy(), roundaboutDict, roundaboutNodes)
        balanceModelDataOSMFactory = ModelDataOSM.BalanceModelDataOSMFactory(G, models, modelDataOSMGraph,
                                                                             roundaboutDict.keys())
