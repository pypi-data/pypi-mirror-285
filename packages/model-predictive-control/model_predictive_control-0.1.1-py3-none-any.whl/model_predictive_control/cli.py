"""CLI interface for model_predictive_control project.

Be creative! do whatever you want!

- Install click or typer and create a CLI app
- Use builtin argparse
- Start a web application
- Import things from your .base module
"""

import matplotlib.pyplot as plt
import numpy as np

from model_predictive_control.cost.trajectory2d_steering_penalty import (
    Traj2DSteeringPenalty,
)
from model_predictive_control.models.bicycle import (
    BicycleModel,
    BicycleModelInputs,
    BicycleModelParams,
    BicycleModelState,
)
from model_predictive_control.mpc import MPC


def main():  # pragma: no cover
    """
    The main function executes on commands:
    `python -m model_predictive_control` and `$ model_predictive_control `.

    This is your program's entry point.

    You can change this function to do whatever you want.
    Examples:
        * Run a test suite
        * Run a server
        * Do some other stuff
        * Run a command line application (Click, Typer, ArgParse)
        * List all available tasks
        * Run an application (Flask, FastAPI, Django, etc.)
    """

    time_step = 0.1
    velocity = 1.38 * 3  # m/s -> 5 km/h

    theta_list = (
        np.arange(-3, 3, 0.1).tolist() + np.arange(3, -3, -0.1).tolist()
    )

    while True:
        for theta in theta_list:

            # Initialize the Bicycle Model
            params = BicycleModelParams(
                time_step=time_step,
                steering_ratio=13.27,
                wheel_base=2.83972,
                speed_kp=1.0,
                speed_ki=0.1,
                speed_kd=0.05,
                throttle_min=-1.0,
                throttle_max=1.0,
                throttle_gain=5.0,  # Max throttle corresponds to 5m/s^2
            )
            bicycle_model = BicycleModel(params)

            # Define the cost function
            cost = Traj2DSteeringPenalty(model=bicycle_model)

            # Initialize MPC Controller
            horizon = 20
            state_dim = 4  # (x, y, theta, velocity)
            controls_dim = 2  # (steering_angle, velocity)

            mpc = MPC(
                model=bicycle_model,
                cost=cost,
                horizon=horizon,
                state_dim=state_dim,
                controls_dim=controls_dim,
            )

            # Define initial state (x, y, theta, velocity)
            start_state = [0.0, 0.0, 0.0, 1.0]

            # Define desired trajectory: moving in a straight line
            # desired_state_sequence = [
            #     [i * 1.0, i * 0.5, 0.0, 1.0] for i in range(horizon)
            # ]
            desired_state_sequence = [[0.0, 0.0, 0.0, 0.0]]

            theta = np.deg2rad(theta)

            for i in range(horizon - 1):
                desired_state_sequence.append(
                    (
                        desired_state_sequence[-1][0]
                        + time_step * velocity * np.cos(i * theta),
                        desired_state_sequence[-1][1]
                        + time_step * velocity * np.sin(i * theta),
                        0.0,
                        velocity,
                    )
                )

            # Initial control sequence: zero steering and constant speed
            initial_control_sequence = [[0.0, 1.0] for _ in range(horizon)]

            # Define control bounds in radians,
            # velocity between 0.0 and 2.0 m/s
            bounds = [
                [(-np.deg2rad(400), np.deg2rad(400)), (-1.0, 1.0)]
                for _ in range(horizon)
            ]

            # Optimize control inputs using MPC
            optimized_control_sequence = mpc.step(
                start_state_tuple=start_state,
                desired_state_sequence=desired_state_sequence,
                initial_control_sequence=initial_control_sequence,
                bounds=bounds,
                max_iters=50,
            )

            # Simulate the vehicle using the optimized control inputs
            current_state = start_state
            trajectory = [current_state]

            for controls in optimized_control_sequence:
                state_tuple = (
                    current_state[0],
                    current_state[1],
                    current_state[2],
                    current_state[3],
                )
                inputs_tuple = (controls[0], controls[1])
                inputs_obj = BicycleModelInputs.fromtuple(inputs_tuple)
                state_obj = BicycleModelState.fromtuple(state_tuple)
                next_state = bicycle_model.run(state_obj, inputs_obj)
                trajectory.append(list(next_state.totuple()))
                current_state = next_state.totuple()

            # Convert trajectory to numpy array for easier plotting
            trajectory = np.array(trajectory)

            # Plot the results
            # plt.figure(figsize=(10, 6))
            plt.plot(
                [state[1] for state in desired_state_sequence],
                [state[0] for state in desired_state_sequence],
                label="Desired Trajectory",
                linestyle="--",
                color="g",
            )
            plt.plot(
                trajectory[:, 1],  # x coordinates
                trajectory[:, 0],  # y coordinates
                label="MPC Trajectory",
                linestyle="-",
                color="b",
            )
            plt.xlabel("X position (m) (Left -> Right)")
            plt.ylabel("Z position (m) (Away from Car)")
            plt.title("MPC Trajectory vs Desired Trajectory")
            plt.legend()
            plt.grid()
            plt.xlim(-5, 5)
            plt.ylim(0, 10)
            plt.draw()
            plt.pause(0.001)
            plt.cla()
            key = plt.waitforbuttonpress(0.001)
            if key:
                exit()
