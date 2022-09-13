from math import sqrt
from base_distribution import BaseDistribution


class TriangularDistribution(BaseDistribution):
    def __init__(self, min: float, max: float, mode: float) -> None:
        super().__init__()

        self.min = min
        self.max = max
        self.mode = mode
        self.mid = (mode - min) / (max - min)
        self.case1m = (max - min) * (mode - min)
        self.case2m = (max - min) * (max - mode)

    def inverse_cdf(self, p: float) -> float:
        icdf = 0
        if p <= self.mid:
            icdf = self.min + sqrt(p * self.case1m)
        else:
            icdf = self.max - sqrt((1 - p) * self.case2m)
        return icdf
