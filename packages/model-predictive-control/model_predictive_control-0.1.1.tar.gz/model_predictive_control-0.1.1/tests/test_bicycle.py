import pytest
import numpy as np
from model_predictive_control.models.bicycle import (
    BicycleModel,
    BicycleModelParams,
    BicycleModelState,
    BicycleModelInputs,
    bicycle_model,
)


@pytest.fixture
def default_params():
    return BicycleModelParams(
        time_step=0.1,
        steering_ratio=15.0,
        wheel_base=2.5,
        speed_kp=1.0,
        speed_ki=0.1,
        speed_kd=0.05,
        throttle_min=-1.0,
        throttle_max=1.0,
        throttle_gain=0.1,
    )


@pytest.fixture
def initial_state():
    return BicycleModelState(x=0.0, y=0.0, theta=0.0, velocity=0.0)


@pytest.fixture
def default_inputs():
    return BicycleModelInputs(steering_angle=1.0, desired_velocity=1.0)


@pytest.fixture
def bicycle_model_instance(default_params):
    return BicycleModel(default_params)


def test_params_initialization(bicycle_model_instance, default_params):
    assert (
        bicycle_model_instance.steering_ratio == default_params.steering_ratio
    )
    assert bicycle_model_instance.wheel_base == default_params.wheel_base
    assert bicycle_model_instance.time_step == default_params.time_step
    assert bicycle_model_instance.throttle_gain == default_params.throttle_gain
    assert bicycle_model_instance.speed_pid.Kp == default_params.speed_kp
    assert bicycle_model_instance.speed_pid.Ki == default_params.speed_ki
    assert bicycle_model_instance.speed_pid.Kd == default_params.speed_kd
    assert bicycle_model_instance.speed_pid.output_limits == (
        default_params.throttle_min,
        default_params.throttle_max,
    )


def test_state_initialization_and_conversion():
    state = BicycleModelState(x=1.0, y=2.0, theta=np.pi / 4, velocity=3.0)
    state_tuple = state.totuple()
    assert state_tuple == (1.0, 2.0, np.pi / 4, 3.0)

    new_state = BicycleModelState.fromtuple(state_tuple)
    assert new_state.x == 1.0
    assert new_state.y == 2.0
    assert new_state.theta == np.pi / 4
    assert new_state.velocity == 3.0


def test_bicycle_model_dynamics():
    x = (0.0, 0.0, 0.0, 1.0)  # (X, Y, theta, velocity)
    u = 10.0  # steering angle in degrees
    steering_ratio = 15.0
    wheel_base = 2.5
    time_step = 0.1
    new_state = bicycle_model(
        x, u, x[3], steering_ratio, wheel_base, time_step
    )

    assert new_state[0] != x[0]  # X should have changed
    assert new_state[1] != x[1]  # Y should have changed
    assert new_state[2] != x[2]  # Theta should have changed


def test_pid_and_throttle_response(
    bicycle_model_instance, initial_state, default_inputs
):
    new_state = bicycle_model_instance.run(initial_state, default_inputs)
    assert new_state.velocity != initial_state.velocity
    assert new_state.x != initial_state.x
    assert new_state.y != initial_state.y
    assert new_state.theta != initial_state.theta


def test_full_bicycle_model_run(
    bicycle_model_instance, initial_state, default_inputs
):
    new_state = bicycle_model_instance.run(initial_state, default_inputs)
    assert isinstance(new_state, BicycleModelState)
    assert new_state.velocity >= 0  # Asserting no reverse motion
    assert new_state.x >= initial_state.x  # Moving forward in x direction
    assert new_state.y >= initial_state.y  # Moving forward in y direction
