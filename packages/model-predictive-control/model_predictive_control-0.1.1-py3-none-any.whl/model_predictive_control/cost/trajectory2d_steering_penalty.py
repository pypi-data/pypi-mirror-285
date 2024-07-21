from typing import List, Tuple

from ..models.bicycle import BicycleModel
from .base import BaseCost


class Traj2DSteeringPenalty(BaseCost):

    steering_penalty: float = 0.0000075

    def __init__(
        self,
        model: BicycleModel,
    ) -> None:
        assert isinstance(model, BicycleModel)
        self.model = model

    def cost(
        self,
        input_sequence: List[Tuple],
        current_state_tuple: Tuple,
        desired_state_sequence: List[Tuple],
    ) -> float:
        cost_val = 0.0
        horizon = len(desired_state_sequence)
        self.model.reset()
        current_state = self.model.base_robot.state.fromtuple(
            current_state_tuple
        )
        assert hasattr(current_state, "x"), "State does not have x"
        assert hasattr(current_state, "y"), "State does not have y"
        for i in range(horizon):
            current_input = self.model.base_robot.inputs.fromtuple(
                input_sequence[i]
            )
            assert hasattr(
                current_input, "steering_angle"
            ), "Inputs doesn't have steering_angle"
            current_state = self.model.run(
                state=current_state,
                inputs=current_input,
            )
            desired_state = self.model.base_robot.state.fromtuple(
                desired_state_sequence[i]
            )

            # Compute cost for each point on the trajectory
            cost_val += (
                (getattr(current_state, "x") - getattr(desired_state, "x"))
                ** 2
                + (getattr(current_state, "y") - getattr(desired_state, "y"))
                ** 2
                + self.steering_penalty * current_input.steering_angle**2
            )

        return cost_val
