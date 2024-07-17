from typing import Type, Union, cast

import numpy as np
import pytest

import math3d as m3d

Matrix4Cls = Type[Union[m3d.Matrix4f, m3d.Matrix4d]]
Vector4Cls = Type[Union[m3d.Vector4f, m3d.Vector4d]]

Matrix4 = Union[m3d.Matrix4f, m3d.Matrix4d]
Vector4 = Union[m3d.Vector4f, m3d.Vector4d]

# Make sure our generators are seeded with the answer to the universe :D
np.random.seed(42)
# Number of times we will sample a random matrix for mat4 operator checks
NUM_RANDOM_SAMPLES = 10
# The delta used for tolerance (due to floating point precision mismatches)
EPSILON = 1e-5


def mat4_all_close(
    mat: Matrix4, mat_np: np.ndarray, epsilon: float = EPSILON
) -> bool:
    return np.allclose(cast(np.ndarray, mat), mat_np, atol=epsilon)


def vec2_all_close(
    vec: Vector4, vec_np: np.ndarray, epsilon: float = EPSILON
) -> bool:
    return np.allclose(cast(np.ndarray, vec), vec_np, atol=epsilon)


@pytest.mark.parametrize(
    "Mat4, FloatType", [(m3d.Matrix4f, np.float32), (m3d.Matrix4d, np.float64)]
)
def test_default_constructor(Mat4: Matrix4Cls, FloatType: type) -> None:
    mat = Mat4()
    expected_np = np.zeros((4, 4), dtype=FloatType)
    assert mat4_all_close(mat, expected_np)


@pytest.mark.parametrize(
    "Mat4, FloatType", [(m3d.Matrix4f, np.float32), (m3d.Matrix4d, np.float64)]
)
def test_diagonal_constructor(Mat4: Matrix4Cls, FloatType: type) -> None:
    mat = Mat4(1.0, 2.0, 3.0, 4.0)
    expected_np = np.diag([1.0, 2.0, 3.0, 4.0]).astype(FloatType)
    assert mat4_all_close(mat, expected_np)


@pytest.mark.parametrize(
    "Mat4, FloatType", [(m3d.Matrix4f, np.float32), (m3d.Matrix4d, np.float64)]
)
def test_all_entries_constructor(Mat4: Matrix4Cls, FloatType: type) -> None:
    # fmt: off
    mat = Mat4(1.0,  2.0,  3.0,  4.0,
               5.0,  6.0,  7.0,  8.0,
               9.0, 10.0, 11.0, 12.0,
               13.0, 14.0, 15.0, 16.0)
    expected_np = np.array([[1.0,  2.0,  3.0,  4.0],
                            [5.0,  6.0,  7.0,  8.0],
                            [9.0, 10.0, 11.0, 12.0],
                            [13.0, 14.0, 15.0, 16.0]], dtype=FloatType)
    # fmt: on
    assert mat4_all_close(mat, expected_np)


@pytest.mark.parametrize(
    "Mat4, Vec4, FloatType",
    [
        (m3d.Matrix4f, m3d.Vector4f, np.float32),
        (m3d.Matrix4d, m3d.Vector4d, np.float64),
    ],
)
def test_columns_constructor(
    Mat4: Matrix4Cls, Vec4: Vector4Cls, FloatType: type
) -> None:
    col_0 = Vec4(1.0, 5.0, 9.0, 13.0)
    col_1 = Vec4(2.0, 6.0, 10.0, 14.0)
    col_2 = Vec4(3.0, 7.0, 11.0, 15.0)
    col_3 = Vec4(4.0, 8.0, 12.0, 16.0)
    mat = Mat4(col_0, col_1, col_2, col_3)
    # fmt: off
    expected_np = np.array([[1.0,  2.0,  3.0,  4.0],
                            [5.0,  6.0,  7.0,  8.0],
                            [9.0, 10.0, 11.0, 12.0],
                            [13.0, 14.0, 15.0, 16.0]], dtype=FloatType)
    # fmt: on
    assert mat4_all_close(mat, expected_np)


@pytest.mark.parametrize(
    "Mat4, FloatType", [(m3d.Matrix4f, np.float32), (m3d.Matrix4d, np.float64)]
)
def test_numpy_array_constructor(Mat4: Matrix4Cls, FloatType: type) -> None:
    # fmt: off
    mat = Mat4(np.array([[1.0,  2.0,  3.0,  4.0],
                         [5.0,  6.0,  7.0,  8.0],
                         [9.0, 10.0, 11.0, 12.0],
                         [13.0, 14.0, 15.0, 16.0]], dtype=FloatType))
    expected_np = np.array([[1.0,  2.0,  3.0,  4.0],
                            [5.0,  6.0,  7.0,  8.0],
                            [9.0, 10.0, 11.0, 12.0],
                            [13.0, 14.0, 15.0, 16.0]], dtype=FloatType)
    # fmt: on
    assert mat4_all_close(mat, expected_np)


@pytest.mark.parametrize(
    "Mat4, Vec4, FloatType",
    [
        (m3d.Matrix4f, m3d.Vector4f, np.float32),
        (m3d.Matrix4d, m3d.Vector4d, np.float64),
    ],
)
def test_get_column(
    Mat4: Matrix4Cls, Vec4: Vector4Cls, FloatType: type
) -> None:
    # fmt: off
    mat = Mat4(1.0,  2.0,  3.0,  4.0,
               5.0,  6.0,  7.0,  8.0,
               9.0, 10.0, 11.0, 12.0,
               13.0, 14.0, 15.0, 16.0)
    # fmt: on

    # __getitem__ by using a single entry should return the requested column
    col0, col1, col2, col3 = mat[0], mat[1], mat[2], mat[3]
    assert (
        type(col0) is Vec4
        and type(col1) is Vec4
        and type(col2) is Vec4
        and type(col3) is Vec4
    )
    assert vec2_all_close(
        col0, np.array([1.0, 5.0, 9.0, 13.0], dtype=FloatType)
    )
    assert vec2_all_close(
        col1, np.array([2.0, 6.0, 10.0, 14.0], dtype=FloatType)
    )
    assert vec2_all_close(
        col2, np.array([3.0, 7.0, 11.0, 15.0], dtype=FloatType)
    )
    assert vec2_all_close(
        col3, np.array([4.0, 8.0, 12.0, 16.0], dtype=FloatType)
    )


@pytest.mark.parametrize("Mat4", [(m3d.Matrix4f), (m3d.Matrix4d)])
def test_get_entry(Mat4: Matrix4Cls) -> None:
    # fmt: off
    mat = Mat4(1.0,  2.0,  3.0,  4.0,
               5.0,  6.0,  7.0,  8.0,
               9.0, 10.0, 11.0, 12.0,
               13.0, 14.0, 15.0, 16.0)
    # fmt: on

    # __getitem__ by using a tuple to get matrix entries
    assert (
        mat[0, 0] == 1.0
        and mat[0, 1] == 2.0
        and mat[0, 2] == 3.0
        and mat[0, 3] == 4.0
    )
    assert (
        mat[1, 0] == 5.0
        and mat[1, 1] == 6.0
        and mat[1, 2] == 7.0
        and mat[1, 3] == 8.0
    )
    assert (
        mat[2, 0] == 9.0
        and mat[2, 1] == 10.0
        and mat[2, 2] == 11.0
        and mat[2, 3] == 12.0
    )
    assert (
        mat[3, 0] == 13.0
        and mat[3, 1] == 14.0
        and mat[3, 2] == 15.0
        and mat[3, 3] == 16.0
    )


@pytest.mark.parametrize(
    "Mat4, FloatType", [(m3d.Matrix4f, np.float32), (m3d.Matrix4d, np.float64)]
)
def test_set_column(Mat4: Matrix4Cls, FloatType: type) -> None:
    # fmt: off
    mat = Mat4(1.0,  2.0,  3.0,  4.0,
               5.0,  6.0,  7.0,  8.0,
               9.0, 10.0, 11.0, 12.0,
               13.0, 14.0, 15.0, 16.0)

    # __setitem__ by passing a column vector and column index
    mat[0] = np.array([1.1, 5.1, 9.1, 13.1], dtype=FloatType)
    mat[1] = np.array([2.1, 6.1, 10.1, 14.1], dtype=FloatType)
    mat[2] = np.array([3.1, 7.1, 11.1, 15.1], dtype=FloatType)
    mat[3] = np.array([4.1, 8.1, 12.1, 16.1], dtype=FloatType)
    expected_np = np.array([[1.1,  2.1,  3.1,  4.1],
                            [5.1,  6.1,  7.1,  8.1],
                            [9.1, 10.1, 11.1, 12.1],
                            [13.1, 14.1, 15.1, 16.1]], dtype=FloatType)
    # fmt: on
    assert mat4_all_close(mat, expected_np)


@pytest.mark.parametrize(
    "Mat4, FloatType", [(m3d.Matrix4f, np.float32), (m3d.Matrix4d, np.float64)]
)
def test_set_entry(Mat4: Matrix4Cls, FloatType: type) -> None:
    # fmt: off
    mat = Mat4(1.0,  2.0,  3.0,  4.0,
               5.0,  6.0,  7.0,  8.0,
               9.0, 10.0, 11.0, 12.0,
               13.0, 14.0, 15.0, 16.0)

    # __setitem__ by passing a single float and a tuple as index
    mat[0, 0], mat[0, 1], mat[0, 2], mat[0, 3] = 1.1, 2.1, 3.1, 4.1
    mat[1, 0], mat[1, 1], mat[1, 2], mat[1, 3] = 5.1, 6.1, 7.1, 8.1
    mat[2, 0], mat[2, 1], mat[2, 2], mat[2, 3] = 9.1, 10.1, 11.1, 12.1
    mat[3, 0], mat[3, 1], mat[3, 2], mat[3, 3] = 13.1, 14.1, 15.1, 16.1

    expected_np = np.array([[1.1,  2.1,  3.1,  4.1],
                            [5.1,  6.1,  7.1,  8.1],
                            [9.1, 10.1, 11.1, 12.1],
                            [13.1, 14.1, 15.1, 16.1]], dtype=FloatType)
    # fmt: on
    assert mat4_all_close(mat, expected_np)


@pytest.mark.parametrize("Mat4", [(m3d.Matrix4f), (m3d.Matrix4d)])
def test_comparison_operator(Mat4: Matrix4Cls) -> None:
    # fmt: off
    mat_a = Mat4(1.0,  2.0,  3.0,  4.0,
                 5.0,  6.0,  7.0,  8.0,
                 9.0, 10.0, 11.0, 12.0,
                 13.0, 14.0, 15.0, 16.0)
    mat_b = Mat4(1.0,  2.0,  3.0,  4.0,
                 5.0,  6.0,  7.0,  8.0,
                 9.0, 10.0, 11.0, 12.0,
                 13.0, 14.0, 15.0, 16.0)
    # fmt: on

    # Checking comparison operator (__eq__)
    assert mat_a == mat_b

    # Update the matrices so they don't match
    mat_a[0, 0], mat_b[0, 0] = 1.1, 2.1

    # Checking neg. comparison  operator (__neq__)
    assert mat_a != mat_b


@pytest.mark.parametrize(
    "Mat4, FloatType", [(m3d.Matrix4f, np.float32), (m3d.Matrix4d, np.float64)]
)
def test_matrix_addition(Mat4: Matrix4Cls, FloatType: type) -> None:
    # Testing against some hard-coded matrices
    # fmt: off
    mat_a = Mat4(1.0,  2.0,  3.0,  4.0,
                 5.0,  6.0,  7.0,  8.0,
                 9.0, 10.0, 11.0, 12.0,
                 13.0, 14.0, 15.0, 16.0)
    mat_b = Mat4(2.0,  3.0,  5.0,  7.0,
                 11.0, 13.0, 17.0, 19.0,
                 23.0, 29.0, 31.0, 37.0,
                 41.0, 43.0, 47.0, 53.0)
    mat_c = mat_a + mat_b
    expected_c = Mat4(3.0,  5.0,  8.0, 11.0,
                      16.0, 19.0, 24.0, 27.0,
                      32.0, 39.0, 42.0, 49.0,
                      54.0, 57.0, 62.0, 69.0)
    # fmt: on
    assert type(mat_c) is Mat4
    assert mat_c == expected_c

    # Testing against some randomly sampled matrices
    for _ in range(NUM_RANDOM_SAMPLES):
        np_a = np.random.randn(4, 4).astype(FloatType)
        np_b = np.random.randn(4, 4).astype(FloatType)
        np_c = np_a + np_b

        mat_a, mat_b = Mat4(np_a), Mat4(np_b)
        mat_c = mat_a + mat_b
        # Check that we're doing what numpy does for addition
        assert mat4_all_close(mat_c, np_c)


@pytest.mark.parametrize(
    "Mat4, FloatType", [(m3d.Matrix4f, np.float32), (m3d.Matrix4d, np.float64)]
)
def test_matrix_substraction(Mat4: Matrix4Cls, FloatType: type) -> None:
    # Testing against some hard-coded matrices
    # fmt: off
    mat_a = Mat4(1.0,  2.0,  3.0,  4.0,
                 5.0,  6.0,  7.0,  8.0,
                 9.0, 10.0, 11.0, 12.0,
                 13.0, 14.0, 15.0, 16.0)
    mat_b = Mat4(2.0,  3.0,  5.0,  7.0,
                 11.0, 13.0, 17.0, 19.0,
                 23.0, 29.0, 31.0, 37.0,
                 41.0, 43.0, 47.0, 53.0)
    mat_c = mat_a - mat_b
    expected_c = Mat4(-1.0,  -1.0,  -2.0,  -3.0,
                      -6.0,  -7.0, -10.0, -11.0,
                      -14.0, -19.0, -20.0, -25.0,
                      -28.0, -29.0, -32.0, -37.0)
    # fmt: on
    assert type(mat_c) is Mat4
    assert mat_c == expected_c

    # Testing against some randomly sampled matrices
    for _ in range(NUM_RANDOM_SAMPLES):
        np_a = np.random.randn(4, 4).astype(FloatType)
        np_b = np.random.randn(4, 4).astype(FloatType)
        np_c = np_a - np_b

        mat_a, mat_b = Mat4(np_a), Mat4(np_b)
        mat_c = mat_a - mat_b
        # Check that we're doing what numpy does for addition
        assert mat4_all_close(mat_c, np_c)


@pytest.mark.parametrize(
    "Mat4, FloatType", [(m3d.Matrix4f, np.float32), (m3d.Matrix4d, np.float64)]
)
def test_matrix_scalar_product(Mat4: Matrix4Cls, FloatType: type) -> None:
    # Checking against hard-coded test case
    # fmt: off
    mat = Mat4(1.0,  2.0,  3.0,  4.0,
               5.0,  6.0,  7.0,  8.0,
               9.0, 10.0, 11.0, 12.0,
               13.0, 14.0, 15.0, 16.0)
    factor = 1.5
    expected_scaled = Mat4(1.5,  3.0,  4.5,  6.0,
                           7.5,  9.0, 10.5, 12.0,
                           13.5, 15.0, 16.5, 18.0,
                           19.5, 21.0, 22.5, 24.0)
    # fmt: on

    # Checking __mul__
    scaled = mat * factor
    assert type(scaled) is Mat4
    assert scaled == expected_scaled

    # Checking __rmul__
    scaled = factor * mat
    assert type(scaled) == Mat4
    assert scaled == expected_scaled

    # Checking against some randomly sampled matrices
    for _ in range(NUM_RANDOM_SAMPLES):
        np_mat = np.random.randn(4, 4).astype(FloatType)
        factor = np.random.randn()
        mat = Mat4(np_mat)

        # Checking __mul__
        scaled = mat * factor
        np_scaled = np_mat * factor
        assert mat4_all_close(scaled, np_scaled)

        # Checking __rmul__
        scaled = factor * mat
        np_scaled = factor * np_mat
        assert mat4_all_close(scaled, np_scaled)


@pytest.mark.parametrize(
    "Mat4, Vec4, FloatType",
    [
        (m3d.Matrix4f, m3d.Vector4f, np.float32),
        (m3d.Matrix4d, m3d.Vector4d, np.float64),
    ],
)
def test_matrix_vector_product(
    Mat4: Matrix4Cls, Vec4: Vector4Cls, FloatType: type
) -> None:
    # Checking against hard-coded test case
    # fmt: off
    mat = Mat4(1.0,  2.0,  3.0,  4.0,
               5.0,  6.0,  7.0,  8.0,
               9.0, 10.0, 11.0, 12.0,
               13.0, 14.0, 15.0, 16.0)
    # fmt: on
    vec = Vec4(1.0, 2.0, 3.0, 4.0)
    prod = mat * vec
    expected_prod = Vec4(30.0, 70.0, 110.0, 150.0)
    assert type(prod) is Vec4
    assert prod == expected_prod

    # Checking against some randomly sampled matrices
    for _ in range(NUM_RANDOM_SAMPLES):
        np_mat = np.random.randn(4, 4).astype(FloatType)
        np_vec = np.random.randn(4, 1).astype(FloatType)
        mat = Mat4(np_mat)
        vec = Vec4(np_vec)

        np_prod = np_mat @ vec
        prod = mat * vec
        assert vec2_all_close(prod, np_prod)


@pytest.mark.parametrize(
    "Mat4, FloatType", [(m3d.Matrix4f, np.float32), (m3d.Matrix4d, np.float64)]
)
def test_matrix_matrix_product(Mat4: Matrix4Cls, FloatType: type) -> None:
    # Checking against hard-coded test case
    # fmt: off
    mat_a = Mat4(1.0,  2.0,  3.0,  4.0,
                 5.0,  6.0,  7.0,  8.0,
                 9.0, 10.0, 11.0, 12.0,
                 13.0, 14.0, 15.0, 16.0)
    mat_b = Mat4(2.0,  3.0,  5.0,  7.0,
                 11.0, 13.0, 17.0, 19.0,
                 23.0, 29.0, 31.0, 37.0,
                 41.0, 43.0, 47.0, 53.0)
    expected_c = Mat4(257.,  288.,  320.,  368,
                      565.,  640.,  720.,  832,
                      873.,  992., 1120., 1296,
                      1181., 1344., 1520., 1760)
    mat_c = mat_a * mat_b
    # fmt: on
    assert type(mat_c) == Mat4
    assert mat_c == expected_c

    # Checking against some randomly sampled matrices
    for _ in range(NUM_RANDOM_SAMPLES):
        np_mat_a = np.random.randn(4, 4).astype(FloatType)
        np_mat_b = np.random.randn(4, 4).astype(FloatType)
        mat_a, mat_b = Mat4(np_mat_a), Mat4(np_mat_b)

        mat_c = mat_a * mat_b
        expected_c = np_mat_a @ np_mat_b
        assert mat4_all_close(mat_c, expected_c)


@pytest.mark.parametrize(
    "Mat4, FloatType", [(m3d.Matrix4f, np.float32), (m3d.Matrix4d, np.float64)]
)
def test_matrix_transpose(Mat4: Matrix4Cls, FloatType: type) -> None:
    # Checking against a hard-coded test case
    # fmt: off
    mat = Mat4(1.0,  2.0,  3.0,  4.0,
               5.0,  6.0,  7.0,  8.0,
               9.0, 10.0, 11.0, 12.0,
               13.0, 14.0, 15.0, 16.0)
    expected_mat = Mat4(1.0, 5.0,  9.0, 13.0,
                        2.0, 6.0, 10.0, 14.0,
                        3.0, 7.0, 11.0, 15.0,
                        4.0, 8.0, 12.0, 16.0)
    # fmt: on
    mat_t = mat.transpose()
    assert type(mat_t) == Mat4
    assert mat_t == expected_mat

    # Checking against a randomly sampled matrix
    for _ in range(NUM_RANDOM_SAMPLES):
        np_mat = np.random.randn(4, 4).astype(FloatType)
        mat = Mat4(np_mat)

        mat_t = mat.transpose()
        expected_np_mat_t = np_mat.T
        assert mat4_all_close(mat_t, expected_np_mat_t)


@pytest.mark.parametrize(
    "Mat4, FloatType", [(m3d.Matrix4f, np.float32), (m3d.Matrix4d, np.float64)]
)
def test_matrix_trace(Mat4: Matrix4Cls, FloatType: type) -> None:
    # Checking against a hard-coded test case
    # fmt: off
    mat = Mat4(1.0,  2.0,  3.0,  4.0,
               5.0,  6.0,  7.0,  8.0,
               9.0, 10.0, 11.0, 12.0,
               13.0, 14.0, 15.0, 16.0)
    # fmt: on
    trace = mat.trace()
    expected_trace = 34.0
    assert type(trace) is float
    assert np.abs(trace - expected_trace) < EPSILON

    # Checking against some randomly sampled matrices
    for _ in range(NUM_RANDOM_SAMPLES):
        np_mat = np.random.randn(4, 4).astype(FloatType)
        mat = Mat4(np_mat)

        trace = mat.trace()
        expected_trace = np.trace(np_mat)
        assert np.abs(trace - expected_trace) < EPSILON


@pytest.mark.parametrize(
    "Mat4, FloatType", [(m3d.Matrix4f, np.float32), (m3d.Matrix4d, np.float64)]
)
def test_matrix_determinant(Mat4: Matrix4Cls, FloatType: type) -> None:
    # Checking against a hard-coded test case
    # fmt: off
    mat = Mat4(0.91464976,  0.55413345,  0.19333044, -0.60001319,
               0.73620611, -0.35718703, -0.69387382,  0.50825215,
               -1.83009442,  0.04651359, -2.44449474, -0.3210386,
               0.61120402, -0.93451763,  0.51492608, -0.43250595)
    # fmt: on
    det = mat.determinant()
    expected_det = -4.079931117433607
    assert type(det) is float
    assert np.abs(det - expected_det) < EPSILON

    # Checking against some randomly sampled matrices
    for _ in range(NUM_RANDOM_SAMPLES):
        np_mat = np.random.randn(4, 4).astype(FloatType)
        mat = Mat4(np_mat)

        det = mat.determinant()
        expected_det = np.linalg.det(np_mat)
        assert np.abs(det - expected_det) < EPSILON


@pytest.mark.parametrize(
    "Mat4, FloatType", [(m3d.Matrix4f, np.float32), (m3d.Matrix4d, np.float64)]
)
def test_matrix_inverse(Mat4: Matrix4Cls, FloatType: type) -> None:
    # Checking against a hard-coded test case
    # fmt: off
    mat = Mat4(0.91464976,  0.55413345,  0.19333044, -0.60001319,
               0.73620611, -0.35718703, -0.69387382,  0.50825215,
               -1.83009442,  0.04651359, -2.44449474, -0.3210386,
               0.61120402, -0.93451763,  0.51492608, -0.43250595)
    inv = mat.inverse()
    expected_inv = Mat4(0.44307324,  0.51365366, -0.09779816,  0.06153157,
                        0.45732357, -0.14613512, -0.07970549, -0.74700735,
                        -0.23821917, -0.4532605, -0.29562532,  0.01727412,
                        -0.64561897,  0.50199861, -0.3179462, -0.5905242)
    # fmt: on
    assert type(inv) is Mat4
    assert inv == expected_inv

    # Checking against some randomly sampled matrices
    for _ in range(NUM_RANDOM_SAMPLES):
        np_mat = np.random.randn(4, 4).astype(FloatType)
        mat = Mat4(np_mat)

        inv = mat.inverse()
        expected_inv = np.linalg.inv(np_mat)
        assert mat4_all_close(inv, expected_inv)
