from pyArango.connection import *
from pyArango.theExceptions import *
from .Error import *
import os
import json
import re

class DBConnector():


    def __init__(self, db_name=None, conf=None, create_if_not_exists=False, verbose=False):
        if type(conf) == dict:
            arangoURL= conf.get(f'DBURL', json.loads(os.environ.get(f'DBURL', None)))
            username=conf.get(f'DBUSERNAME', os.environ.get(f'DBUSERNAME',  None))
            password=conf.get(f'DBPASSWORD', os.environ.get(f'DBPASSWORD', None))
        else:
            arangoURL=json.loads(os.environ.get(f'DBURL', None))
            username=os.environ.get(f'DBUSERNAME', None)
            password=os.environ.get(f'DBPASSWORD', None)
        if arangoURL == None or username == None or password == None:
            raise MissingConfigurationException
        if db_name != None:
            self.db_name=db_name

        # Create connection with loaded config
        db_client = Connection(arangoURL=arangoURL, username=username, password=password, verify=True, verbose=verbose, statsdClient=None, reportFileName=None, loadBalancing='round-robin', use_grequests=False, use_jwt_authentication=False, use_lock_for_reseting_jwt=True, max_retries=10)
        
        if not db_client.hasDatabase(self.db_name):
            if create_if_not_exists==True:
                self.db = db_client.createDatabase(self.db_name)
            else:
                raise DBNotExists
        else:
            self.db = db_client[self.db_name]
            
    @property
    def collection(self):
        return self._collection
    
    def get_collection_name(self):
        return getattr(self, '_collection_name', '')

    @collection.setter
    def collection(self, value):
        self._collection_name = value
        self._collection = self.db[self._collection_name]
            
    @property
    def db_name(self):
        return getattr(self, '_db_name', '')

    @db_name.setter
    def db_name(self, value):
        self._db_name = value
            
    @property
    def is_edge(self):
        return getattr(self, '_is_edge', False)

    @is_edge.setter
    def is_edge(self, value):
        self._is_edge = value
            
    @property
    def vertex(self):
        return getattr(self, '_vertex', {})

    @vertex.setter
    def vertex(self, value):
        if '_from' in value and '_to' in value:
            self._vertex = value
            self.is_edge = True
        else:
            self._vertex = {}
            self.is_edge = False
            

    @classmethod
    def build_filter_string_from_dict(cls, filters:dict) -> str:
        attribute_list = [{'val':filters[att] , 'dim': att, 'op':'=='} for att in filters if filters[att] != None ]
        return cls.build_filter_string_from_list(attribute_list)
            

    @classmethod
    def build_filter_list_from_dict(cls, filters:dict) -> str:
        attribute_list = [{'val':filters[att] , 'dim': att, 'op':'=='} for att in filters if filters[att] != None ]
        return attribute_list

    
    @classmethod
    def build_filter_string_from_list(cls, filters:list) -> str:
        filters_list = []
        for att in filters:
            if 'val' in att and 'dim' in att:
                if isinstance(att.get('val', None), str):
                    if att.get("op", '==') == '=~':
                        filters_list.append(f'Regex_Test(m.`{att["dim"]}`,"{att["val"]}", true)')
                    else:
                        filters_list.append(f'm.`{att["dim"]}` {att["op"]} "{att["val"]}"')
                else:
                    filters_list.append(f'm.`{att["dim"]}` {att["op"]} {att["val"]}')
        filters_string = ' && '.join(filters_list)
        return filters_string
    
    @classmethod
    def build_sort_string_from_list(cls, sorting:list) -> str:
        sort_list = []
        for att in sorting:
            if 'dim' in att:
                if att.get("op", 'asc').lower() == 'asc':
                    sort_list.append(f"m.`{att.get('dim')}`")
                else:
                    sort_list.append(f"m.`{att.get('dim')}` DESC")
        filters_string = ', '.join(sort_list)
        return filters_string
    
    @classmethod
    def regex_vowel_spelling(cls, in_string:str, line_end=True) -> str:
        re_string = re.sub("[àáâãäå]", 'a', in_string)
        re_string = re.sub("[èéêë]", 'e', re_string)
        re_string = re.sub("[ìíîï]", 'i', re_string)
        re_string = re.sub("[òóôõö]", 'o', re_string)
        re_string = re.sub("[ùúûü]", 'u', re_string)
        re_string = re.sub("[ýÿ]", 'y', re_string)
        if line_end == True:
            re_string = re_string + '$'
        return re_string


    def get_one(self, id, rawResults = True):
        try:
            found = self.collection.fetchDocument(id, rawResults = rawResults)
        except DocumentNotFoundError as e:
            raise ObjectNotFoundException(message=f"Object with id {id} not found in collection {self.get_collection_name()}")
        return found

    def update_one(self, id, data):
        # Document Object from PyArango
        document = self.get_one(id, rawResults = False)
        before_rev = document['_rev']
        data.pop('_key', None)
        data.pop('_id', None)
        data.pop('_rev', None)
        document.set(data)
        document.save()
        after_rev = document['_rev']
        return before_rev != after_rev

    def insert_one(self, data, id=None):
        data.pop('_key', '')
        if id != None:
            data['_key'] = id
        data.pop('_id', '')
        data.pop('_rev', '')
        document = self.collection.createDocument(data)
        document.save()
        self._key = document._key
        return document._key

    def insert_many(self, data_list):
        aql = f'for nd IN {json.dumps(data_list)} \
            INSERT nd into {self.get_collection_name()} \
            LET inserted = NEW \
            RETURN inserted._key'
        res = self.db.AQLQuery(aql, rawResults=True, batchSize=100000)
        return res

    
    def delete_one(self, id):
        del_obj = self.get_one(id, False)
        del_obj.delete()
        return True
    
    def delete_many(self, query_list=[]):
        '''
            Queries the collection defined and removes all matches.

            @query_list: list of dictionaries, each with dim, op and val keys
        '''
        qf = self.build_filter_string_from_list(query_list)
        if qf != '':
            qf = ' FILTER '+qf
        query = 'for m in '+ self.get_collection_name() +'\
                '+qf + ' REMOVE m in '+ self.get_collection_name()
        deleted = self.db.AQLQuery(query)
        return deleted

    def search(self, query_list=[], limit=None, sort_list=[], dims_list=[], unique=False, rawResults=False):
        '''
            Queries the collection defined.

            @query_list: list of dictionaries, each with dim, op and val keys
            @limit: limit the number of hits
            @sort: list of dictoinaries, each with dim and dir keys
            @unique: if true returns unique results
        '''
        qf = self.build_filter_string_from_list(query_list)
        qs = self.build_sort_string_from_list(sort_list)

        if qf != '':
            qf = ' FILTER '+qf

        if qs != '':
            qf = qf + ' SORT '+ qs

        if limit != None:
            qf = qf + ' limit ' + str(limit)

        ds = 'm'
        if len(dims_list) > 0:
            ds = '{' + ', '.join([f'{dim}' for dim in dims_list]) + '}'
            cd = ', '.join([f'{dim} = m.{dim}' for dim in dims_list])

            query = 'for m in '+ self.get_collection_name() + ' ' + qf + ' return ' +\
                    ('COLLECT ' + cd + 'DISTINCT ' if unique == True else '') +\
                    ds 
        else:

            query = 'for m in '+ self.get_collection_name() + ' ' + qf + ' return ' +\
                    (' DISTINCT ' if unique == True else '') +\
                    ds 

        found = self.db.AQLQuery(query, rawResults=rawResults, batchSize=1000)
        return found
