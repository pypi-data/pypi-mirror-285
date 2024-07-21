import pytest
from model_predictive_control.cost.trajectory2d_steering_penalty import (
    Traj2DSteeringPenalty,
)
from model_predictive_control.models.bicycle import (
    BicycleModel,
    BicycleModelParams,
    BicycleModelState,
    BicycleModelInputs,
)

# Fixtures for creating necessary instances and states


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
def traj_cost(bicycle_model):
    return Traj2DSteeringPenalty(model=bicycle_model)


@pytest.fixture
def input_sequence():
    return [
        (0.0, 1.0),  # (steering_angle, desired_velocity)
        (5.0, 1.0),
        (10.0, 1.0),
    ]


@pytest.fixture
def current_state():
    return (0.0, 0.0, 0.0, 1.0)  # (x, y, theta, velocity)


@pytest.fixture
def desired_state_sequence():
    return [
        (1.0, 1.0, 0.0, 1.0),
        (2.0, 2.0, 0.0, 1.0),
        (3.0, 3.0, 0.0, 1.0),
    ]


# Test cases


def test_initialization(traj_cost):
    assert traj_cost.steering_penalty == 0.0000075


def test_unsupported_model_error():
    class UnsupportedModel:
        pass

    with pytest.raises(
        AssertionError,
    ):
        model = Traj2DSteeringPenalty(model=UnsupportedModel())
        cost = model.cost(
            [(0,)],
            (0,),
            [(0,)],
        )
        print(cost)


def test_cost_calculation(
    traj_cost, input_sequence, current_state, desired_state_sequence
):
    cost_val = traj_cost.cost(
        input_sequence, current_state, desired_state_sequence
    )
    assert cost_val > 0  # Basic check that cost is calculated
    # Optionally, more precise checks on cost can be added


def test_missing_x_attribute(
    traj_cost, input_sequence, desired_state_sequence
):
    current_state_invalid = (0.0, 0.0, 0.0)  # Missing velocity for simplicity
    with pytest.raises(AssertionError):
        traj_cost.cost(
            input_sequence, current_state_invalid, desired_state_sequence
        )


def test_missing_steering_angle_attribute(
    traj_cost, current_state, desired_state_sequence
):
    input_sequence_invalid = [
        (0.0, 1.0),  # Correct
        (1.0,),  # Missing steering angle
        (2.0, 1.0),
    ]
    with pytest.raises(AssertionError):
        traj_cost.cost(
            input_sequence_invalid, current_state, desired_state_sequence
        )
