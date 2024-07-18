from typing import Callable, Type, Union, cast

import numpy as np
import pytest

import math3d as m3d

QuaternionCls = Type[Union[m3d.Quaternionf, m3d.Quaterniond]]
Vector2Cls = Type[Union[m3d.Vector2f, m3d.Vector2d]]
Vector3Cls = Type[Union[m3d.Vector3f, m3d.Vector3d]]
Vector4Cls = Type[Union[m3d.Vector4f, m3d.Vector4d]]
Matrix2Cls = Type[Union[m3d.Matrix2f, m3d.Matrix2d]]
Matrix3Cls = Type[Union[m3d.Matrix3f, m3d.Matrix3d]]
Matrix4Cls = Type[Union[m3d.Matrix4f, m3d.Matrix4d]]

################################################################################
#                       Tests for math3d types to nparray                      #
################################################################################


@pytest.mark.parametrize(
    "Func,Class,Type",
    [
        (m3d.quat_to_nparray_f32, m3d.Quaternionf, np.float32),
        (m3d.quat_to_nparray_f64, m3d.Quaterniond, np.float64),
    ],
)
def test_quat_to_nparray(
    Func: Callable, Class: QuaternionCls, Type: type
) -> None:
    array_np = Func(Class(0.733, 0.462, 0.191, 0.462))
    assert array_np.dtype == Type and np.allclose(
        array_np, np.array([0.733, 0.462, 0.191, 0.462], dtype=Type)
    )


@pytest.mark.parametrize(
    "Func,Class,Type",
    [
        (m3d.vec2_to_nparray_f32, m3d.Vector2f, np.float32),
        (m3d.vec2_to_nparray_f64, m3d.Vector2d, np.float64),
    ],
)
def test_vec2_to_nparray(Func: Callable, Class: Vector2Cls, Type: type) -> None:
    array_np = Func(Class(2.0, 3.0))
    assert array_np.dtype == Type and np.allclose(
        array_np, np.array([2.0, 3.0], dtype=Type)
    )


@pytest.mark.parametrize(
    "Func,Class,Type",
    [
        (m3d.vec3_to_nparray_f32, m3d.Vector3f, np.float32),
        (m3d.vec3_to_nparray_f64, m3d.Vector3d, np.float64),
    ],
)
def test_vec3_to_nparray(Func: Callable, Class: Vector3Cls, Type: type) -> None:
    array_np = Func(Class(2.0, 3.0, 5.0))
    assert array_np.dtype == Type and np.allclose(
        array_np, np.array([2.0, 3.0, 5.0], dtype=Type)
    )


@pytest.mark.parametrize(
    "Func,Class,Type",
    [
        (m3d.vec4_to_nparray_f32, m3d.Vector4f, np.float32),
        (m3d.vec4_to_nparray_f64, m3d.Vector4d, np.float64),
    ],
)
def test_vec4_to_nparray(Func: Callable, Class: Vector4Cls, Type: type) -> None:
    array_np = Func(Class(2.0, 3.0, 5.0, 7.0))
    assert array_np.dtype == Type and np.allclose(
        array_np, np.array([2.0, 3.0, 5.0, 7.0], dtype=Type)
    )


@pytest.mark.parametrize(
    "Func,Class,Type",
    [
        (m3d.mat2_to_nparray_f32, m3d.Matrix2f, np.float32),
        (m3d.mat2_to_nparray_f64, m3d.Matrix2d, np.float64),
    ],
)
def test_mat2_to_nparray(Func: Callable, Class: Matrix2Cls, Type: type) -> None:
    # fmt: off
    array_np = Func(Class(2.0, 3.0,
                          5.0, 7.0))
    # fmt: on
    assert array_np.dtype == Type and np.allclose(
        array_np, np.array([[2.0, 3.0], [5.0, 7.0]], dtype=Type)
    )


@pytest.mark.parametrize(
    "Func,Class,Type",
    [
        (m3d.mat3_to_nparray_f32, m3d.Matrix3f, np.float32),
        (m3d.mat3_to_nparray_f64, m3d.Matrix3d, np.float64),
    ],
)
def test_mat3_to_nparray(Func: Callable, Class: Matrix3Cls, Type: type) -> None:
    # fmt: off
    array_np = Func(Class(2.0, 3.0, 5.0,
                          7.0, 11.0, 13.0,
                          17.0, 19.0, 23.0))
    # fmt: on
    assert array_np.dtype == Type and np.allclose(
        array_np,
        np.array(
            [[2.0, 3.0, 5.0], [7.0, 11.0, 13.0], [17.0, 19.0, 23.0]], dtype=Type
        ),
    )


@pytest.mark.parametrize(
    "Func,Class,Type",
    [
        (m3d.mat4_to_nparray_f32, m3d.Matrix4f, np.float32),
        (m3d.mat4_to_nparray_f64, m3d.Matrix4d, np.float64),
    ],
)
def test_mat4_to_nparray(Func: Callable, Class: Matrix4Cls, Type: type) -> None:
    # fmt: off
    array_np = Func(Class(2.0, 3.0, 5.0, 7.0,
                          11.0, 13.0, 17.0, 19.0,
                          23.0, 29.0, 31.0, 37.0,
                          41.0, 43.0, 47.0, 53.0))
    # fmt: on
    assert array_np.dtype == Type and np.allclose(
        array_np,
        np.array(
            [
                [2.0, 3.0, 5.0, 7.0],
                [11.0, 13.0, 17.0, 19.0],
                [23.0, 29.0, 31.0, 37.0],
                [41.0, 43.0, 47.0, 53.0],
            ],
            dtype=Type,
        ),
    )


################################################################################
#                       Tests for nparray to math3d types                      #
################################################################################


@pytest.mark.parametrize(
    "Func,Type",
    [
        (m3d.nparray_to_quat_f32, np.float32),
        (m3d.nparray_to_quat_f64, np.float64),
    ],
)
def test_nparray_to_quat(Func: Callable, Type: type) -> None:
    quat = Func(np.array([0.733, 0.462, 0.191, 0.462], dtype=Type))
    assert np.allclose(
        cast(np.ndarray, quat),
        np.array([0.733, 0.462, 0.191, 0.462], dtype=Type),
    )


@pytest.mark.parametrize(
    "Func,Type",
    [
        (m3d.nparray_to_vec2_f32, np.float32),
        (m3d.nparray_to_vec2_f64, np.float64),
    ],
)
def test_nparray_to_vec2(Func: Callable, Type: type) -> None:
    vec = Func(np.array([2.0, 3.0], dtype=Type))
    assert np.allclose(cast(np.ndarray, vec), np.array([2.0, 3.0], dtype=Type))


@pytest.mark.parametrize(
    "Func,Type",
    [
        (m3d.nparray_to_vec3_f32, np.float32),
        (m3d.nparray_to_vec3_f64, np.float64),
    ],
)
def test_nparray_to_vec3(Func: Callable, Type: type) -> None:
    vec = Func(np.array([2.0, 3.0, 5.0], dtype=Type))
    assert np.allclose(
        cast(np.ndarray, vec), np.array([2.0, 3.0, 5.0], dtype=Type)
    )


@pytest.mark.parametrize(
    "Func,Type",
    [
        (m3d.nparray_to_vec4_f32, np.float32),
        (m3d.nparray_to_vec4_f64, np.float64),
    ],
)
def test_nparray_to_vec4(Func: Callable, Type: type) -> None:
    vec = Func(np.array([2.0, 3.0, 5.0, 7.0], dtype=Type))
    assert np.allclose(
        cast(np.ndarray, vec), np.array([2.0, 3.0, 5.0, 7.0], dtype=Type)
    )


@pytest.mark.parametrize(
    "Func,Type",
    [
        (m3d.nparray_to_mat2_f32, np.float32),
        (m3d.nparray_to_mat2_f64, np.float64),
    ],
)
def test_nparray_to_mat2(Func: Callable, Type: type) -> None:
    mat_np = np.array([[2.0, 3.0], [5.0, 7.0]], dtype=Type)
    mat = Func(mat_np)
    assert np.allclose(cast(np.ndarray, mat), mat_np)


@pytest.mark.parametrize(
    "Func,Type",
    [
        (m3d.nparray_to_mat3_f32, np.float32),
        (m3d.nparray_to_mat3_f64, np.float64),
    ],
)
def test_nparray_to_mat3(Func: Callable, Type: type) -> None:
    mat_np = np.array(
        [[2.0, 3.0, 5.0], [7.0, 11.0, 13.0], [17.0, 19.0, 23.0]], dtype=Type
    )
    mat = Func(mat_np)
    assert np.allclose(cast(np.ndarray, mat), mat_np)


@pytest.mark.parametrize(
    "Func,Type",
    [
        (m3d.nparray_to_mat4_f32, np.float32),
        (m3d.nparray_to_mat4_f64, np.float64),
    ],
)
def test_nparray_to_mat4(Func: Callable, Type: type) -> None:
    mat_np = np.array(
        [
            [2.0, 3.0, 5.0, 7.0],
            [11.0, 13.0, 17.0, 19.0],
            [23.0, 29.0, 31.0, 37.0],
            [41.0, 43.0, 47.0, 53.0],
        ],
        dtype=Type,
    )
    mat = Func(mat_np)
    assert np.allclose(cast(np.ndarray, mat), mat_np)
