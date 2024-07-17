from typing import Type, Union, cast

import numpy as np
import pytest

import math3d as m3d

Matrix3Cls = Type[Union[m3d.Matrix3f, m3d.Matrix3d]]
Vector3Cls = Type[Union[m3d.Vector3f, m3d.Vector3d]]

Matrix3 = Union[m3d.Matrix3f, m3d.Matrix3d]
Vector3 = Union[m3d.Vector3f, m3d.Vector3d]

# Make sure our generators are seeded with the answer to the universe :D
np.random.seed(42)
# Number of times we will sample a random matrix for mat3 operator checks
NUM_RANDOM_SAMPLES = 10
# The delta used for tolerance (due to floating point precision mismatches)
EPSILON = 1e-5


def mat3_all_close(
    mat: Matrix3, mat_np: np.ndarray, epsilon: float = EPSILON
) -> bool:
    return np.allclose(cast(np.ndarray, mat), mat_np, atol=epsilon)


def vec3_all_close(
    vec: Vector3, vec_np: np.ndarray, epsilon: float = EPSILON
) -> bool:
    return np.allclose(cast(np.ndarray, vec), vec_np, atol=epsilon)


@pytest.mark.parametrize(
    "Mat3, FloatType", [(m3d.Matrix3f, np.float32), (m3d.Matrix3d, np.float64)]
)
def test_default_constructor(Mat3: Matrix3Cls, FloatType: type) -> None:
    mat = Mat3()
    assert mat3_all_close(mat, np.zeros((3, 3), dtype=FloatType))


@pytest.mark.parametrize(
    "Mat3, FloatType", [(m3d.Matrix3f, np.float32), (m3d.Matrix3d, np.float64)]
)
def test_diagonal_constructor(Mat3: Matrix3Cls, FloatType: type) -> None:
    mat = Mat3(1.0, 2.0, 3.0)
    assert mat3_all_close(mat, np.diag([1.0, 2.0, 3.0]).astype(FloatType))


@pytest.mark.parametrize(
    "Mat3, FloatType", [(m3d.Matrix3f, np.float32), (m3d.Matrix3d, np.float64)]
)
def test_all_entries_constructor(Mat3: Matrix3Cls, FloatType: type) -> None:
    mat = Mat3(1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0)
    assert mat3_all_close(mat, np.arange(1, 10).reshape(3, 3).astype(FloatType))


@pytest.mark.parametrize(
    "Mat3, Vec3, FloatType",
    [
        (m3d.Matrix3f, m3d.Vector3f, np.float32),
        (m3d.Matrix3d, m3d.Vector3d, np.float64),
    ],
)
def test_columns_constructor(
    Mat3: Matrix3Cls, Vec3: Vector3Cls, FloatType: type
) -> None:
    col_0 = Vec3(1.0, 4.0, 7.0)
    col_1 = Vec3(2.0, 5.0, 8.0)
    col_2 = Vec3(3.0, 6.0, 9.0)
    mat = Mat3(col_0, col_1, col_2)
    assert mat3_all_close(mat, np.arange(1, 10).reshape(3, 3).astype(FloatType))


@pytest.mark.parametrize(
    "Mat3, FloatType", [(m3d.Matrix3f, np.float32), (m3d.Matrix3d, np.float64)]
)
def test_numpy_array_constructor(Mat3: Matrix3Cls, FloatType: type) -> None:
    mat = Mat3(
        np.array(
            [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]],
            dtype=FloatType,
        )
    )
    assert mat3_all_close(mat, np.arange(1, 10).reshape(3, 3).astype(FloatType))


@pytest.mark.parametrize(
    "Mat3, Vec3, FloatType",
    [
        (m3d.Matrix3f, m3d.Vector3f, np.float32),
        (m3d.Matrix3d, m3d.Vector3d, np.float64),
    ],
)
def test_mat3_accessors(Mat3, Vec3, FloatType) -> None:
    mat = Mat3(
        np.array(
            [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]], dtype=FloatType
        )
    )

    # __getitem__ by using a single entry should return the requested column
    col0, col1, col2 = mat[0], mat[1], mat[2]
    assert type(col0) == Vec3 and type(col1) == Vec3 and type(col2) == Vec3
    assert vec3_all_close(col0, np.array([1.0, 4.0, 7.0], dtype=FloatType))
    assert vec3_all_close(col1, np.array([2.0, 5.0, 8.0], dtype=FloatType))
    assert vec3_all_close(col2, np.array([3.0, 6.0, 9.0], dtype=FloatType))

    # __getitem__ by using a tuple
    assert mat[0, 0] == 1.0 and mat[0, 1] == 2.0 and mat[0, 2] == 3.0
    assert mat[1, 0] == 4.0 and mat[1, 1] == 5.0 and mat[1, 2] == 6.0
    assert mat[2, 0] == 7.0 and mat[2, 1] == 8.0 and mat[2, 2] == 9.0

    # __getitem__ by using a slice
    # TODO(wilbert): impl. __getitem__ to retrieve a slice-view of the vector


@pytest.mark.parametrize(
    "Mat3, FloatType", [(m3d.Matrix3f, np.float32), (m3d.Matrix3d, np.float64)]
)
def test_comparison_operator(Mat3: Matrix3Cls, FloatType: type) -> None:
    mat_a = Mat3(np.arange(1, 10).reshape(3, 3).astype(FloatType))
    mat_b = Mat3(np.arange(1, 10).reshape(3, 3).astype(FloatType))

    # Checking comparison operator (__eq__)
    assert mat_a == mat_b

    # Update the matrices so they don't match
    mat_a[0, 0], mat_b[0, 0] = 1.1, 2.1

    # Checking neg. comparison  operator (__neq__)
    assert mat_a != mat_b


@pytest.mark.parametrize(
    "Mat3, FloatType", [(m3d.Matrix3f, np.float32), (m3d.Matrix3d, np.float64)]
)
def test_matrix_addition(Mat3: Matrix3Cls, FloatType: type) -> None:
    # Testing against some hardcoded matrices
    np_a = np.array(
        [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]], dtype=FloatType
    )
    np_b = np.array(
        [[2.0, 3.0, 5.0], [7.0, 11.0, 13.0], [17.0, 19.0, 23.0]],
        dtype=FloatType,
    )
    np_c = np_a + np_b

    mat_a, mat_b = Mat3(np_a), Mat3(np_b)
    mat_c = mat_a + mat_b
    # Check that we're doing what numpy does for addition
    assert mat3_all_close(mat_c, np_c)

    # Testing against randomly sampled matrices
    for i in range(NUM_RANDOM_SAMPLES):  # pyright: ignore
        np_a = np.random.randn(3, 3).astype(FloatType)
        np_b = np.random.randn(3, 3).astype(FloatType)
        np_c = np_a + np_b

        mat_a, mat_b = Mat3(np_a), Mat3(np_b)
        mat_c = mat_a + mat_b
        # Check that we're doing what numpy does for addition
        assert mat3_all_close(mat_c, np_c)


@pytest.mark.parametrize(
    "Mat3, FloatType", [(m3d.Matrix3f, np.float32), (m3d.Matrix3d, np.float64)]
)
def test_matrix_substraction(Mat3: Matrix3Cls, FloatType: type) -> None:
    # Testing against some hardcoded matrices
    np_a = np.array(
        [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]], dtype=FloatType
    )
    np_b = np.array(
        [[2.0, 3.0, 5.0], [7.0, 11.0, 13.0], [17.0, 19.0, 23.0]],
        dtype=FloatType,
    )
    np_c = np_a - np_b

    mat_a, mat_b = Mat3(np_a), Mat3(np_b)
    mat_c = mat_a - mat_b
    # Check that we're doing what numpy does for substraction
    assert mat3_all_close(mat_c, np_c)

    # Testing against randomly sampled matrices
    for i in range(NUM_RANDOM_SAMPLES):  # pyright: ignore
        np_a = np.random.randn(3, 3).astype(FloatType)
        np_b = np.random.randn(3, 3).astype(FloatType)
        np_c = np_a - np_b

        mat_a, mat_b = Mat3(np_a), Mat3(np_b)
        mat_c = mat_a - mat_b
        # Check that we're doing what numpy does for addition
        assert mat3_all_close(mat_c, np_c)


@pytest.mark.parametrize(
    "Mat3, FloatType", [(m3d.Matrix3f, np.float32), (m3d.Matrix3d, np.float64)]
)
def test_matrix_scalar_product(Mat3: Matrix3Cls, FloatType: type) -> None:
    # Checking against hard coded test case
    np_mat = np.arange(1, 10).reshape(3, 3).astype(FloatType)
    factor = 1.5
    mat = Mat3(np_mat)

    # Checking __mul__
    s_mat = mat * factor  # Math3d land
    s_np_mat = np_mat * factor  # Numpy land
    assert type(s_mat) == Mat3
    assert mat3_all_close(s_mat, s_np_mat)

    # Checking __rmul__
    s_mat = factor * mat  # Math3d land
    s_np_mat = factor * np_mat  # Numpy
    assert type(s_mat) == Mat3
    assert mat3_all_close(s_mat, s_np_mat)

    # Checking against a randomly sampled matrix
    for i in range(NUM_RANDOM_SAMPLES):  # pyright: ignore
        np_mat = np.random.randn(3, 3).astype(FloatType)
        factor = np.random.randn()
        mat = Mat3(np_mat)

        # Checking __mul__
        s_mat = mat * factor
        s_np_mat = np_mat * factor
        assert type(s_mat) == Mat3
        assert mat3_all_close(s_mat, s_np_mat)

        # Checking __rmul__
        s_mat = factor * mat
        assert type(s_mat) == Mat3
        assert mat3_all_close(s_mat, s_np_mat)


@pytest.mark.parametrize(
    "Mat3, Vec3, FloatType",
    [
        (m3d.Matrix3f, m3d.Vector3f, np.float32),
        (m3d.Matrix3d, m3d.Vector3d, np.float64),
    ],
)
def test_matrix_vector_product(
    Mat3: Matrix3Cls, Vec3: Vector3Cls, FloatType: type
) -> None:
    # Checking against hard-coded test case
    # fmt: off
    mat = Mat3(1.0, -4.0, 1.0,
               -6.0, -7.0, 9.0,
               -4.0,  6.0, 0.0)
    # fmt: on
    vec = Vec3(2.0, 7.0, 6.0)

    n_vec = mat * vec

    assert vec3_all_close(n_vec, np.array([-20.0, -7.0, 34.0]))

    # Checking against a randomly sampled matrix
    for _ in range(NUM_RANDOM_SAMPLES):
        np_mat = np.random.randn(3, 3).astype(FloatType)
        np_vec = np.random.randn(3, 1).astype(FloatType)
        mat = Mat3(np_mat)
        vec = Vec3(np_vec)

        np_prod = np_mat @ vec
        prod = mat * vec
        assert type(prod) == Vec3
        assert vec3_all_close(prod, np_prod)


@pytest.mark.parametrize(
    "Mat3, FloatType", [(m3d.Matrix3f, np.float32), (m3d.Matrix3d, np.float64)]
)
def test_matrix_matrix_product(Mat3: Matrix3Cls, FloatType: type) -> None:
    # Checking against hard-coded test case
    # fmt: off
    mat_a = Mat3(-10.0, -10.0, -2.0,
                 -8.0,  -8.0,  1.0,
                 5.0,  -7.0, -3.0)

    mat_b = Mat3(-1.0, -1.0,  8.0,
                 6.0,  6.0,  0.0,
                 -8.0,  2.0, -9.0)
    mat_c = mat_a * mat_b
    expected_c = np.array([[-34.0, -54.0, -62.0],
                           [-48.0, -38.0, -73.0],
                           [-23.0, -53.0,  67.0]], dtype=FloatType)
    # fmt: on
    assert type(mat_c) == Mat3
    assert mat3_all_close(mat_c, expected_c)

    # Checking against a randomly sampled matrix
    for i in range(NUM_RANDOM_SAMPLES):  # pyright: ignore
        np_mat_a = np.random.randn(3, 3).astype(FloatType)
        np_mat_b = np.random.randn(3, 3).astype(FloatType)
        mat_a, mat_b = Mat3(np_mat_a), Mat3(np_mat_b)

        mat_c = mat_a * mat_b
        expected_c = np_mat_a @ np_mat_b
        assert mat3_all_close(mat_c, expected_c)


@pytest.mark.parametrize(
    "Mat3, FloatType",
    [
        (m3d.Matrix3f, np.float32),
        (m3d.Matrix3d, np.float64),
    ],
)
class TestMat3Methods:
    def test_matrix_transpose(self, Mat3: Matrix3Cls, FloatType: type) -> None:
        # Checking against a hard-coded test case
        # fmt: off
        mat = Mat3(1.0, 2.0, 3.0,
                   4.0, 5.0, 6.0,
                   7.0, 8.0, 9.0)
        expected_mat = Mat3(1.0, 4.0, 7.0,
                            2.0, 5.0, 8.0,
                            3.0, 6.0, 9.0)
        # fmt: on
        mat_t = mat.transpose()
        assert type(mat_t) == Mat3
        assert mat_t == expected_mat

        # Checking against a randomly sampled matrix
        for _ in range(NUM_RANDOM_SAMPLES):
            np_mat = np.random.randn(3, 3).astype(FloatType)
            mat = Mat3(np_mat)

            mat_t = mat.transpose()
            expected_np_mat_t = np_mat.T
            assert mat3_all_close(mat_t, expected_np_mat_t)

    def test_matrix_trace(self, Mat3: Matrix3Cls, FloatType: type) -> None:
        # Checking against a hard-coded test case
        # fmt: off
        mat = Mat3(1.0, 2.0, 3.0,
                   4.0, 5.0, 6.0,
                   7.0, 8.0, 9.0)
        # fmt: on
        trace = mat.trace()
        expected_trace = 15.0
        assert type(trace) is float
        assert np.abs(trace - expected_trace) < EPSILON

        # Checking against some randomly sampled matrices
        for _ in range(NUM_RANDOM_SAMPLES):
            np_mat = np.random.randn(3, 3).astype(FloatType)
            mat = Mat3(np_mat)

            trace = mat.trace()
            expected_trace = np.trace(np_mat)
            assert np.abs(trace - expected_trace) < EPSILON

    def test_matrix_determinant(
        self, Mat3: Matrix3Cls, FloatType: type
    ) -> None:
        # Checking against a hard-coded test case
        # fmt: off
        mat = Mat3(0.50130818,  0.3485203, -0.73158798,
                   0.11190553, -0.78547367, -0.83114009,
                   -1.89185312, -1.26867963,  1.98250988)
        # fmt: on
        det = mat.determinant()
        expected_det = 0.3524501163395751
        assert type(det) is float
        assert np.abs(det - expected_det) < EPSILON

        # Checking against some randomly sampled matrices
        for _ in range(NUM_RANDOM_SAMPLES):
            np_mat = np.random.randn(3, 3).astype(FloatType)
            mat = Mat3(np_mat)

            det = mat.determinant()
            expected_det = np.linalg.det(np_mat)
            assert np.abs(det - expected_det) < EPSILON

    def test_matrix_inverse(self, Mat3: Matrix3Cls, FloatType: type) -> None:
        # Checking against a hard-coded test case
        # fmt: off
        mat = Mat3(0.50130818,  0.3485203, -0.73158798,
                   0.11190553, -0.78547367, -0.83114009,
                   -1.89185312, -1.26867963,  1.98250988)
        inv = mat.inverse()
        expected_inv = np.array([[-7.41001263,  0.67301955, -2.45229678],
                                 [3.83186468, -1.10713136,  0.94988927],
                                 [-4.61901701, -0.06624979, -1.22787794]],
                                dtype=FloatType)
        # fmt: on
        assert type(inv) is Mat3
        assert mat3_all_close(inv, expected_inv)

        # Checking against some randomly sampled matrices
        for _ in range(NUM_RANDOM_SAMPLES):
            np_mat = np.random.randn(3, 3).astype(FloatType)
            mat = Mat3(np_mat)

            inv = mat.inverse()
            expected_inv = np.linalg.inv(np_mat)
            assert mat3_all_close(inv, expected_inv)
