from abc import ABC, abstractmethod
import pickle


class Pickler(ABC):
    def pickle(self) -> None:
        """Basic function to pickle an object and give it the class name"""
        n = self.__class__.__name__
        with open("results/" + n + ".pkl", "wb") as p:
            pickle.dump(self, p)

    @classmethod
    def unpickle(cls):
        """Basic function to load pickled object from disk

        Returns:
            [type]: [description]
        """
        n = cls.__name__
        with open("results/" + n + ".pkl", "rb") as p:
            return pickle.load(p)
