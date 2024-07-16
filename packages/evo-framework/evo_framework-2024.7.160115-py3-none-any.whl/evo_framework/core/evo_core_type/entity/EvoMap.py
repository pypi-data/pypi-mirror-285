#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation    https://github.com/cyborg-ai-git # 
#========================================================================================================================================

#from typing import TypeVar
#_T = TypeVar("_T")

class EvoMap(object):
    def __init__(self):
        self.__dictionary = {}

    def doSet(self, eObject):
        self.__dictionary[eObject.id] = eObject

    def doGet(self, id):
        return self.__dictionary.get(id)

    def doDel(self, id):
        if id is not None:
            if id in self.__dictionary.keys():
                self.__dictionary.pop(id)
                       
    def doDelAll(self):
        self.__dictionary.clear()
        
    def items(self):
        return self.__dictionary.items()
    
    def keys(self):
        return self.__dictionary.keys()
    
    def values(self):
        return self.__dictionary.values()
    
        
    def __str__(self) ->str:
        from evo_framework.entity.EObject import EObject
        strReturn = ""
        for key,value in self.items():
            strValue = f"{key}: None"
            if value is not None:
                if isinstance(value, EObject):
                    strValue = f"{key!r}: {value.__class__.__name__} {value.toStringID()} {value.time}"
                else:
                    strValue = f"{key!r}: {value.__class__.__name__}"
                                  
            strReturn = "\n".join([strReturn, f"\t\t{strValue}"])

        return strReturn

'''
import json
class EvoMapEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, EvoMap):
            return obj.name  # {'name': obj.name, 'dictionary': obj.dictionary}
        return json.JSONEncoder.default(self, obj)

'''