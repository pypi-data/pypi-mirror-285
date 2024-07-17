# File: ArangoDB Metadata and ORM support functions
# Author: alexsanchezvega
# Company: d20
# Version: 1.0

def secure_attribute_name(name):
    from .BasicElement import BasicElement
    from .Element import Element
    from .DBConnector import DBConnector
    exclusions = dir(BasicElement)
    [exclusions.append(e) for e in dir(Element)]
    [exclusions.append(e) for e in dir(DBConnector)]
    return (name not in exclusions and name != None)
