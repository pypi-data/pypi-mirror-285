import pytest
import numpy as np
from scipy.optimize import OptimizeResult
from model_predictive_control.mpc import MPC
from model_predictive_control.models.bicycle import (
    BicycleModel,
    BicycleModelParams,
)
from model_predictive_control.cost.trajectory2d_steering_penalty import (
    Traj2DSteeringPenalty,
)

# Fixtures for creating necessary instances


@pytest.fixture
def bicycle_model():
    params = BicycleModelParams(
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
    return BicycleModel(params)


@pytest.fixture
def cost(bicycle_model):
    return Traj2DSteeringPenalty(model=bicycle_model)


@pytest.fixture
def mpc(bicycle_model, cost):
    return MPC(
        model=bicycle_model, cost=cost, horizon=10, state_dim=4, controls_dim=2
    )


@pytest.fixture
def start_state():
    return [0.0, 0.0, 0.0, 1.0]


@pytest.fixture
def desired_state_sequence():
    return [[1.0, 1.0, 0.0, 1.0] for _ in range(10)]


@pytest.fixture
def initial_control_sequence():
    # return [0.0, 1.0]
    return [[0.0, 1.0] for _ in range(10)]


@pytest.fixture
def bounds():
    # return [(-0.5, 0.5), (0.0, 2.0)]
    return [[(-400.0, 400.0), (-1.0, 1.0)] for _ in range(10)]


@pytest.fixture
def max_iters():
    return 50


# Test cases


def test_initialization(mpc, bicycle_model, cost):
    assert mpc.model == bicycle_model
    assert mpc.cost == cost
    assert mpc.horizon == 10
    assert mpc.state_dim == 4
    assert mpc.controls_dim == 2


def test_step_shape(
    mpc,
    start_state,
    desired_state_sequence,
    initial_control_sequence,
    bounds,
    max_iters,
):
    control_sequence = mpc.step(
        start_state,
        desired_state_sequence,
        initial_control_sequence,
        bounds,
        max_iters,
    )
    assert isinstance(control_sequence, list)
    assert len(control_sequence) == 10
    assert all(len(ctrl) == 2 for ctrl in control_sequence)


def test_invalid_model():
    class InvalidModel:
        pass

    with pytest.raises(AssertionError):
        MPC(
            model=InvalidModel(),
            cost=None,
            horizon=10,
            state_dim=4,
            controls_dim=2,
        )


def test_cost_function_call(
    mocker,
    mpc,
    start_state,
    desired_state_sequence,
    initial_control_sequence,
    bounds,
    max_iters,
):
    mock_cost = mocker.patch.object(mpc.cost, "cost", return_value=1.0)
    mpc.step(
        start_state,
        desired_state_sequence,
        initial_control_sequence,
        bounds,
        max_iters,
    )
    assert mock_cost.call_count > 0


# def test_control_sequence_bounds(
#     mpc,
#     start_state,
#     desired_state_sequence,
#     initial_control_sequence,
#     bounds,
#     max_iters,
# ):
#     control_sequence = mpc.step(
#         start_state,
#         desired_state_sequence,
#         initial_control_sequence,
#         bounds,
#         max_iters,
#     )
#     control_sequence_flat = np.array(control_sequence).reshape(-1)
#     bounds_flat = np.array(bounds).reshape(-1, 2)
#     assert bounds_flat.shape[0] == control_sequence_flat.shape[0]
#     for i in range(bounds_flat.shape[0]):
#         assert (
#             bounds_flat[i][0] <= control_sequence_flat[i] <= bounds_flat[i][1]
#         ), f"Value out of bounds ({bounds_flat[i]}) at index {i}: {control_sequence_flat[i]}"


def test_invalid_input_dimensions(mpc, start_state, desired_state_sequence):
    with pytest.raises(AssertionError):
        invalid_control_sequence = [
            [0.0] for _ in range(10)
        ]  # Incorrect controls_dim
        mpc.step(
            start_state,
            desired_state_sequence,
            invalid_control_sequence,
            bounds=[[(0.0, 1.0)] for _ in range(10)],
            max_iters=50,
        )

    with pytest.raises(AssertionError):
        invalid_start_state = [0.0, 0.0]  # Incorrect state_dim
        mpc.step(
            invalid_start_state,
            desired_state_sequence,
            initial_control_sequence=[[0.0, 1.0] for _ in range(10)],
            bounds=[[(0.0, 1.0), (0.0, 1.0)] for _ in range(10)],
            max_iters=50,
        )

    with pytest.raises(AssertionError):
        invalid_desired_state_sequence = [
            [0.0, 0.0, 0.0] for _ in range(10)
        ]  # Incorrect state_dim
        mpc.step(
            start_state,
            invalid_desired_state_sequence,
            initial_control_sequence=[[0.0, 1.0] for _ in range(10)],
            bounds=[[(0.0, 1.0), (0.0, 1.0)] for _ in range(10)],
            max_iters=50,
        )
