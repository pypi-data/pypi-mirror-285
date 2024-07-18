from typing import Type, Union

import numpy as np
import pytest

import math3d as m3d

Vector3Cls = Type[Union[m3d.Vector3f, m3d.Vector3d]]


@pytest.mark.parametrize("Vec3", [(m3d.Vector3f), (m3d.Vector3d)])
def test_vec3_attrs(Vec3: Vector3Cls):
    # Make sure we have exposed x, y, and z as properties
    assert hasattr(Vec3, "x") and hasattr(Vec3, "y") and hasattr(Vec3, "z")


@pytest.mark.parametrize("Vec3", [(m3d.Vector3f), (m3d.Vector3d)])
class TestVec3Constructors:
    def test_default_constructor(self, Vec3: Vector3Cls) -> None:
        # Default constructor initializes to (0.0, 0.0, 0.0)
        vec = Vec3()
        assert (vec.x == 0.0) and (vec.y == 0.0) and (vec.z == 0.0)

    def test_single_arg_constructor(self, Vec3: Vector3Cls) -> None:
        # Single scalar argument x initializes to (x, x, x)
        vec = Vec3(1.0)
        assert (vec.x == 1.0) and (vec.y == 1.0) and (vec.z == 1.0)

    def test_double_args_constructor(self, Vec3: Vector3Cls) -> None:
        # Two scalar arguments x, y initializes to (x, y, y)
        vec = Vec3(1.0, 2.0)
        assert (vec.x == 1.0) and (vec.y == 2.0) and (vec.z == 2.0)

    def test_full_args_constructor(self, Vec3: Vector3Cls) -> None:
        # Three scalar arguments x, y, z, initializes to (v, y, z)
        vec = Vec3(1.0, 2.0, 3.0)
        assert (vec.x == 1.0) and (vec.y == 2.0) and (vec.z == 3.0)


@pytest.mark.parametrize(
    "Vec3,FloatType", [(m3d.Vector3f, np.float32), (m3d.Vector3d, np.float64)]
)
def test_numpy_array_constructor(Vec3: Vector3Cls, FloatType):
    # From a numpy array (requires same dtype)
    vec_np = np.array([19.0, 23.0, 29.0])
    vec = Vec3(vec_np.astype(FloatType))
    assert (vec.x == 19.0) and (vec.y == 23.0) and (vec.z == 29.0)

    vec = Vec3(vec_np.reshape(1, 3).astype(FloatType))
    assert (vec.x == 19.0) and (vec.y == 23.0) and (vec.z == 29.0)

    vec = Vec3(vec_np.reshape(3, 1).astype(FloatType))
    assert (vec.x == 19.0) and (vec.y == 23.0) and (vec.z == 29.0)


@pytest.mark.parametrize("Vec3", [(m3d.Vector3f), (m3d.Vector3d)])
def test_vec3_accessors(Vec3: Vector3Cls) -> None:
    # Can get x, y, and z as properties
    vec = Vec3(3.0, 7.0, 11.0)
    assert (vec.x == 3.0) and (vec.y == 7.0) and (vec.z == 11.0)
    # Can get elements using __getitem__ as well
    assert (vec[0] == 3.0) and (vec[1] == 7.0) and (vec[2] == 11.0)
    # Can also update the entries using either of the two accessors
    vec.x, vec.y, vec.z = 1.0, 2.0, 3.0
    assert (vec.x == 1.0) and (vec.y == 2.0) and (vec.z == 3.0)


@pytest.mark.parametrize("Vec3", [(m3d.Vector3f), (m3d.Vector3d)])
class TestVec3Operators:
    def test_comparison_operator(self, Vec3: Vector3Cls) -> None:
        vec_a = Vec3(1.0, 2.0, 3.0)
        vec_b = Vec3(1.0, 2.0, 3.0)
        # Comparison __eq__ internally calls == operator, which uses an epsilon
        assert vec_a == vec_b

        vec_b.x, vec_b.y, vec_b.z = 1.1, 2.1, 3.1
        # Comparison __neq__ internally calls != operator, which uses an epsilon
        assert vec_a != vec_b

    def test_vector_addition(self, Vec3: Vector3Cls) -> None:
        vec_a = Vec3(3.0, 7.0, 11.0)
        vec_b = Vec3(4.0, 5.0, 6.0)
        vec_sum = vec_a + vec_b
        assert (
            (vec_sum.x == 7.0) and (vec_sum.y == 12.0) and (vec_sum.z == 17.0)
        )

    def test_vector_substraction(self, Vec3: Vector3Cls) -> None:
        vec_a = Vec3(3.0, 7.0, 11.0)
        vec_b = Vec3(4.0, 5.0, 6.0)
        vec_diff = vec_a - vec_b
        assert (
            (vec_diff.x == -1.0) and (vec_diff.y == 2.0) and (vec_diff.z == 5.0)
        )

    def test_vector_scalar_product(self, Vec3: Vector3Cls) -> None:
        vec = Vec3(4.0, 8.0, 12.0)
        scale = 3.5
        vec_scaled = vec * scale
        assert (
            (vec_scaled.x == 14.0)
            and (vec_scaled.y == 28.0)
            and (vec_scaled.z == 42.0)
        )
        vec_scaled = scale * vec
        assert (
            (vec_scaled.x == 14.0)
            and (vec_scaled.y == 28.0)
            and (vec_scaled.z == 42.0)
        )

    def test_unary_negative(self, Vec3: Vector3Cls) -> None:
        vec = Vec3(3.0, 5.0, 7.0)
        vec_neg = -vec
        assert (
            (vec_neg.x == -3.0) and (vec_neg.y == -5.0) and (vec_neg.z == -7.0)
        )


@pytest.mark.parametrize("Vec3", [(m3d.Vector3f), (m3d.Vector3d)])
class TestVec3Methods:
    def test_length(self, Vec3: Vector3Cls) -> None:
        vec = Vec3(3.0, 4.0, 12.0)
        assert (np.abs(vec.norm() - 13.0) < 1e-5) and (
            np.abs(vec.squareNorm() - 169.0) < 1e-5
        )

    def test_normalize_in_place(self, Vec3: Vector3Cls) -> None:
        vec = Vec3(3.0, 4.0, 12.0)
        vec.normalize_()
        assert (
            np.abs(vec.x - 3.0 / 13.0) < 1e-5
            and np.abs(vec.y - 4.0 / 13.0) < 1e-5
            and np.abs(vec.z - 12.0 / 13.0) < 1e-5
        )

    def test_normalize(self, Vec3: Vector3Cls) -> None:
        vec = Vec3(3.0, 4.0, 12.0)
        vec_n = vec.normalize()
        assert (
            np.abs(vec_n.x - 3.0 / 13.0) < 1e-5
            and np.abs(vec_n.y - 4.0 / 13.0) < 1e-5
            and np.abs(vec_n.z - 12.0 / 13.0) < 1e-5
        )

    def test_dot_product(self, Vec3: Vector3Cls) -> None:
        vec_a = Vec3(3.0, 5.0, 7.0)
        vec_b = Vec3(11.0, 13.0, 17.0)
        assert np.abs(vec_a.dot(vec_b) - 217.0) < 1e-5

    def test_cross_product(self, Vec3: Vector3Cls) -> None:
        vec_i = Vec3(1.0, 0.0, 0.0)
        vec_j = Vec3(0.0, 1.0, 0.0)
        vec_k = Vec3(0.0, 0.0, 1.0)

        vec_a = vec_i.cross(vec_j)
        expected_a = Vec3(0.0, 0.0, 1.0)
        assert vec_a == expected_a

        vec_b = vec_j.cross(vec_k)
        expected_b = Vec3(1.0, 0.0, 0.0)
        assert vec_b == expected_b

        vec_c = vec_k.cross(vec_i)
        expected_c = Vec3(0.0, 1.0, 0.0)
        assert vec_c == expected_c


@pytest.mark.parametrize(
    "Vec3,FloatType", [(m3d.Vector3f, np.float32), (m3d.Vector3d, np.float64)]
)
def test_convert_to_numpy(Vec3: Vector3Cls, FloatType: type) -> None:
    vec3 = Vec3(1.0, 2.0, 3.0)
    np_vec3 = vec3.numpy()
    assert type(np_vec3) == np.ndarray
    assert np.allclose(np_vec3, np.array([1.0, 2.0, 3.0], dtype=FloatType))
