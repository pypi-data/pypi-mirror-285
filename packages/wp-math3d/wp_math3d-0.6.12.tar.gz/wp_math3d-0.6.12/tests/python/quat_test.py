from typing import List, Type, Union

import numpy as np
import pytest

import math3d as m3d

QuaternionCls = Type[Union[m3d.Quaternionf, m3d.Quaterniond]]
Vector3Cls = Type[Union[m3d.Vector3f, m3d.Vector3d]]

Quaternion = Union[m3d.Quaternionf, m3d.Quaterniond]


def quat_all_close(
    quat: Quaternion, q_list: List[float], tol: float = 1e-5
) -> bool:
    return (
        np.abs(quat.w - q_list[0]) < tol
        and np.abs(quat.x - q_list[1]) < tol
        and np.abs(quat.y - q_list[2]) < tol
        and np.abs(quat.z - q_list[3]) < tol
    )


@pytest.mark.parametrize("Quat", [(m3d.Quaternionf), (m3d.Quaterniond)])
def test_quat_attrs(Quat: QuaternionCls) -> None:
    assert (
        hasattr(Quat, "w")
        and hasattr(Quat, "x")
        and hasattr(Quat, "y")
        and hasattr(Quat, "z")
    )


@pytest.mark.parametrize("Quat", [(m3d.Quaternionf), (m3d.Quaterniond)])
def test_default_constructor(Quat: QuaternionCls) -> None:
    q = Quat()
    assert q.w == 1.0 and q.x == 0.0 and q.y == 0.0 and q.z == 0.0


@pytest.mark.parametrize("Quat", [(m3d.Quaternionf), (m3d.Quaterniond)])
def test_single_scalar_arg_constructor(Quat: QuaternionCls) -> None:
    q = Quat(2.0)
    assert q.w == 2.0 and q.x == 0.0 and q.y == 0.0 and q.z == 0.0


@pytest.mark.parametrize("Quat", [(m3d.Quaternionf), (m3d.Quaterniond)])
def test_four_scalars_args_constructor(Quat: QuaternionCls) -> None:
    q = Quat(2.0, 3.0, 5.0, 7.0)
    assert q.w == 2.0 and q.x == 3.0 and q.y == 5.0 and q.z == 7.0


@pytest.mark.parametrize(
    "Quat,FloatType",
    [(m3d.Quaternionf, np.float32), (m3d.Quaterniond, np.float64)],
)
def test_numpy_array_constructor(Quat: QuaternionCls, FloatType: type) -> None:
    arr_np = np.array([11.0, 13.0, 17.0, 19.0])
    q = Quat(arr_np.astype(FloatType))
    assert q.w == 11.0 and q.x == 13.0 and q.y == 17.0 and q.z == 19.0

    q = Quat(arr_np.reshape(1, 4).astype(FloatType))
    assert q.w == 11.0 and q.x == 13.0 and q.y == 17.0 and q.z == 19.0

    q = Quat(arr_np.reshape(4, 1).astype(FloatType))
    assert q.w == 11.0 and q.x == 13.0 and q.y == 17.0 and q.z == 19.0

    q = Quat([11.0, 13.0, 17.0, 19.0])
    assert q.w == 11.0 and q.x == 13.0 and q.y == 17.0 and q.z == 19.0


@pytest.mark.parametrize("Quat", [(m3d.Quaternionf), (m3d.Quaterniond)])
def test_quat_accessors(Quat: QuaternionCls) -> None:
    q = Quat(3.0, 5.0, 7.0, 11.0)
    assert q.w == 3.0 and q.x == 5.0 and q.y == 7.0 and q.z == 11.0
    assert q[0] == 3.0 and q[1] == 5.0 and q[2] == 7.0 and q[3] == 11.0

    q[0], q.z = 13.0, 17.0
    assert q.w == 13.0 and q[3] == 17.0


@pytest.mark.parametrize("Quat", [(m3d.Quaternionf), (m3d.Quaterniond)])
class TestQuatOperators:
    def test_comparison_operator(self, Quat: QuaternionCls) -> None:
        q1 = Quat(1.0, 2.0, 3.0, 4.0)
        q2 = Quat(1.0, 2.0, 3.0, 4.0)
        assert q1 == q2

        q1.w, q2.w = 11.0, 13.0
        assert q1 != q2

    def test_quat_addition(self, Quat: QuaternionCls) -> None:
        q1 = Quat(1.0, 2.0, 4.0, 8.0)
        q2 = Quat(1.0, 3.0, 9.0, 27.0)
        q_sum = q1 + q2
        assert (
            q_sum.w == 2.0
            and q_sum.x == 5.0
            and q_sum.y == 13.0
            and q_sum.z == 35.0
        )

    def test_quat_substraction(self, Quat: QuaternionCls) -> None:
        q1 = Quat(1.0, 2.0, 4.0, 8.0)
        q2 = Quat(1.0, 3.0, 9.0, 27.0)
        q_sum = q1 - q2
        assert (
            q_sum.w == 0.0
            and q_sum.x == -1.0
            and q_sum.y == -5.0
            and q_sum.z == -19.0
        )

    def test_quat_scalar_product(self, Quat: QuaternionCls) -> None:
        q, scale = Quat(1.0, 2.0, 3.0, 4.0), 2.5
        q_scaled = q * scale
        assert (
            q_scaled.w == 2.5
            and q_scaled.x == 5.0
            and q_scaled.y == 7.5
            and q_scaled.z == 10.0
        )
        q_scaled = scale * q
        assert (
            q_scaled.w == 2.5
            and q_scaled.x == 5.0
            and q_scaled.y == 7.5
            and q_scaled.z == 10.0
        )

    def test_quat_multiplication(self, Quat: QuaternionCls) -> None:
        i = Quat(0.0, 1.0, 0.0, 0.0)
        j = Quat(0.0, 0.0, 1.0, 0.0)
        k = Quat(0.0, 0.0, 0.0, 1.0)
        assert i * j == k and j * k == i and k * i == j

        q1 = Quat(1.0, 2.0, 3.0, 4.0)
        q2 = Quat(1.0, 3.0, 5.0, 7.0)
        q_mul = q1 * q2
        assert (
            q_mul.w == -48.0
            and q_mul.x == 6.0
            and q_mul.y == 6.0
            and q_mul.z == 12.0
        )


@pytest.mark.parametrize("Quat", [(m3d.Quaternionf), (m3d.Quaterniond)])
class TestQuatMethods:
    def test_length(self, Quat: QuaternionCls) -> None:
        EPSILON = 1e-3
        w, x, y, z = 1.0, 2.0, 3.0, 4.0
        q = Quat(w, x, y, z)
        expected_length_square = w**2 + x**2 + y**2 + z**2
        expected_length = np.sqrt(expected_length_square)
        assert np.abs(q.lengthSquare() - expected_length_square) < EPSILON
        assert np.abs(q.length() - expected_length) < EPSILON

    def test_normalize_in_place(self, Quat: QuaternionCls) -> None:
        EPSILON = 1e-3
        w, x, y, z = 1.0, 2.0, 3.0, 4.0
        norm = np.sqrt(w**2 + x**2 + y**2 + z**2)
        q = Quat(w, x, y, z)
        q.normalize_()
        assert (
            np.abs(q.w - w / norm) < EPSILON
            and np.abs(q.y - y / norm) < EPSILON
            and np.abs(q.z - z / norm) < EPSILON
            and np.abs(q.x - x / norm) < EPSILON
        )

    def test_normalize(self, Quat: QuaternionCls) -> None:
        EPSILON = 1e-3
        w, x, y, z = 1.0, 2.0, 3.0, 4.0
        norm = np.sqrt(w**2 + x**2 + y**2 + z**2)
        q = Quat(w, x, y, z)
        q_n = q.normalize()
        assert (
            np.abs(q_n.w - w / norm) < EPSILON
            and np.abs(q_n.y - y / norm) < EPSILON
            and np.abs(q_n.z - z / norm) < EPSILON
            and np.abs(q_n.x - x / norm) < EPSILON
        )

    def test_conjugation(self, Quat: QuaternionCls) -> None:
        w, x, y, z = 1.0, 2.0, 3.0, 4.0
        q = Quat(w, x, y, z)
        q_conj = q.conjugate()
        assert (
            q_conj.w == w
            and q_conj.x == -x
            and q_conj.y == -y
            and q_conj.z == -z
        )

    def test_inverse(self, Quat: QuaternionCls) -> None:
        EPSILON = 1e-5
        w, x, y, z = 1.0, 2.0, 3.0, 4.0
        norm_square = w**2 + x**2 + y**2 + z**2
        q = Quat(w, x, y, z)
        q_inv = q.inverse()

        assert np.abs(q_inv.w - w / norm_square) < EPSILON
        assert np.abs(q_inv.x + x / norm_square) < EPSILON
        assert np.abs(q_inv.y + y / norm_square) < EPSILON
        assert np.abs(q_inv.z + z / norm_square) < EPSILON


@pytest.mark.parametrize("Quat", [(m3d.Quaternionf), (m3d.Quaterniond)])
def test_quat_factory_functions(Quat: QuaternionCls) -> None:
    # Create quaternions using RotationXYZ functions, and check the
    # implementation works as expected
    theta, epsilon = np.pi / 2.0, 1e-5
    cos_half_t, sin_half_t = np.cos(theta / 2.0), np.sin(theta / 2.0)
    q_rot_x = Quat.RotationX(theta)  # type: ignore
    q_rot_y = Quat.RotationY(theta)  # type: ignore
    q_rot_z = Quat.RotationZ(theta)  # type: ignore

    assert quat_all_close(q_rot_x, [cos_half_t, sin_half_t, 0.0, 0.0], epsilon)
    assert quat_all_close(q_rot_y, [cos_half_t, 0.0, sin_half_t, 0.0], epsilon)
    assert quat_all_close(q_rot_z, [cos_half_t, 0.0, 0.0, sin_half_t], epsilon)


@pytest.mark.parametrize(
    "Quat,Vec3,FloatType",
    [
        (m3d.Quaternionf, m3d.Vector3f, np.float32),
        (m3d.Quaterniond, m3d.Vector3d, np.float64),
    ],
)
def test_quat_rotate_vec(
    Quat: QuaternionCls, Vec3: Vector3Cls, FloatType: type
) -> None:
    np_i = np.array([1.0, 0.0, 0.0])
    np_j = np.array([0.0, 1.0, 0.0])
    np_k = np.array([0.0, 0.0, 1.0])
    vec_i = Vec3(np_i.astype(FloatType))
    vec_j = Vec3(np_j.astype(FloatType))
    vec_k = Vec3(np_k.astype(FloatType))

    q_rot_x = Quat.RotationX(np.pi / 2.0)  # type: ignore
    q_rot_y = Quat.RotationY(np.pi / 2.0)  # type: ignore
    q_rot_z = Quat.RotationZ(np.pi / 2.0)  # type: ignore

    assert vec_j == q_rot_z.rotate(vec_i)
    assert vec_k == q_rot_x.rotate(vec_j)
    assert vec_i == q_rot_y.rotate(vec_k)
