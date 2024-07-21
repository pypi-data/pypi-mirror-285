# model_predictive_control

[![codecov](https://codecov.io/gh/AdityaNG/model_predictive_control/branch/main/graph/badge.svg?token=model_predictive_control_token_here)](https://codecov.io/gh/AdityaNG/model_predictive_control)
[![CI](https://github.com/AdityaNG/model_predictive_control/actions/workflows/main.yml/badge.svg)](https://github.com/AdityaNG/model_predictive_control/actions/workflows/main.yml)
[![GitHub License](https://img.shields.io/github/license/AdityaNG/model_predictive_control)](https://github.com/AdityaNG/model_predictive_control/blob/main/LICENSE)
[![PyPI - Version](https://img.shields.io/pypi/v/model_predictive_control)](https://pypi.org/project/model_predictive_control/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/model_predictive_control)


Python implementation of MPC solver

![demo](https://raw.githubusercontent.com/AdityaNG/model_predictive_control/main/media/demo.gif)

## Install it from PyPI

```bash
pip install model_predictive_control
```

## Usage

```py
import numpy as np

from model_predictive_control.cost.trajectory2d_steering_penalty import (
    Traj2DSteeringPenalty,
)
from model_predictive_control.models.bicycle import (
    BicycleModel,
    BicycleModelParams,
)
from model_predictive_control.mpc import MPC

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
desired_state_sequence = [[i * 1.0, i * 0.5, 0.0, 1.0] for i in range(horizon)]

# Initial control sequence: assuming zero steering and constant speed
initial_control_sequence = [[0.0, 1.0] for _ in range(horizon)]

# Define control bounds: steering_angle between -0.5 and 0.5 radians,
# velocity between 0.0 and 2.0 m/s
bounds = [[(-np.deg2rad(400), np.deg2rad(400)), (-1.0, 1.0)] for _ in range(horizon)]

# Optimize control inputs using MPC
optimized_control_sequence = mpc.step(
    start_state_tuple=start_state,
    desired_state_sequence=desired_state_sequence,
    initial_control_sequence=initial_control_sequence,
    bounds=bounds,
    max_iters=50,
)
```

Run the demo with the following

```bash
$ python -m model_predictive_control
#or
$ model_predictive_control
```

## Cite

This work was a part of the D³Nav paper. Cite our work if you find it useful

```bibtex
@article{NG2024D3Nav,
  title={D³Nav: Data-Driven Driving Agents for Autonomous Vehicles in Unstructured Traffic},
  author={Aditya NG and Gowri Srinivas},
  journal={The 35th British Machine Vision Conference (BMVC)},
  year={2024},
  url={https://bmvc2024.org/}
}
``` 


## Development

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## TODO

- [x] Bicycle Model
- [ ] Drone Model
- [x] MPC
- [x] Visualizer Demo
- [ ] MPC Auto-Optimizer: Takes a set of expected vehicle trajectories and the search space of hyperparamters and returns the list of optimal hyperparameters
- [ ] MPC Compiler: Takes the MPC model with a set of expected vehicle trajectories and produces numpy array a mapping from trajectory to control signals. This can be used with a cosine similarity logic to decide on control logic in real time.
