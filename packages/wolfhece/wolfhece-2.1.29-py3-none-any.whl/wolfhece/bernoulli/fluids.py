from enum import Enum

class Water():

    rho:float = 1000.
    mu:float  = 1e-3

    @property
    def nu(self) -> float:
        return self.mu / self.rho