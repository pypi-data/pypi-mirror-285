# File: ArangoDB ORM
# Author: alexsanchezvega
# Company: d20
# Version: 2.0

from .BasicElement import BasicElement
from .support import secure_attribute_name

class Element(BasicElement):

    def dict_by_scope(self, scopes=[]):
        res = {}
        for s in scopes:
            if s in self.get('scopes'):
                for a in self.get('scopes')[s]:
                    res[a] = self.get(a)
        return res

    def make(self):
        from .Metadata import Metadata
        df = Metadata.DataField(obj_type=self.__class__.__name__.lower())
        self.data_fields = df.get('found')
        self.scopes = {}
        self.obj_attributes = []
        self.attributes = []
        for f in self.data_fields:
            if secure_attribute_name(f.get('name')):
                self.attributes.append(f.get('name'))
                if f.get('type') == 'object' and f.get('isArray') != True:
                    self.obj_attributes.append({'name':f.get('name'), 'obj_type':f.get('subtype')})
                if not f.get('scope') in self.get('scopes'):
                    self.scopes[f.get('scope')] = []
                self.scopes[f.get('scope')].append(f.get('name'))
        for key in self.attributes:
            setattr(self, key, None)
            
    def get_related_object(self, otype, okey):
        from .Metadata import Metadata
        obj = otype(id=okey)
        obj.load()
        df = Metadata.DataField(obj_type=otype.lower(), data={'active': True, 'deleted' :False, 'search_extract':True})
        df.found = list(filter(lambda x: (not 'deleted' in x or x['deleted'] != True) and ('active' in x and x['active'] == True)  and ('search_extract' in x and x['search_extract'] == True) , df.found))
        dfb = Metadata.DataField(obj_type=otype.lower(), data={'active': True, 'deleted' :False, 'scope':'basic'})
        dfb.found = list(filter(lambda x: (not 'deleted' in x or x['deleted'] != True) and ('active' in x and x['active'] == True)  and ('scope' in x and x['scope'] == 'basic') , dfb.found))
        schema = df.get('found', [])
        schema_basic = dfb.get('found', [])
        ans = [obj.to_dict(), schema, schema_basic]
        return ans

    def load(self, id, get_if_deleted=False):
        super().load(id=id, get_if_deleted=get_if_deleted)
        return
        for att in self.obj_attributes:
            otype = att['obj_type']
            att_val = self.get(att['name'])
            if '_to' == att['name']:
                otype = self.vertex.get('class_to')
                [o_to, schema, schema_basic] = self.get_related_object(otype, self._to)
                if len(schema) > 0:
                    alias = schema[0]['name']
                    if alias in o_to:
                        self.alias_to = o_to[alias]
                    else:
                        self.alias_to = ''
                    self.attributes.append('alias_to')
                    self.scopes['basic'].append('alias_to')
                    self.obj_to = {}
                    for df in schema_basic:
                        if df['name'] in o_to:
                            self.obj_to[df['name']] = o_to[df['name']] 
                    self.attributes.append('obj_to')
                    self.scopes['basic'].append('obj_to')
            elif '_from' == att['name']:
                otype = self.vertex.get('class_from')
                [o_from, schema, schema_basic] = self.get_related_object(otype, self._from)
                if len(schema) > 0:
                    alias = schema[0]['name']
                    if alias in o_from:
                        self.alias_from = o_from[alias]
                    else:
                        self.alias_from = ''
                    self.attributes.append('alias_from')
                    self.scopes['basic'].append('alias_from')
                    self.obj_from = {}
                    for df in schema_basic:
                        if df['name'] in o_from:
                            self.obj_from[df['name']] = o_from[df['name']] 
                    self.attributes.append('obj_from')
                    self.scopes['basic'].append('obj_from')
            elif self.get(att['name']) != '' and self.get(att['name']) != [] and self.get(att['name']) != None:
                [obj, schema, schema_basic] = self.get_related_object(otype, att_val)
                if len(schema) > 0:
                    alias = schema[0]['name']
                    if alias in obj:
                        self.__setattr__(f'alias_{att["name"]}',obj[alias])
                        self.attributes.append(f'alias_{att["name"]}')
                        self.scopes['basic'].append(f'alias_{att["name"]}')
                    obj_p = {}
                    for df in schema_basic:
                        if df['name'] in obj:
                            obj_p[df['name']] = obj[df['name']]
                    self.__setattr__(f'obj_{att["name"]}',obj_p)
                    self.attributes.append(f'obj_{att["name"]}')
                    self.scopes['basic'].append(f'obj_{att["name"]}')
