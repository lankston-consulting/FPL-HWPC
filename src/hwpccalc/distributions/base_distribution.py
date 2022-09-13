from abc import ABC, abstractclassmethod, abstractmethod


class BaseDistribution(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def inverse_cdf(self, p: float) -> float:
        raise NotImplemented
