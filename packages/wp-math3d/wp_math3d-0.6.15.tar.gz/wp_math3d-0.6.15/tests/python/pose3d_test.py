from typing import Type, Union, cast

import numpy as np
import pytest

import math3d as m3d

Vec3Cls = Type[Union[m3d.Vector3f, m3d.Vector3d]]
QuatCls = Type[Union[m3d.Quaternionf, m3d.Quaterniond]]
Mat3Cls = Type[Union[m3d.Matrix3f, m3d.Matrix3d]]
Pose3dCls = Type[Union[m3d.Pose3d_f, m3d.Pose3d_d]]

np.random.seed(0)

# NOTE: We're ignoring a lot of typing errors from pyright related to helper
# function used for creating rotation types. It's just an issue with the typing


@pytest.mark.parametrize("Class", [(m3d.Pose3d_f), (m3d.Pose3d_d)])
def test_pose3d_attrs(Class: Pose3dCls) -> None:
    # Make sure we have exposed 'position' and 'orientation' properties
    assert hasattr(Class, "position") and hasattr(Class, "orientation")


@pytest.mark.parametrize(
    "Class,Type", [(m3d.Pose3d_f, np.float32), (m3d.Pose3d_d, np.float64)]
)
def test_default_constructor(Class: Pose3dCls, Type: type) -> None:
    pose = Class()
    # Default position is set to the world origin
    assert np.allclose(
        cast(np.ndarray, pose.position),
        np.array([0.0, 0.0, 0.0], dtype=Type),
    )
    # Default orientation is set to the (w=1, x=0, y=0, z=0)
    assert np.allclose(
        cast(np.ndarray, pose.orientation),
        np.array([1.0, 0.0, 0.0, 0.0], dtype=Type),
    )


@pytest.mark.parametrize(
    "Pose,Vec3,Quat,Type",
    [
        (m3d.Pose3d_f, m3d.Vector3f, m3d.Quaternionf, np.float32),
        (m3d.Pose3d_d, m3d.Vector3d, m3d.Quaterniond, np.float64),
    ],
)
def test_pos_quat_constructor(
    Pose: Pose3dCls, Vec3: Vec3Cls, Quat: QuatCls, Type: type
) -> None:
    position = Vec3(np.random.randn(1, 3).astype(Type))
    quat_orientation = Quat(np.random.randn(1, 4).astype(Type))
    pose = Pose(position, quat_orientation)
    # Position should be copied directly to the pose object
    assert np.allclose(
        cast(np.ndarray, pose.position), cast(np.ndarray, position)
    )
    # Orientation is normalized to ensure it represents a rotation
    assert np.abs(pose.orientation.length() - 1.0) < 1e-5


@pytest.mark.parametrize(
    "Pose,Vec3,Mat3,Quat,Type",
    [
        (m3d.Pose3d_f, m3d.Vector3f, m3d.Matrix3f, m3d.Quaternionf, np.float32),
        (m3d.Pose3d_d, m3d.Vector3d, m3d.Matrix3d, m3d.Quaterniond, np.float64),
    ],
)
def test_pos_mat3_constructor(
    Pose: Pose3dCls, Vec3: Vec3Cls, Mat3: Mat3Cls, Quat: QuatCls, Type: type
) -> None:
    position = Vec3(np.random.randn(1, 3).astype(Type))
    # NOTE(wilbert): if using [-pi, pi], we might get neg. quaternions, which
    # in the end result in the same orientation, but won't check using allclose
    angle = np.pi * (np.random.random() - 0.5)

    rotmat = Mat3.RotationX(angle)  # type: ignore
    pose = Pose(position, rotmat)
    assert np.allclose(
        cast(np.ndarray, pose.position), cast(np.ndarray, position)
    )
    assert np.allclose(
        cast(np.ndarray, pose.orientation),
        cast(np.ndarray, Quat.RotationX(angle)),  # type: ignore
        atol=1e-5,
    )
    assert np.abs(pose.orientation.length() - 1.0) < 1e-5

    rotmat = Mat3.RotationY(angle)  # type: ignore
    pose = Pose(position, rotmat)
    assert np.allclose(
        cast(np.ndarray, pose.position), cast(np.ndarray, position)
    )
    assert np.allclose(
        cast(np.ndarray, pose.orientation),
        cast(np.ndarray, Quat.RotationY(angle)),  # type: ignore
        atol=1e-5,
    )
    assert np.abs(pose.orientation.length() - 1.0) < 1e-5

    rotmat = Mat3.RotationZ(angle)  # type: ignore
    pose = Pose(position, rotmat)
    assert np.allclose(
        cast(np.ndarray, pose.position), cast(np.ndarray, position)
    )
    assert np.allclose(
        cast(np.ndarray, pose.orientation),
        cast(np.ndarray, Quat.RotationZ(angle)),  # type: ignore
        atol=1e-5,
    )
    assert np.abs(pose.orientation.length() - 1.0) < 1e-5


@pytest.mark.parametrize(
    "Pose,Vec3,Quat,Type",
    [
        (m3d.Pose3d_f, m3d.Vector3f, m3d.Quaternionf, np.float32),
        (m3d.Pose3d_d, m3d.Vector3d, m3d.Quaterniond, np.float64),
    ],
)
def test_apply_method(
    Pose: Pose3dCls, Vec3: Vec3Cls, Quat: QuatCls, Type: type
) -> None:
    # Point B in A = (1.0, 1.0, 1.0)
    # X of A in W = {pos=(-3.0, 0.0, 0.0), rot=quat_rot_z(PI / 2)}
    # Point B in W = (-4.0, 1.0, 1.0)
    p_BA = Vec3(1.0, 1.0, 1.0)
    X_AW = Pose(
        Vec3(-3.0, 0.0, 0.0), Quat.RotationZ(np.pi / 2.0)  # type: ignore
    )
    p_BW = X_AW.apply(p_BA)
    assert np.allclose(
        cast(np.ndarray, p_BW), np.array([-4.0, 1.0, 1.0]).astype(Type)
    )


@pytest.mark.parametrize(
    "Pose,Vec3,Quat,Type",
    [
        (m3d.Pose3d_f, m3d.Vector3f, m3d.Quaternionf, np.float32),
        (m3d.Pose3d_d, m3d.Vector3d, m3d.Quaterniond, np.float64),
    ],
)
def test_inverse_method(
    Pose: Pose3dCls, Vec3: Vec3Cls, Quat: QuatCls, Type: type
) -> None:
    # X of A in W = {pos=(0.0, 3.0, 0.0), rot=quat_rot_x(PI / 2)}
    # X of W in A = (pos=(0.0, 0.0, 3.0), rot=quat_rot_x(-PI / 2))
    X_AW = Pose(
        Vec3(0.0, 3.0, 0.0), Quat.RotationX(np.pi / 2.0)  # type: ignore
    )
    X_WA = X_AW.inverse()
    assert np.allclose(
        cast(np.ndarray, X_WA.position), np.array([0.0, 0.0, 3.0], dtype=Type)
    )
    assert np.allclose(
        cast(np.ndarray, X_WA.orientation),
        cast(np.ndarray, Quat.RotationX(-np.pi / 2.0)),  # type: ignore
    )


@pytest.mark.parametrize(
    "Pose,Vec3,Quat,Type",
    [
        (m3d.Pose3d_f, m3d.Vector3f, m3d.Quaternionf, np.float32),
        (m3d.Pose3d_d, m3d.Vector3d, m3d.Quaterniond, np.float64),
    ],
)
def test_vecmul_operator_method(
    Pose: Pose3dCls, Vec3: Vec3Cls, Quat: QuatCls, Type: type
) -> None:
    # Point B in A = (1.0, 1.0, 1.0)
    # X of A in W = {pos=(-3.0, 0.0, 0.0), rot=quat_rot_z(PI / 2)}
    # Point B in W = (-4.0, 1.0, 1.0)
    p_BA = Vec3(1.0, 1.0, 1.0)
    X_AW = Pose(
        Vec3(-3.0, 0.0, 0.0), Quat.RotationZ(np.pi / 2.0)  # type: ignore
    )
    p_BW = X_AW * p_BA
    assert np.allclose(
        cast(np.ndarray, p_BW), np.array([-4.0, 1.0, 1.0], dtype=Type)
    )

    # Point C in B = (1.0, 1.0, 1.0)
    # X of B in A = {pos(0.0, 5.0, 0.0), rot=quat_rot_x(PI / 2)}
    # Point C in A = (1.0, 6.0, -1.0)
    # X of A in W = {pos(0.0, 5.0, 0.0), rot=quat_rot_y(PI / 2)}
    # Point C in W = (1.0, 6.0, 6.0)
    X_BA = Pose(
        Vec3(0.0, 5.0, 0.0), Quat.RotationY(np.pi / 2.0)  # type: ignore
    )
    X_AW = Pose(
        Vec3(0.0, 5.0, 0.0), Quat.RotationX(np.pi / 2.0)  # type: ignore
    )
    p_CB = Vec3(1.0, 1.0, 1.0)
    p_CA = X_BA * p_CB
    assert np.allclose(
        cast(np.ndarray, p_CA), np.array([1.0, 6.0, -1.0], dtype=Type)
    )
    p_CW = X_AW * p_CA
    assert np.allclose(
        cast(np.ndarray, p_CW), np.array([1.0, 6.0, 6.0], dtype=Type)
    )


@pytest.mark.parametrize(
    "Pose,Vec3,Quat,Type",
    [
        (m3d.Pose3d_f, m3d.Vector3f, m3d.Quaternionf, np.float32),
        (m3d.Pose3d_d, m3d.Vector3d, m3d.Quaterniond, np.float64),
    ],
)
def test_posemul_operator_method(
    Pose: Pose3dCls, Vec3: Vec3Cls, Quat: QuatCls, Type: type
) -> None:
    # Point C in B = (1.0, 1.0, 1.0)
    # X of B in A = {pos(0.0, 5.0, 0.0), rot=quat_rot_x(PI / 2)}
    # Point C in A = (1.0, 6.0, -1.0)
    # X of A in W = {pos(0.0, 5.0, 0.0), rot=quat_rot_y(PI / 2)}
    # Point C in W = (1.0, 6.0, 6.0)
    # X of B in W = X_AW * X_BA = ...
    # ... {pos(0.0, 5.0, 5.0), rot=quat_rot_x(PI / 2) * quat_rot_y(PI / 2)}
    p_CB = Vec3(1.0, 1.0, 1.0)
    X_BA = Pose(
        Vec3(0.0, 5.0, 0.0), Quat.RotationY(np.pi / 2.0)  # type: ignore
    )
    X_AW = Pose(
        Vec3(0.0, 5.0, 0.0), Quat.RotationX(np.pi / 2.0)  # type: ignore
    )
    X_BW = X_AW * X_BA
    assert np.allclose(
        cast(np.ndarray, X_BW.position), np.array([0.0, 5.0, 5.0], dtype=Type)
    )
    assert np.allclose(
        cast(np.ndarray, X_BW.orientation),
        cast(
            np.ndarray,
            Quat.RotationX(np.pi / 2.0)  # type: ignore
            * Quat.RotationY(np.pi / 2.0),  # type: ignore
        ),
    )
    p_CW = X_BW.apply(p_CB)
    assert np.allclose(
        cast(np.ndarray, p_CW), np.array([1.0, 6.0, 6.0], dtype=Type)
    )
