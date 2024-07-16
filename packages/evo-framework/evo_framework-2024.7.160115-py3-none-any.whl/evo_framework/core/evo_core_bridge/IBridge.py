from abc import ABC, abstractmethod

class IBridge(ABC):
    @abstractmethod
    async def onERequest(self, eRequest):
        """Implement this method"""
        pass

    @abstractmethod
    async def onEResponse(self, eResponse):
        """Implement this method"""
        pass