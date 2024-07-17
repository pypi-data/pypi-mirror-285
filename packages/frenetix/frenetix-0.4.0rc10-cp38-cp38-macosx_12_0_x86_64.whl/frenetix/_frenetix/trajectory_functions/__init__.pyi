from . import (
    cost_functions as cost_functions,
    feasability_functions as feasability_functions
)
import _frenetix


class ComputeInitialState(TrajectoryStrategy):
    def __init__(self, coordinateSystem: _frenetix.CoordinateSystemWrapper, wheelBase: float, steeringAngle: float, lowVelocityMode: bool) -> None: ...

    def evaluate_trajectory(self, trajectory: _frenetix.TrajectorySample) -> None: ...

class CostStrategy(TrajectoryStrategy):
    pass

class FeasabilityStrategy(TrajectoryStrategy):
    pass

class FillCoordinates(TrajectoryStrategy):
    def __init__(self, lowVelocityMode: bool, initialOrientation: float, coordinateSystem: _frenetix.CoordinateSystemWrapper, horizon: float) -> None: ...

    def evaluate_trajectory(self, trajectory: _frenetix.TrajectorySample) -> None: ...

class TrajectoryStrategy:
    def evaluate_trajectory(self, trajectory: _frenetix.TrajectorySample) -> None: ...

    @property
    def name(self) -> str: ...
