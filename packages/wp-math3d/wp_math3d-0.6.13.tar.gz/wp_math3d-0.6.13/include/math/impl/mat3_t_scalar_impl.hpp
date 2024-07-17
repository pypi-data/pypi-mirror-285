#pragma once

#include <cmath>
#include <utility>

#include <math/mat3_t_decl.hpp>

namespace math {
namespace scalar {

template <typename T>
using Mat3Buffer = typename Matrix3<T>::BufferType;

template <typename T>
using Vec3Buffer = typename Vector3<T>::BufferType;

template <typename T>
using SFINAE_MAT3_SCALAR_GUARD =
    typename std::enable_if<IsScalar<T>::value>::type*;

template <typename T, SFINAE_MAT3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_transpose_inplace_mat3(Mat3Buffer<T>& mat) -> void {
    std::swap(mat[0][1], mat[1][0]);
    std::swap(mat[0][2], mat[2][0]);
    std::swap(mat[1][2], mat[2][1]);
}

template <typename T, SFINAE_MAT3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_trace_mat3(const Mat3Buffer<T>& mat) -> T {
    return mat[0][0] + mat[1][1] + mat[2][2];
}

template <typename T, SFINAE_MAT3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_determinant_mat3(const Mat3Buffer<T>& mat) -> T {
    auto m00 = mat[0][0];
    auto m10 = mat[0][1];
    auto m20 = mat[0][2];

    auto m01 = mat[1][0];
    auto m11 = mat[1][1];
    auto m21 = mat[1][2];

    auto m02 = mat[2][0];
    auto m12 = mat[2][1];
    auto m22 = mat[2][2];

    // Compute cofactors (only the ones required for the determinant)
    auto c00 = (m11 * m22 - m21 * m12);
    auto c10 = -(m01 * m22 - m21 * m02);
    auto c20 = (m01 * m12 - m11 * m02);

    return m00 * c00 + m10 * c10 + m20 * c20;
}

template <typename T, SFINAE_MAT3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_inverse_mat3(Mat3Buffer<T>& dst, const Mat3Buffer<T>& src)
    -> void {
    auto m00 = src[0][0];
    auto m10 = src[0][1];
    auto m20 = src[0][2];

    auto m01 = src[1][0];
    auto m11 = src[1][1];
    auto m21 = src[1][2];

    auto m02 = src[2][0];
    auto m12 = src[2][1];
    auto m22 = src[2][2];

    // Compute cofactors
    auto c00 = (m11 * m22 - m21 * m12);
    auto c10 = -(m01 * m22 - m21 * m02);
    auto c20 = (m01 * m12 - m11 * m02);

    auto c01 = -(m10 * m22 - m20 * m12);
    auto c11 = (m00 * m22 - m20 * m02);
    auto c21 = -(m00 * m12 - m10 * m02);

    auto c02 = (m10 * m21 - m20 * m11);
    auto c12 = -(m00 * m21 - m20 * m01);
    auto c22 = (m00 * m11 - m10 * m01);

    auto det = m00 * c00 + m10 * c10 + m20 * c20;
    auto inv_det = static_cast<T>(1.0) / det;

    // The inverse is the adjoint (transpose of cofactors matrix) divided by det
    dst[0][0] = c00 * inv_det;
    dst[0][1] = c01 * inv_det;
    dst[0][2] = c02 * inv_det;

    dst[1][0] = c10 * inv_det;
    dst[1][1] = c11 * inv_det;
    dst[1][2] = c12 * inv_det;

    dst[2][0] = c20 * inv_det;
    dst[2][1] = c21 * inv_det;
    dst[2][2] = c22 * inv_det;
}

template <typename T, SFINAE_MAT3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_mat3(Mat3Buffer<T>& dst, const Mat3Buffer<T>& lhs,
                               const Mat3Buffer<T>& rhs) -> void {
    for (uint32_t col = 0; col < Matrix3<T>::MATRIX_SIZE; ++col) {
        for (uint32_t row = 0; row < Matrix3<T>::MATRIX_SIZE; ++row) {
            dst[col][row] = lhs[col][row] + rhs[col][row];
        }
    }
}

template <typename T, SFINAE_MAT3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_mat3(Mat3Buffer<T>& dst, const Mat3Buffer<T>& lhs,
                               const Mat3Buffer<T>& rhs) -> void {
    for (uint32_t col = 0; col < Matrix3<T>::MATRIX_SIZE; ++col) {
        for (uint32_t row = 0; row < Matrix3<T>::MATRIX_SIZE; ++row) {
            dst[col][row] = lhs[col][row] - rhs[col][row];
        }
    }
}

template <typename T, SFINAE_MAT3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_mat3(Mat3Buffer<T>& dst, T scale,
                                 const Mat3Buffer<T>& mat) -> void {
    for (uint32_t col = 0; col < Matrix3<T>::MATRIX_SIZE; ++col) {
        for (uint32_t row = 0; row < Matrix3<T>::MATRIX_SIZE; ++row) {
            dst[col][row] = scale * mat[col][row];
        }
    }
}

template <typename T, SFINAE_MAT3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_mat3(Mat3Buffer<T>& dst, const Mat3Buffer<T>& lhs,
                                  const Mat3Buffer<T>& rhs) -> void {
    // We're assumming that dst is zero-initialized (default-constructor)
    for (uint32_t col = 0; col < Matrix3<T>::MATRIX_SIZE; ++col) {
        for (uint32_t row = 0; row < Matrix3<T>::MATRIX_SIZE; ++row) {
            for (uint32_t k = 0; k < Matrix3<T>::MATRIX_SIZE; ++k) {
                dst[col][row] += lhs[k][row] * rhs[col][k];
            }
        }
    }
}

template <typename T, SFINAE_MAT3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_vec_mat3(Vec3Buffer<T>& dst,
                                      const Mat3Buffer<T>& mat,
                                      const Vec3Buffer<T>& vec) -> void {
    dst[0] = mat[0][0] * vec[0] + mat[1][0] * vec[1] + mat[2][0] * vec[2];
    dst[1] = mat[0][1] * vec[0] + mat[1][1] * vec[1] + mat[2][1] * vec[2];
    dst[2] = mat[0][2] * vec[0] + mat[1][2] * vec[1] + mat[2][2] * vec[2];
}

template <typename T, SFINAE_MAT3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_hadamard_mat3(Mat3Buffer<T>& dst,
                                    const Mat3Buffer<T>& lhs,
                                    const Mat3Buffer<T>& rhs) -> void {
    for (uint32_t col = 0; col < Matrix3<T>::MATRIX_SIZE; ++col) {
        for (uint32_t row = 0; row < Matrix3<T>::MATRIX_SIZE; ++row) {
            dst[col][row] = lhs[col][row] * rhs[col][row];
        }
    }
}

template <typename T, SFINAE_MAT3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_compare_eq_mat3(const Mat3Buffer<T>& lhs,
                                      const Mat3Buffer<T>& rhs) -> bool {
    for (uint32_t col = 0; col < Matrix3<T>::MATRIX_SIZE; ++col) {
        for (uint32_t row = 0; row < Matrix3<T>::MATRIX_SIZE; ++row) {
            if (std::abs(lhs[col][row] - rhs[col][row]) >
                static_cast<T>(math::EPS)) {
                return false;
            }
        }
    }
    return true;
}

}  // namespace scalar
}  // namespace math
