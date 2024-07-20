import os
import random
import xml.etree.ElementTree as ET
from sumo_experiments.components import FlowBuilder, DetectorBuilder
import networkx as nx


class LilleNetwork:
    """
    Create the SUMO network and flows for the city of Lille.
    """

    THIS_FILE_PATH = os.path.abspath(os.path.dirname(__file__))

    NB_ROUTES_EACH_FLOW = 100

    FLOWS_ENTRIES = {
        'TOURQUENNOIS_LILLE': 12600,
        'ROUBAISIEN_LILLE': 23100,
        'EST_LILLE': 32400,
        'SUD_LILLE': 32400,
        'WEPPES_LILLE': 13300,
        'NORD_LILLE': 45600,
        'LYS_LILLE': 9100
    }

    FLOWS_EXITS = {
        'LILLE_TOURQUENNOIS': 13300,
        'LILLE_ROUBAISIEN': 22400,
        'LILLE_EST': 33600,
        'LILLE_SUD': 31800,
        'LILLE_WEPPES': 13300,
        'LILLE_NORD': 44400,
        'LILLE_LYS': 8400,
    }

    PROPORTIONS_TO_TIME = [
        0.3, 0.1, 0.1, 0.1, 0.2, 0.4, 1.2, 6.4, 10.2, 4.3, 5, 6.5, 7.5, 7.6, 5, 6.7, 10, 9.5, 7.7, 5, 3, 1.5, 1, 0.7
    ]

    ENTRIES_EACH_FLOW = {
        'TOURQUENNOIS_LILLE': {'114800016#1': 0.2, '691053721-AddedOffRampEdge': 0.8},
        'ROUBAISIEN_LILLE': {'114800016#1': 0.2, '691053721-AddedOffRampEdge': 0.8},
        'EST_LILLE': {'674454570': 0.05, '32391880': 0.95},
        'SUD_LILLE': {'986419403#3': 0.1, '670522617#0': 0.45, '669441008#0': 0.45},
        'WEPPES_LILLE': {'842421984': 0.95, '986419403#3': 0.05},
        'NORD_LILLE': {'114800016#1': 0.1, '1252597600#0': 0.3, '95426996#0': 0.2, '220886686': 0.4},
        'LYS_LILLE': {'180818488#0': 0.25, '1184172235': 0.25, '220886686': 0.4, '95426996#0': 0.1}
    }

    EXITS_EACH_FLOW = {
        'LILLE_TOURQUENNOIS': {'181634862': 0.2, '326114344': 0.8},
        'LILLE_ROUBAISIEN': {'181634862': 0.2, '326114344': 0.8},
        'LILLE_EST': {'151484632': 0.05, '30834157': 0.95},
        'LILLE_SUD': {'149408034#0': 0.1, '670522615#0': 0.45, '23298866#0': 0.45},
        'LILLE_WEPPES': {'237476482': 0.95, '149408034#0': 0.05},
        'LILLE_NORD': {'181634862': 0.1, '1137309858#0': 0.3, '19906584#3': 0.2, '177547335': 0.4},
        'LILLE_LYS': {'-39437728': 0.25, '1102613333#0': 0.25, '177547335': 0.4, '19906584#3': 0.1},
    }

    def __init__(self):
        """
        Init of class
        """
        self.NET_FILE = os.path.join(self.THIS_FILE_PATH, 'lille/lille.net.xml')
        self.ENTRIES_FILE = os.path.join(self.THIS_FILE_PATH, 'lille/liste_entrees.txt')
        self.EXITS_FILE = os.path.join(self.THIS_FILE_PATH, 'lille/liste_sorties.txt')
        self.FORBID_EXITS_FILE = os.path.join(self.THIS_FILE_PATH, 'lille/exit_forbidden.txt')
        self.TL_JUNCTIONS = self.get_tl_junctions()
        self.EDGES_TO_TL = self.get_edges_to_tl()
        self.EDGES_FROM_TL = self.get_edges_from_tl()
        self.GRAPH = self.net_to_graph()
        self.flows = FlowBuilder()
        self.flows.add_v_type(id='car0')

    def generate_flows(self, intensity=1):
        """
        Generate flows for the network.
        :param intensity: The intensity of the normal flow. A coefficient to multiply the number of vehicle for each flow.
        :type intensity: float
        :return: The flows
        :rtype: FlowBuilder
        """
        forbid_exits = self.get_forbidden_exits()
        tree = ET.parse(self.NET_FILE)
        edges = [e.get('id') for e in tree.iter('edge')]
        hours = [3600 * i for i in range(25)]
        cpt = 0
        for time in range(len(self.PROPORTIONS_TO_TIME)):
            # From outside to Lille
            for flow in self.FLOWS_ENTRIES:
                for entry in self.ENTRIES_EACH_FLOW[flow]:
                    c = 0
                    while c < self.NB_ROUTES_EACH_FLOW:
                        exit = random.choices(edges)[0]
                        if exit[0] != ':' and nx.has_path(self.GRAPH, entry, exit) and exit not in forbid_exits:
                            freq = int((self.FLOWS_ENTRIES[flow] * self.PROPORTIONS_TO_TIME[time] * self.ENTRIES_EACH_FLOW[flow][entry]) // self.NB_ROUTES_EACH_FLOW)
                            freq *= intensity
                            if freq == 0:
                                freq = 1
                            self.flows.add_flow(id=f"{cpt}",
                                                begin=hours[time],
                                                end=hours[time+1],
                                                from_edge=entry,
                                                to_edge=exit,
                                                frequency=freq,
                                                v_type='car0',
                                                distribution='binomial')
                            c += 1
                            cpt += 1
            # From Lille to outside
            for flow in self.FLOWS_EXITS:
                for exit in self.EXITS_EACH_FLOW[flow]:
                    c = 0
                    while c < self.NB_ROUTES_EACH_FLOW:
                        entry = random.choices(edges)[0]
                        if entry[0] != ':' and nx.has_path(self.GRAPH, entry, exit):
                            freq = int((self.FLOWS_EXITS[flow] * self.PROPORTIONS_TO_TIME[time] * self.EXITS_EACH_FLOW[flow][exit]) // self.NB_ROUTES_EACH_FLOW)
                            freq *= intensity
                            if freq == 0:
                                freq = 1
                            self.flows.add_flow(id=f"{cpt}",
                                                begin=hours[time],
                                                end=hours[time+1],
                                                from_edge=entry,
                                                to_edge=exit,
                                                frequency=freq,
                                                v_type='car0',
                                                distribution='binomial')
                            c += 1
                            cpt += 1
        return self.flows







    def generate_flows_from_outside(self):
        """
        Generate flows for the network.
        :return: The flows
        :rtype: FlowBuilder
        """
        entries = self.get_entries()
        exits = self.get_exits()
        for entry in entries:
            for exit in exits:
                if entry != exit:
                    self.flows.add_flow(id=f"{entry.get('id')}-{exit.get('id')}",
                                   end=3600,
                                   from_edge=entry.get('id'),
                                   to_edge=exit.get('id'),
                                   frequency=50,
                                   v_type='car0',
                                   distribution='binomial')
        return self.flows

    def generate_flows_intra_city(self, n):
        """
        Generate flows that start and end inside the city, and not from entry to exit.
        :param n: The number of flows to create
        :type n: int
        :return: The flows
        :rtype: FlowBuilder
        """
        tree = ET.parse(self.NET_FILE)
        edges = [e.get('id') for e in tree.iter('edge')]
        c = 0
        forbid_exits = self.get_forbidden_exits()
        while c < n:
            couple = random.choices(edges, k=2)
            if nx.has_path(self.GRAPH, couple[0], couple[1]) and couple[0][0] != ':' and couple[1][0] != ':' and couple[1] not in forbid_exits:
                self.flows.add_flow(id=f"{couple[0]}-{couple[1]}",
                                    end=3600,
                                    from_edge=couple[0],
                                    to_edge=couple[1],
                                    frequency=1,
                                    v_type='car0',
                                    distribution='binomial')
                c += 1
        return self.flows


    def get_tl_junctions(self):
        """
        Get all junctions managed by a traffic light.
        :return: The list of all junctions managed by a traffic light
        :rtype: list
        """
        tree = ET.parse(self.NET_FILE)
        junctions = tree.iter('junction')
        traffic_lights = []
        for junction in junctions:
            if junction.get('type') == 'traffic_light':
                traffic_lights.append(junction)
        return traffic_lights

    def get_edges_to_tl(self):
        """
        Get all edges ending in a traffic light.
        :return: The edges ending into each traffic light node
        :rtype: dict
        """
        tree = ET.parse(self.NET_FILE)
        edges = tree.iter('edge')
        tl_to_edges = {}
        for junction in self.TL_JUNCTIONS:
            tl_to_edges[junction.get('id')] = []
        for edge in edges:
            if edge.get('to') in tl_to_edges:
                tl_to_edges[edge.get('to')].append(edge)
        return tl_to_edges

    def get_edges_from_tl(self):
        """
        Get all edges starting from a traffic light.
        :return: The edges strating from each traffic light node
        :rtype: dict
        """
        tree = ET.parse(self.NET_FILE)
        edges = tree.iter('edge')
        tl_to_edges = {}
        for junction in self.TL_JUNCTIONS:
            tl_to_edges[junction.get('id')] = []
        for edge in edges:
            if edge.get('from') in tl_to_edges:
                tl_to_edges[edge.get('from')].append(edge)
        return tl_to_edges


    def get_entries(self):
        """
        Return the list of all the id of the entry edges of the network.
        :return: The list of all the entries of the network.
        :rtype: list
        """
        nodes_id = []
        with open(self.ENTRIES_FILE, 'r') as f:
            id = f.readline()[:-1]
            while id != "":
                nodes_id.append(id)
                id = f.readline()[:-1]
        tree = ET.parse(self.NET_FILE)
        edges = tree.iter('edge')
        entries_id = []
        for edge in edges:
            if edge.get('from') in nodes_id:
                entries_id.append(edge)
        return entries_id

    def get_exits(self):
        """
        Return the list of all the id of the exit edges of the network.
        :return: The list of all the exits of the network.
        :rtype: list
        """
        nodes_id = []
        with open(self.EXITS_FILE, 'r') as f:
            id = f.readline()[:-1]
            while id != "":
                nodes_id.append(id)
                id = f.readline()[:-1]
        tree = ET.parse(self.NET_FILE)
        edges = tree.iter('edge')
        exits_id = []
        for edge in edges:
            if edge.get('to') in nodes_id:
                exits_id.append(edge)
        return exits_id

    def get_forbidden_exits(self):
        """
        Return the list of all the id of the forbidden exits edges of the network.
        :return: The list of all the forbidden exits of the network.
        :rtype: list
        """
        edges_id = []
        with open(self.FORBID_EXITS_FILE, 'r') as f:
            id = f.readline()[:-1]
            while id != "":
                edges_id.append(id)
                id = f.readline()[:-1]
        return edges_id

    def net_to_graph(self):
        """
        Convert the network in xml format to a graph where edges are the nodes, and connections are the links.
        :return: The graph representation of the network
        :rtype: networkx.Graph
        """
        G = nx.DiGraph()
        tree = ET.parse(self.NET_FILE)
        edges = tree.iter('edge')
        for edge in edges:
            G.add_node(edge.get('id'))
        connections = tree.iter('connection')
        for connection in connections:
            G.add_edge(connection.get('from'), connection.get('to'))
        return G







if __name__ == '__main__':
    lille = LilleNetwork()
    print(lille.generate_flows_intra_city(100))


