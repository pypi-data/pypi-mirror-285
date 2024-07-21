import time
from typing import List, Tuple, cast

import numpy as np
from scipy.optimize import minimize

from .cost.base import BaseCost
from .models.base import BaseRobotModel


class MPC:
    def __init__(
        self,
        model: BaseRobotModel,
        cost: BaseCost,
        horizon: int,
        state_dim: int,
        controls_dim: int,
    ) -> None:
        assert isinstance(model, BaseRobotModel), (
            f"model must be a subclass of {BaseRobotModel}, "
            f"instead got {type(model)}"
        )
        self.model = model
        self.cost = cost
        self.horizon = horizon
        self.state_dim = state_dim
        self.controls_dim = controls_dim

    def step(
        self,
        start_state_tuple: List[float],
        desired_state_sequence: List[List[float]],
        initial_control_sequence: List[float],
        bounds: List[List[float]],
        max_iters: int,
    ) -> List[List[float]]:
        """
        start_state_tuple (self.state_dim,)
        desired_state_sequence (self.horizon, self.state_dim)
        initial_control_sequence (self.horizon, self.controls_dim)
        bounds (self.horizon, self.controls_dim, 2)
        """
        ###########################################
        # Time stamps in seconds
        now = time.time()
        ###########################################

        def cost(u: np.ndarray, x, x_des) -> float:
            u_np = u.reshape(self.horizon, self.controls_dim).tolist()
            return self.cost.cost(cast(List[Tuple], u_np), x, x_des)

        #######################################################################
        # Optimizer Setup

        # initial state and input sequence
        x0 = np.array(start_state_tuple)  # (self.state_dim,)
        assert x0.shape == (self.state_dim,)
        # Incorporate current trajectory
        u0 = np.array(
            initial_control_sequence
        )  # (self.horizon, self.controls_dim)
        assert u0.shape == (
            self.horizon,
            self.controls_dim,
        )
        xdes = np.array(desired_state_sequence)
        assert xdes.shape == (
            self.horizon,
            self.state_dim,
        ), f"Expected: {(self.horizon, self.state_dim)}, got {xdes.shape}"
        bounds_np = np.array(bounds)
        assert bounds_np.shape == (
            self.horizon,
            self.controls_dim,
            2,
        ), bounds_np.shape

        # Reshape controls and bounds
        u0 = u0.reshape(-1)
        bounds_np = bounds_np.reshape(-1, 2)

        #######################################################################
        # Optimize the cost function
        res = minimize(
            cost,
            u0,
            args=(x0, xdes),
            method="SLSQP",
            # bounds=bounds_np,
            options=dict(maxiter=max_iters),
        )

        optimized_control_sequence = res.x.reshape(
            self.horizon, self.controls_dim
        )  # (self.horizon, self.controls_dim)
        assert optimized_control_sequence.shape == (
            self.horizon,
            self.controls_dim,
        ), optimized_control_sequence.shape

        optimized_control_sequence_list = optimized_control_sequence.tolist()

        #####################################
        self.last_update_time = now
        return optimized_control_sequence_list
