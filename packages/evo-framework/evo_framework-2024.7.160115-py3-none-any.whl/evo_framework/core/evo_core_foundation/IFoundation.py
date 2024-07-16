from abc import ABC, abstractmethod
import asyncio
from evo_framework.entity.EObject import EObject
from evo_framework.core.evo_core_type.entity.EvoMap import EvoMap

class IFoundation(ABC):
    @abstractmethod
    async def doSet(self, eObject, isFoundation:bool = True):
        """Implement this method"""
        pass

    @abstractmethod
    async def doGetOne(self, iD) -> EObject:
        """Implement this method"""
        pass
    
    @abstractmethod
    async def doGet(self, eQuery) -> EvoMap:
        """Implement this method"""
        pass
    
    @abstractmethod
    async def doDel(self, iD, isFoundation:bool = True):
        """Implement this method"""
        pass
            