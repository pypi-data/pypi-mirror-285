import pyArango
from pyArango.connection import *
from pyArango.collection import *
from pyArango.graph import *
from .Error import *
from .DBConnector import DBConnector


class ClassFactory():

    def __init__(self, graphname, db_name, collections = [], edgeDefinitions={}, conf=None):
        '''
            Initialiazes graph and elements. If Database is not in server, creates it. If collections or edges are added, creates them. Edges with no definition are ignored

            graphname - Name of graph to use or create
            db_name - Name of database to use or create
            collections - List of collection names
            edgeDefinitions - dictionary with the structure {edgeName: { fromCollections : list, toCollections: list }}
            prefix - Added before db name
            conf - dictionary to override os.eviron, required keys: DBURL, DBUSERNAME, DBPASSWORD

            If from/toCollections contain collections not in collections list, adds them as collections

        '''
        
        self.db_connector = DBConnector(db_name, conf=conf, create_if_not_exists=True)

        # Determine all collections connected in the edgeDefinitions
        db_connected = []
        db_edges = [edge for edge in edgeDefinitions]
        for edge in edgeDefinitions:
            for colFrom in edgeDefinitions[edge]['fromCollections']:
                if colFrom not in db_connected:
                    db_connected.append(colFrom)
            for colTo in edgeDefinitions[edge]['toCollections']:
                if colTo not in db_connected:
                    db_connected.append(colTo)
        # Collections given and not connected are orphans
        db_orphans = [collection for collection in collections if collection not in db_connected]

        # All connected collections need to be created
        db_collections = collections
        db_collections.extend(db_connected)
        db_collections = list(set(db_collections))
        # Create each collection and edge class for instancing
        for cl in db_collections:
            if cl not in db_edges:
                globals()[cl] = type(cl, (Collection,), {"_fields" : {}})
        for cl in db_edges:
            globals()[cl] = type(cl, (Edges,), {"_fields" : {}})

        # Look for collections, edges and graph and reference or create
        for col in db_collections:
            if col not in db_edges:
                if not self.db_connector.db.hasCollection(col):
                    self.db_connector.db.createCollection(className='Collection', name=col)
        for col in db_edges:
            if not self.db_connector.db.hasCollection(col):
                self.db_connector.db.createCollection(className='Edges', name=col)


        # Create edgeDefinitions tuple from parameter dictionary
        db_edgeDefinitions = tuple([pyArango.graph.EdgeDefinition (edge,fromCollections = edgeDefinitions[edge]['fromCollections'],toCollections = edgeDefinitions[edge]['toCollections']) for edge in edgeDefinitions])

        # Create graph class for instancing
        if len(db_edgeDefinitions) > 0 and graphname != '':
            globals()[graphname] = type(graphname, (pyArango.graph.Graph,), {"_edgeDefinitions" : db_edgeDefinitions, "_orphanedCollections" : db_orphans })

        if not self.db_connector.db.hasGraph(graphname) and len(db_edgeDefinitions) > 0 and graphname != '':
            self.db_connector.db.createGraph(graphname)

        self.graphname = graphname
        self.collections = db_collections
        self.edges = db_edges
        self.edgeDefinitions = edgeDefinitions

    def __str__(self):
        desc = f'Graph Class for {self.db_connector.db_name}'
        return desc

    

