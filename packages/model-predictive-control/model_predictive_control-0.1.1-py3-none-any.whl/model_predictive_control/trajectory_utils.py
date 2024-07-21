"""

trajectory plotting utils: https://github.com/AdityaNG/general-navigation/blob/306fd4eed07a54b0fbc5b6df0ecd1dc78f8ba497/general_navigation/models/model_utils.py  # noqa
"""

import numpy as np


def interpolate_trajectory(
    trajectory: np.ndarray,
    samples: int = 1,
) -> np.ndarray:
    """
    Interpolates the trajectory (N, 2) to (M, 2)
    Where M = N*(S+1)+1

    :param trajectory: (N,2) numpy trajectory
    :type trajectory: np.ndarray
    :param samples: number of samples
    :type samples: int
    :returns: (M,2) interpolated numpy trajectory
    """
    # Calculate the number of segments
    num_segments = trajectory.shape[0] - 1

    # Generate the interpolated trajectory
    interpolated_trajectory = np.zeros((num_segments * (samples + 1) + 1, 2))

    # Fill in the interpolated points
    for i in range(num_segments):
        start = trajectory[i]
        end = trajectory[i + 1]
        interpolated_trajectory[
            i * (samples + 1) : (i + 1) * (samples + 1)
        ] = np.linspace(start, end, samples + 2)[:-1]

    # Add the last point
    interpolated_trajectory[-1] = trajectory[-1]

    return interpolated_trajectory


def get_trajectory_rectangles_coords_3d(
    Pi: np.ndarray, Pj: np.ndarray, width: float
) -> np.ndarray:
    # Pi = Pi.reshape(4, 1)
    # Pj = Pj.reshape(4, 1)
    x_i, y_i = Pi[0], Pi[2]
    x_j, y_j = Pj[0], Pj[2]
    points_2D = get_trajectory_rectangle_coords(x_i, y_i, x_j, y_j, width)
    points_3D_l = []
    for index in range(points_2D.shape[0]):
        # point_2D = points_2D[index]
        point_3D = Pi.copy()
        point_3D[0] = points_2D[index, 0]
        point_3D[2] = points_2D[index, 1]

        points_3D_l.append(point_3D)

    points_3D = np.array(points_3D_l)
    return points_3D


def get_trajectory_rectangle_coords(
    x_i: float, y_i: float, x_j: float, y_j: float, width: float
) -> np.ndarray:
    """
    Takes two adjacent points on the trajecotry and returns the corners of
    a rectange that encompass the two points.
    """
    Pi = np.array([x_i, y_i])
    Pj = np.array([x_j, y_j])
    height = np.linalg.norm(Pi - Pj)
    diagonal = (width**2 + height**2) ** 0.5
    D = diagonal / 2.0

    M = ((Pi + Pj) / 2.0).reshape((2,))
    theta = np.arctan2(Pi[1] - Pj[1], Pi[0] - Pj[0])
    theta += np.pi / 4.0
    points = np.array(
        [
            M
            + np.array(
                [
                    D * np.sin(theta + 0 * np.pi / 2.0),
                    D * np.cos(theta + 0 * np.pi / 2.0),
                ]
            ),
            M
            + np.array(
                [
                    D * np.sin(theta + 1 * np.pi / 2.0),
                    D * np.cos(theta + 1 * np.pi / 2.0),
                ]
            ),
            M
            + np.array(
                [
                    D * np.sin(theta + 2 * np.pi / 2.0),
                    D * np.cos(theta + 2 * np.pi / 2.0),
                ]
            ),
            M
            + np.array(
                [
                    D * np.sin(theta + 3 * np.pi / 2.0),
                    D * np.cos(theta + 3 * np.pi / 2.0),
                ]
            ),
        ]
    )
    return points


def traverse_trajectory(
    traj: np.ndarray,
    distance: float,
) -> np.ndarray:
    """
    Takes a (N, 2) trajectory as input and produces an (M, 2) trajectory such
    that the new trajectory's adjacent points are all seperated by the
    specified distance.

    :param np.ndarray traj: input trajectory in meters (N, 2)
    :param float distance: split distance

    :return np.ndarray split_traj: trajectory where all adjacent points are \
        seperated by the specified distance
    """
    traj_interp = [
        traj[0],
    ]
    dist = 0.0
    total_dist = 0.0
    for traj_i in range(1, traj.shape[0]):
        traj_dist = (
            (traj[traj_i, 0] - traj[traj_i - 1, 0]) ** 2
            + (traj[traj_i, 1] - traj[traj_i - 1, 1]) ** 2
        ) ** 0.5
        if dist + traj_dist > distance:
            traj_interp.append(traj[traj_i - 1])
            dist = traj_dist
        else:
            dist += traj_dist
        total_dist += traj_dist

    return np.array(traj_interp)
