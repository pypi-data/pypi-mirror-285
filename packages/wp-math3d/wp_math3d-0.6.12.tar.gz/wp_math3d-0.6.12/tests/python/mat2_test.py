from typing import Type, Union, cast

import numpy as np
import pytest

import math3d as m3d

Matrix2Cls = Type[Union[m3d.Matrix2f, m3d.Matrix2d]]
Vector2Cls = Type[Union[m3d.Vector2f, m3d.Vector2d]]

Matrix2 = Union[m3d.Matrix2f, m3d.Matrix2d]
Vector2 = Union[m3d.Vector2f, m3d.Vector2d]

# Make sure our generators are seeded with the answer to the universe :D
np.random.seed(42)
# Number of times we will sample a random matrix for mat2 operator checks
NUM_RANDOM_SAMPLES = 10
# The delta used for tolerance (due to floating point precision mismatches)
EPSILON = 1e-5


def mat2_all_close(
    mat: Matrix2, mat_np: np.ndarray, epsilon: float = EPSILON
) -> bool:
    return np.allclose(cast(np.ndarray, mat), mat_np, atol=epsilon)


def vec2_all_close(
    vec: Vector2, vec_np: np.ndarray, epsilon: float = EPSILON
) -> bool:
    return np.allclose(cast(np.ndarray, vec), vec_np, atol=epsilon)


@pytest.mark.parametrize(
    "Mat2, FloatType", [(m3d.Matrix2f, np.float32), (m3d.Matrix2d, np.float64)]
)
def test_default_constructor(Mat2: Matrix2Cls, FloatType: type) -> None:
    mat = Mat2()
    expected_np = np.zeros((2, 2), dtype=FloatType)
    assert mat2_all_close(mat, expected_np)


@pytest.mark.parametrize(
    "Mat2, FloatType", [(m3d.Matrix2f, np.float32), (m3d.Matrix2d, np.float64)]
)
def test_diagonal_constructor(Mat2: Matrix2Cls, FloatType: type) -> None:
    mat = Mat2(1.0, 2.0)
    expected_np = np.diag([1.0, 2.0]).astype(FloatType)
    assert mat2_all_close(mat, expected_np)


@pytest.mark.parametrize(
    "Mat2, FloatType", [(m3d.Matrix2f, np.float32), (m3d.Matrix2d, np.float64)]
)
def test_all_entries_constructor(Mat2: Matrix2Cls, FloatType: type) -> None:
    # fmt: off
    mat = Mat2(1.0, 2.0,
               3.0, 4.0)
    expected_np = np.array([[1.0, 2.0],
                            [3.0, 4.0]], dtype=FloatType)
    # fmt: on
    assert mat2_all_close(mat, expected_np)


@pytest.mark.parametrize(
    "Mat2, Vec2, FloatType",
    [
        (m3d.Matrix2f, m3d.Vector2f, np.float32),
        (m3d.Matrix2d, m3d.Vector2d, np.float64),
    ],
)
def test_columns_constructor(
    Mat2: Matrix2Cls, Vec2: Vector2Cls, FloatType: type
) -> None:
    col_0 = Vec2(1.0, 3.0)
    col_1 = Vec2(2.0, 4.0)
    mat = Mat2(col_0, col_1)
    # fmt: off
    expected_np = np.array([[1.0, 2.0],
                            [3.0, 4.0]], dtype=FloatType)
    # fmt: on
    assert mat2_all_close(mat, expected_np)


@pytest.mark.parametrize(
    "Mat2, FloatType", [(m3d.Matrix2f, np.float32), (m3d.Matrix2d, np.float64)]
)
def test_numpy_array_constructor(Mat2: Matrix2Cls, FloatType: type) -> None:
    # fmt: off
    mat = Mat2(np.array([[1.0, 2.0],
                         [3.0, 4.0]], dtype=FloatType))
    expected_np = np.array([[1.0, 2.0],
                            [3.0, 4.0]], dtype=FloatType)
    # fmt: on
    assert mat2_all_close(mat, expected_np)


@pytest.mark.parametrize(
    "Mat2, Vec2, FloatType",
    [
        (m3d.Matrix2f, m3d.Vector2f, np.float32),
        (m3d.Matrix2d, m3d.Vector2d, np.float64),
    ],
)
def test_get_column(
    Mat2: Matrix2Cls, Vec2: Vector2Cls, FloatType: type
) -> None:
    # fmt: off
    mat = Mat2(1.0, 2.0,
               3.0, 4.0)
    # fmt: on

    # __getitem__ by using a single entry should return the requested column
    col0, col1 = mat[0], mat[1]
    assert type(col0) == Vec2 and type(col1) == Vec2
    assert vec2_all_close(col0, np.array([1.0, 3.0], dtype=FloatType))
    assert vec2_all_close(col1, np.array([2.0, 4.0], dtype=FloatType))


@pytest.mark.parametrize("Mat2", [(m3d.Matrix2f), (m3d.Matrix2d)])
def test_get_entry(Mat2: Matrix2Cls) -> None:
    # fmt: off
    mat = Mat2(1.0, 2.0,
               3.0, 4.0)
    # fmt: on

    # __getitem__ by using a tuple to get matrix entries
    assert mat[0, 0] == 1.0 and mat[0, 1] == 2.0
    assert mat[1, 0] == 3.0 and mat[1, 1] == 4.0


@pytest.mark.parametrize(
    "Mat2, FloatType", [(m3d.Matrix2f, np.float32), (m3d.Matrix2d, np.float64)]
)
def test_set_column(Mat2: Matrix2Cls, FloatType: type) -> None:
    # fmt: off
    mat = Mat2(1.0, 2.0,
               3.0, 4.0)

    # __setitem__ by passing a column vector and column index
    mat[0] = np.array([1.1, 3.1], dtype=FloatType)
    mat[1] = np.array([2.1, 4.1], dtype=FloatType)
    expected_np = np.array([[1.1, 2.1],
                            [3.1, 4.1]], dtype=FloatType)
    # fmt: on
    assert mat2_all_close(mat, expected_np)


@pytest.mark.parametrize(
    "Mat2, FloatType", [(m3d.Matrix2f, np.float32), (m3d.Matrix2d, np.float64)]
)
def test_set_entry(Mat2: Matrix2Cls, FloatType: type) -> None:
    # fmt: off
    mat = Mat2(1.0, 2.0,
               3.0, 4.0)

    # __setitem__ by passing a single float and a tuple as index
    mat[0, 0], mat[0, 1] = 1.1, 2.1
    mat[1, 0], mat[1, 1] = 3.1, 4.1

    expected_np = np.array([[1.1, 2.1],
                            [3.1, 4.1]], dtype=FloatType)
    # fmt: on
    assert mat2_all_close(mat, expected_np)


@pytest.mark.parametrize("Mat2", [(m3d.Matrix2f), (m3d.Matrix2d)])
def test_comparison_operator(Mat2: Matrix2Cls) -> None:
    # fmt: off
    mat_a = Mat2(1.0, 2.0,
                 3.0, 4.0)
    mat_b = Mat2(1.0, 2.0,
                 3.0, 4.0)
    # fmt: on

    # Checking comparison operator (__eq__)
    assert mat_a == mat_b

    # Update the matrices so they don't match
    mat_a[0, 0], mat_b[0, 0] = 1.1, 2.1

    # Checking neg. comparison  operator (__neq__)
    assert mat_a != mat_b


@pytest.mark.parametrize(
    "Mat2, FloatType", [(m3d.Matrix2f, np.float32), (m3d.Matrix2d, np.float64)]
)
def test_matrix_addition(Mat2: Matrix2Cls, FloatType: type) -> None:
    # Testing against some hard-coded matrices
    # fmt: off
    mat_a = Mat2(1.0, 2.0,
                 3.0, 4.0)
    mat_b = Mat2(2.0, 3.0,
                 5.0, 7.0)
    mat_c = mat_a + mat_b
    expected_c = Mat2(3.0, 5.0,
                      8.0, 11.0)
    # fmt: on
    assert type(mat_c) is Mat2
    assert mat_c == expected_c

    # Testing against some randomly sampled matrices
    for _ in range(NUM_RANDOM_SAMPLES):
        np_a = np.random.randn(2, 2).astype(FloatType)
        np_b = np.random.randn(2, 2).astype(FloatType)
        np_c = np_a + np_b

        mat_a, mat_b = Mat2(np_a), Mat2(np_b)
        mat_c = mat_a + mat_b
        # Check that we're doing what numpy does for addition
        assert mat2_all_close(mat_c, np_c)


@pytest.mark.parametrize(
    "Mat2, FloatType", [(m3d.Matrix2f, np.float32), (m3d.Matrix2d, np.float64)]
)
def test_matrix_substraction(Mat2: Matrix2Cls, FloatType: type) -> None:
    # Testing against some hard-coded matrices
    # fmt: off
    mat_a = Mat2(1.0, 2.0,
                 3.0, 4.0)
    mat_b = Mat2(2.0, 3.0,
                 5.0, 7.0)
    mat_c = mat_a - mat_b
    expected_c = Mat2(-1.0, -1.0,
                      -2.0, -3.0)
    # fmt: on
    assert type(mat_c) is Mat2
    assert mat_c == expected_c

    # Testing against some randomly sampled matrices
    for _ in range(NUM_RANDOM_SAMPLES):
        np_a = np.random.randn(2, 2).astype(FloatType)
        np_b = np.random.randn(2, 2).astype(FloatType)
        np_c = np_a - np_b

        mat_a, mat_b = Mat2(np_a), Mat2(np_b)
        mat_c = mat_a - mat_b
        # Check that we're doing what numpy does for addition
        assert mat2_all_close(mat_c, np_c)


@pytest.mark.parametrize(
    "Mat2, FloatType", [(m3d.Matrix2f, np.float32), (m3d.Matrix2d, np.float64)]
)
def test_matrix_scalar_product(Mat2: Matrix2Cls, FloatType: type) -> None:
    # Checking against hard-coded test case
    # fmt: off
    mat = Mat2(1.0, 2.0,
               3.0, 4.0)
    factor = 1.5
    expected_scaled = Mat2(1.5, 3.0,
                           4.5, 6.0)
    # fmt: on

    # Checking __mul__
    scaled = mat * factor
    assert type(scaled) is Mat2
    assert scaled == expected_scaled

    # Checking __rmul__
    scaled = factor * mat
    assert type(scaled) == Mat2
    assert scaled == expected_scaled

    # Checking against some randomly sampled matrices
    for _ in range(NUM_RANDOM_SAMPLES):
        np_mat = np.random.randn(2, 2).astype(FloatType)
        factor = np.random.randn()
        mat = Mat2(np_mat)

        # Checking __mul__
        scaled = mat * factor
        np_scaled = np_mat * factor
        assert mat2_all_close(scaled, np_scaled)

        # Checking __rmul__
        scaled = factor * mat
        np_scaled = factor * np_mat
        assert mat2_all_close(scaled, np_scaled)


@pytest.mark.parametrize(
    "Mat2, Vec2, FloatType",
    [
        (m3d.Matrix2f, m3d.Vector2f, np.float32),
        (m3d.Matrix2d, m3d.Vector2d, np.float64),
    ],
)
def test_matrix_vector_product(
    Mat2: Matrix2Cls, Vec2: Vector2Cls, FloatType: type
) -> None:
    # Checking against hard-coded test case
    # fmt: off
    mat = Mat2(1.0, 2.0,
               3.0, 4.0)
    # fmt: on
    vec = Vec2(1.0, 2.0)
    prod = mat * vec
    expected_prod = Vec2(5.0, 11.0)
    assert type(prod) is Vec2
    assert prod == expected_prod

    # Checking against some randomly sampled matrices
    for _ in range(NUM_RANDOM_SAMPLES):
        np_mat = np.random.randn(2, 2).astype(FloatType)
        np_vec = np.random.randn(2, 1).astype(FloatType)
        mat = Mat2(np_mat)
        vec = Vec2(np_vec)

        np_prod = np_mat @ vec
        prod = mat * vec
        assert vec2_all_close(prod, np_prod)


@pytest.mark.parametrize(
    "Mat2, FloatType", [(m3d.Matrix2f, np.float32), (m3d.Matrix2d, np.float64)]
)
def test_matrix_matrix_product(Mat2: Matrix2Cls, FloatType: type) -> None:
    # Checking against hard-coded test case
    # fmt: off
    mat_a = Mat2(1.0, 2.0,
                 3.0, 4.0)
    mat_b = Mat2(5.0, 6.0,
                 7.0, 8.0)
    expected_c = Mat2(19.0, 22.0,
                      43.0, 50.0)
    mat_c = mat_a * mat_b
    # fmt: on
    assert type(mat_c) == Mat2
    assert mat_c == expected_c

    # Checking against some randomly sampled matrices
    for _ in range(NUM_RANDOM_SAMPLES):
        np_mat_a = np.random.randn(2, 2).astype(FloatType)
        np_mat_b = np.random.randn(2, 2).astype(FloatType)
        mat_a, mat_b = Mat2(np_mat_a), Mat2(np_mat_b)

        mat_c = mat_a * mat_b
        expected_c = np_mat_a @ np_mat_b
        assert mat2_all_close(mat_c, expected_c)


@pytest.mark.parametrize(
    "Mat2, FloatType", [(m3d.Matrix2f, np.float32), (m3d.Matrix2d, np.float64)]
)
def test_matrix_transpose(Mat2: Matrix2Cls, FloatType: type) -> None:
    # Checking against a hard-coded test case
    # fmt: off
    mat = Mat2(1.0, 2.0,
               3.0, 4.0)
    expected_mat = Mat2(1.0, 3.0,
                        2.0, 4.0)
    # fmt: on
    mat_t = mat.transpose()
    assert type(mat_t) == Mat2
    assert mat_t == expected_mat

    # Checking against a randomly sampled matrix
    for _ in range(NUM_RANDOM_SAMPLES):
        np_mat = np.random.randn(2, 2).astype(FloatType)
        mat = Mat2(np_mat)

        mat_t = mat.transpose()
        expected_np_mat_t = np_mat.T
        assert mat2_all_close(mat_t, expected_np_mat_t)


@pytest.mark.parametrize(
    "Mat2, FloatType", [(m3d.Matrix2f, np.float32), (m3d.Matrix2d, np.float64)]
)
def test_matrix_trace(Mat2: Matrix2Cls, FloatType: type) -> None:
    # Checking against a hard-coded test case
    # fmt: off
    mat = Mat2(1.0, 2.0,
               3.0, 4.0)
    # fmt: on
    trace = mat.trace()
    expected_trace = 5.0
    assert type(trace) is float
    assert np.abs(trace - expected_trace) < EPSILON

    # Checking against some randomly sampled matrices
    for _ in range(NUM_RANDOM_SAMPLES):
        np_mat = np.random.randn(2, 2).astype(FloatType)
        mat = Mat2(np_mat)

        trace = mat.trace()
        expected_trace = np.trace(np_mat)
        assert np.abs(trace - expected_trace) < EPSILON


@pytest.mark.parametrize(
    "Mat2, FloatType", [(m3d.Matrix2f, np.float32), (m3d.Matrix2d, np.float64)]
)
def test_matrix_determinant(Mat2: Matrix2Cls, FloatType: type) -> None:
    # Checking against a hard-coded test case
    # fmt: off
    mat = Mat2(0.27958992, -2.56058477,
               -0.40810265, -1.03088155)
    # fmt: on
    det = mat.determinant()
    expected_det = -1.3332055294650407
    assert type(det) is float
    assert np.abs(det - expected_det) < EPSILON

    # Checking against some randomly sampled matrices
    for _ in range(NUM_RANDOM_SAMPLES):
        np_mat = np.random.randn(2, 2).astype(FloatType)
        mat = Mat2(np_mat)

        det = mat.determinant()
        expected_det = np.linalg.det(np_mat)
        assert np.abs(det - expected_det) < EPSILON


@pytest.mark.parametrize(
    "Mat2, FloatType", [(m3d.Matrix2f, np.float32), (m3d.Matrix2d, np.float64)]
)
def test_matrix_inverse(Mat2: Matrix2Cls, FloatType: type) -> None:
    # Checking against a hard-coded test case
    # fmt: off
    mat = Mat2(0.27958992, -2.56058477,
               -0.40810265, -1.03088155)
    inv = mat.inverse()
    expected_inv = Mat2(0.77323528, -1.92062268,
                        -0.30610633, -0.20971254)
    # fmt: on
    assert type(inv) is Mat2
    assert inv == expected_inv

    # Checking against some randomly sampled matrices
    for _ in range(NUM_RANDOM_SAMPLES):
        np_mat = np.random.randn(2, 2).astype(FloatType)
        mat = Mat2(np_mat)

        inv = mat.inverse()
        expected_inv = np.linalg.inv(np_mat)
        assert mat2_all_close(inv, expected_inv)
