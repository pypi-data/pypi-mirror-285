from BasicElement import BasicElement

class BasicElementTest(BasicElement):
    db_name = 'UNIT_TEST'
    
    def make(self):
        self.attributes = ['_key', 'test']
        for key in self.attributes:
            setattr(self, key, None)
            
    @classmethod
    def get_collection(cls):
        return 'orphan1'

    def get_class(self):
        return 'BasicElementTest'
    
    def isEdge(self):
        return False

    def vertex(self):
        return {}