
from .DBConnector import DBConnector
from .Error import *
import datetime
import re

class BasicElement(DBConnector):

    # V2
    def __init__(self, id = None, data = None, multi = False, conf = {}, db_name = None):
        if db_name != None:   
            self.db_name = db_name        
        super().__init__(conf=conf)
        self.make()
        if multi == True:
            self.values = []
            # Option to send data to multi objects
            if type(data) == list:
                for element in data:
                    for key in data:
                        if key not in self.attributes:
                            element.pop(key)
                    self.values.append(element)
        elif data != None:    
            for key in self.attributes:
                setattr(self, key, data[key] if key in data else None)
        elif id != None:
            self.id = id

    @classmethod
    def search_attributes(cls):
        return []

    def get_all(self):
        query_list = [{'dim':att, 'op':'==', 'val':self.get(att)}  for att in self.get('attributes') if self.get(att) != None]
        self.search(query_list=query_list)

      # V2
    @property
    def id(self):
        return getattr(self, '_id', self.get('_key', None))

    @id.setter
    def id(self, value):
        self._id = value
            
      # V2
    @property
    def multi(self):
        return getattr(self, '_multi', False)

    @id.setter
    def multi(self, value):
        self._multi = value
            
    def auth(self):
        return False

    # V2 still unsure
    def duplicate(self):
        return self.__init__(data = self.to_dict(), multi=self.multi, db_name=self.db_name, id=self.id)

    # V2
    def insert_many(self, data=None):
        self.date_created= datetime.datetime.utcnow().isoformat()
        self.date_updated = self.date_created
        self.deleted = self.get('deleted', False)
        if self.deleted == None:
            self.deleted = False
        if self.multi == False and data==None:
            raise MissingRequiredParamatersException
        elif data != None:
            values = data
        elif self.multi == True:
            values = self.values
        else:
            raise MissingRequiredParamatersException
        for val in values:
            val['date_created'] = self.date_created
            val['date_updated'] = self.date_updated
            val['deleted'] = self.deleted
            for key in self.attributes:
                if key in val and val[key] == None:
                    val.pop(key)
            val = self.build_edges(val)
        res = super().insert_many(values)
        for i,val in enumerate(values):
            val['_key'] = res[i]
        if self.multi == True:
            self.values = values
        return len(values)        
    
    # V2
    def wipeByFilter(self, query_list=[]):
        deleted = self.delete_many(query_list=query_list)
        return deleted

    def get_alias(self):
        return self.get('_key')

    # V2
    def wipe(self):
        self.delete_one(self.id)
        self.id = None
        self.__init__(data={})

    # V2
    def delete(self):
        self.deleted = True
        self.active = False
        self.status = self.update()
    
    # V2
    def load_multikey(self, keys:list, get_if_deleted=False):
        found = False
        i=0
        while not found and i < len(keys):
            query_list = [{
                'op': '==',
                'dim': keys[i],
                'val': self.get(keys[i])
            }]
            records = self.search(query_list=query_list, limit=1, rawResults=True)
            if len(records) > 0:
                record = records[0]
                found = True
                if record.get('deleted') == True and get_if_deleted==False:
                    raise ObjectNotFoundException
                self.set(record.get('_key', None), record)
        if not found:
            raise ObjectNotFoundException

    # V2
    def search(self, query_list=[], limit=None, sort_list=[], unique=False, avoid_deleted=True, vowel_regex=False):
        if vowel_regex == True:
            for q in query_list:
                if isinstance(q.get('val', None), str):
                    if q.get("op", None) == '=~':
                        q['val'] = self.regex_vowel_spelling(q['val'])
        found = super().search(query_list=query_list, limit=limit, sort_list=sort_list, unique=unique)
        if avoid_deleted == True:
            found = list(filter(lambda x: not 'deleted' in x or x['deleted'] != True, found))
        self.found = []
        tmp_keys = []
        for record in found:
            data = record.getStore()
            data.pop('password', None)
            if unique != True or data['_key'] not in tmp_keys:
                obj = self.__class__(data=data)
                obj.id=data['_key']
                tmp_keys.append(obj.id)
                obj.set_edges()
                self.found.append(obj)

    # Makes Sense V2        
    def get(self, att, default=None):
        res = getattr(self, att, default)
        if res == None:
            return default
        return res
    
    # Deprecate, should use __class__.__name__
    # Maintain for V2
    def get_class(self):
        return self.__class__.__name__

    # V2
    def get_distinct_elements(self, dims=['_key']):
        elements = self.search(dims_list=dims, unique=True)
        for i, record in enumerate(elements):
            data = record.getStore()
            data.pop('password', None)
            obj =  self.__class__(data=data)
            obj.id=data.get('_key', f'query_res_{i}')
            obj.set_edges()
            self.delements.append(obj)

    # Makes Sense V2
    def to_dict(self):
        res = {}
        for key in self.attributes:
            res[key] = self.get(key)
        return res

    # V2
    def update(self, id=None, data=None):
        if id != None:
            self.id = id
        if data != None:
            self.set(self.id, data)
        self.date_updated = datetime.datetime.utcnow().isoformat()
        to_update = self.to_dict()
        to_update.pop('date_created', None)
        to_update.pop('user_created', None)
        for key in self.attributes:
            if key in to_update and (to_update[key] == None or re.search(r'^(obj_){1}\w+$', key) != None or re.search(r'^(alias_){1}\w+$', key) != None):
                to_update.pop(key)
        to_update = self.build_edges(to_update)
        result = self.update_one(self.id, to_update)
        if result == True:
            self.set(self.id, to_update)

    # Makes sense V2
    def make(self):
        self.attributes = ['_key']
        for key in self.attributes:
            setattr(self, key, None)
    
    # V2
    def set(self, id, data):
        if type(data) == dict:
            self.set_from_dict(data)
        self.set_edges()
        self.id = id

    # V2
    def load(self, id=None, get_if_deleted=False):
        if id != None:
            self.id = id
        self._load(get_if_deleted=get_if_deleted)

    # V2
    def _load(self, get_if_deleted=False):
        record = self.get_one(self.id)
        if record.get('deleted', False) == True and get_if_deleted==False:
            raise ObjectNotFoundException
        self.set(self.id, record)

    # V2
    def set_edges(self, data=None):
        if self.is_edge == True:
            if data != None:
                self._to = data.get('_to', self._to)
                self._from = data.get('_from', self._from)
            if len(self.get('_to', '').split("/")) > 1:
                self._to = self.get('_to').split("/")[1]
            if len(self.get('_from', '').split("/")) > 1:
                self._from = self.get('_from').split("/")[1]

    # V2
    def build_edges(self, base_obj):
        if self.is_edge == True:
            from_to = self.vertex
            if self.get('_to', None) != None and base_obj.get('_to', '').find(f'{from_to.get("_to", "Collection")}/') != 0:
                base_obj['_to'] = f'{from_to["_to"]}/{self.get("_to")}'
            if self.get('_from', None) != None and base_obj.get('_from', '').find(f'{from_to.get("_from", "Collection")}/') != 0:
                base_obj['_from'] = f'{from_to["_from"]}/{self.get("_from")}'
        return base_obj


    # V2
    def set_from_dict(self, data):
        for key in self.attributes:
            setattr(self, key, data[key] if key in data else self.get(key))


    # V2
    def insert(self, id=None, data=None):
        if id != None:
            self.id = id
        if data != None:
            self.set(self.id, data)
        # try:
        self.date_created= datetime.datetime.utcnow().isoformat()
        self.date_updated = self.date_created
        self.deleted = self.get('deleted', False)
        if self.deleted == None:
            self.deleted = False
        to_insert = self.to_dict()
        for key in self.attributes:
            if key in to_insert and to_insert[key] == None:
                to_insert.pop(key)
        to_insert = self.build_edges(to_insert)
        self.id = self.insert_one(to_insert, id=self.id)
        return self.id