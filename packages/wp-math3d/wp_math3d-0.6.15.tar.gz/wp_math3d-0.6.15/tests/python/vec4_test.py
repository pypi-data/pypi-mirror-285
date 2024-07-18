from typing import Type, Union

import numpy as np
import pytest

import math3d as m3d

Vector4Cls = Type[Union[m3d.Vector4f, m3d.Vector4d]]


@pytest.mark.parametrize("Vec4", [(m3d.Vector4f), (m3d.Vector4d)])
def test_vec4_attrs(Vec4: Vector4Cls):
    # Make sure we have exposed x, y, z and w as properties
    assert (
        hasattr(Vec4, "x")
        and hasattr(Vec4, "y")
        and hasattr(Vec4, "z")
        and hasattr(Vec4, "w")
    )


@pytest.mark.parametrize("Vec4", [(m3d.Vector4f), (m3d.Vector4d)])
class TestVec4Constructors:
    def test_default_constructor(self, Vec4: Vector4Cls) -> None:
        # Default constructor initializes to (0.0, 0.0, 0.0, 0.0)
        vec = Vec4()
        assert (
            (vec.x == 0.0)
            and (vec.y == 0.0)
            and (vec.z == 0.0)
            and (vec.w == 0.0)
        )

    def test_single_arg_constructor(self, Vec4: Vector4Cls) -> None:
        # Single scalar argument x initializes to (x, x, x, x)
        vec = Vec4(1.0)
        assert (
            (vec.x == 1.0)
            and (vec.y == 1.0)
            and (vec.z == 1.0)
            and (vec.w == 1.0)
        )

    def test_double_args_constructor(self, Vec4: Vector4Cls) -> None:
        # Two scalar arguments x, y initializes to (x, y, y, y)
        vec = Vec4(1.0, 2.0)
        assert (
            (vec.x == 1.0)
            and (vec.y == 2.0)
            and (vec.z == 2.0)
            and (vec.w == 2.0)
        )

    def test_triple_args_constructor(self, Vec4: Vector4Cls) -> None:
        # Three scalar arguments x, y, z initializes to (x, y, z, z)
        vec = Vec4(1.0, 2.0, 3.0)
        assert (
            (vec.x == 1.0)
            and (vec.y == 2.0)
            and (vec.z == 3.0)
            and (vec.w == 3.0)
        )

    def test_full_args_constructor(self, Vec4: Vector4Cls) -> None:
        # Three scalar arguments x, y, z, w, initializes to (v, y, z, w)
        vec = Vec4(1.0, 2.0, 3.0, 4.0)
        assert (
            (vec.x == 1.0)
            and (vec.y == 2.0)
            and (vec.z == 3.0)
            and (vec.w == 4.0)
        )


@pytest.mark.parametrize(
    "Vec4,FloatType", [(m3d.Vector4f, np.float32), (m3d.Vector4d, np.float64)]
)
def test_numpy_array_constructor(Vec4: Vector4Cls, FloatType):
    # From a numpy array (requires same dtype)
    vec_np = np.array([19.0, 23.0, 29.0, 31.0])
    vec = Vec4(vec_np.astype(FloatType))
    assert (
        (vec.x == 19.0)
        and (vec.y == 23.0)
        and (vec.z == 29.0)
        and (vec.w == 31.0)
    )

    vec = Vec4(vec_np.reshape(1, 4).astype(FloatType))
    assert (
        (vec.x == 19.0)
        and (vec.y == 23.0)
        and (vec.z == 29.0)
        and (vec.w == 31.0)
    )

    vec = Vec4(vec_np.reshape(4, 1).astype(FloatType))
    assert (
        (vec.x == 19.0)
        and (vec.y == 23.0)
        and (vec.z == 29.0)
        and (vec.w == 31.0)
    )


@pytest.mark.parametrize("Vec4", [(m3d.Vector4f), (m3d.Vector4d)])
def test_vec4_accessors(Vec4: Vector4Cls) -> None:
    # Can get x, y, z, and w as properties
    vec = Vec4(3.0, 7.0, 11.0, 13.0)
    assert (
        (vec.x == 3.0)
        and (vec.y == 7.0)
        and (vec.z == 11.0)
        and (vec.w == 13.0)
    )
    # Can get elements using __getitem__ as well
    assert (
        (vec[0] == 3.0)
        and (vec[1] == 7.0)
        and (vec[2] == 11.0)
        and (vec[3] == 13.0)
    )
    # Can also update the entries using either of the two accessors
    vec.x, vec.y, vec.z, vec.w = 1.0, 2.0, 3.0, 4.0
    assert (
        (vec.x == 1.0) and (vec.y == 2.0) and (vec.z == 3.0) and (vec.w == 4.0)
    )


@pytest.mark.parametrize("Vec4", [(m3d.Vector4f), (m3d.Vector4d)])
class TestVec4Operators:
    def test_comparison_operator(self, Vec4: Vector4Cls) -> None:
        vec_a = Vec4(1.0, 2.0, 3.0, 4.0)
        vec_b = Vec4(1.0, 2.0, 3.0, 4.0)
        # Comparison __eq__ internally calls == operator, which uses an epsilon
        assert vec_a == vec_b

        vec_b.x, vec_b.y, vec_b.z, vec_b.w = 1.1, 2.1, 3.1, 4.1
        # Comparison __neq__ internally calls != operator, which uses an epsilon
        assert vec_a != vec_b

    def test_vector_addition(self, Vec4: Vector4Cls) -> None:
        vec_a = Vec4(3.0, 7.0, 11.0, 13.0)
        vec_b = Vec4(4.0, 5.0, 6.0, 7.0)
        vec_sum = vec_a + vec_b
        assert (
            (vec_sum.x == 7.0)
            and (vec_sum.y == 12.0)
            and (vec_sum.z == 17.0)
            and (vec_sum.w == 20.0)
        )

    def test_vector_substraction(self, Vec4: Vector4Cls) -> None:
        vec_a = Vec4(3.0, 7.0, 11.0, 13.0)
        vec_b = Vec4(4.0, 5.0, 6.0, 7.0)
        vec_diff = vec_a - vec_b
        assert (
            (vec_diff.x == -1.0)
            and (vec_diff.y == 2.0)
            and (vec_diff.z == 5.0)
            and (vec_diff.w == 6.0)
        )

    def test_vector_scalar_product(self, Vec4: Vector4Cls) -> None:
        vec = Vec4(4.0, 8.0, 12.0, 16.0)
        scale = 3.5
        vec_scaled = vec * scale
        assert (
            (vec_scaled.x == 14.0)
            and (vec_scaled.y == 28.0)
            and (vec_scaled.z == 42.0)
            and (vec_scaled.w == 56.0)
        )
        vec_scaled = scale * vec
        assert (
            (vec_scaled.x == 14.0)
            and (vec_scaled.y == 28.0)
            and (vec_scaled.z == 42.0)
            and (vec_scaled.w == 56.0)
        )

    def test_unary_negative(self, Vec4: Vector4Cls) -> None:
        vec = Vec4(3.0, 5.0, 7.0, 11.0)
        vec_neg = -vec
        assert (
            (vec_neg.x == -3.0)
            and (vec_neg.y == -5.0)
            and (vec_neg.z == -7.0)
            and (vec_neg.w == -11.0)
        )


@pytest.mark.parametrize("Vec4", [(m3d.Vector4f), (m3d.Vector4d)])
class TestVec4Methods:
    def test_length(self, Vec4: Vector4Cls) -> None:
        epsilon = 1e-2
        x, y, z, w = 1.0, 2.0, 3.0, 4.0
        vec = Vec4(x, y, z, w)
        expected_norm_square = x**2 + y**2 + z**2 + w**2
        expected_norm = np.sqrt(expected_norm_square)
        assert (np.abs(vec.norm() - expected_norm) < epsilon) and (
            np.abs(vec.squareNorm() - expected_norm_square) < epsilon
        )

    def test_normalize_in_place(self, Vec4: Vector4Cls) -> None:
        EPSILON = 1e-5
        x, y, z, w = 1.0, 2.0, 3.0, 4.0
        norm = np.sqrt(x**2 + y**2 + z**2 + w**2)
        vec = Vec4(x, y, z, w)
        vec.normalize_()
        assert (
            np.abs(vec.x - x / norm) < EPSILON
            and np.abs(vec.y - y / norm) < EPSILON
            and np.abs(vec.z - z / norm) < EPSILON
            and np.abs(vec.w - w / norm) < EPSILON
        )

    def test_normalize(self, Vec4: Vector4Cls) -> None:
        EPSILON = 1e-5
        x, y, z, w = 1.0, 2.0, 3.0, 4.0
        norm = np.sqrt(x**2 + y**2 + z**2 + w**2)
        vec = Vec4(x, y, z, w)
        vec_n = vec.normalize()
        assert (
            np.abs(vec_n.x - x / norm) < EPSILON
            and np.abs(vec_n.y - y / norm) < EPSILON
            and np.abs(vec_n.z - z / norm) < EPSILON
            and np.abs(vec_n.w - w / norm) < EPSILON
        )

    def test_dot_product(self, Vec4: Vector4Cls) -> None:
        vec_a = Vec4(3.0, 5.0, 7.0, 11.0)
        vec_b = Vec4(13.0, 17.0, 19.0, 23.0)
        assert np.abs(vec_a.dot(vec_b) - 510.0) < 1e-5


@pytest.mark.parametrize(
    "Vec4,FloatType", [(m3d.Vector4f, np.float32), (m3d.Vector4d, np.float64)]
)
def test_convert_to_numpy(Vec4: Vector4Cls, FloatType: type) -> None:
    vec4 = Vec4(1.0, 2.0, 3.0, 4.0)
    np_vec4 = vec4.numpy()
    assert type(np_vec4) == np.ndarray
    assert np.allclose(np_vec4, np.array([1.0, 2.0, 3.0, 4.0], dtype=FloatType))
