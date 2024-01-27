from abc import ABC, abstractmethod

# TODO extend class
class IStrategy(ABC):

    @abstractmethod
    def pick_next_move(self, ):
        pass
