#pragma once

#include <cmath>
#include <utility>

#include <math/mat4_t_decl.hpp>

namespace math {
namespace scalar {

template <typename T>
using Mat4Buffer = typename Matrix4<T>::BufferType;

template <typename T>
using Vec4Buffer = typename Vector4<T>::BufferType;

template <typename T>
using SFINAE_MAT4_SCALAR_GUARD =
    typename std::enable_if<IsScalar<T>::value>::type*;

template <typename T, SFINAE_MAT4_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_transpose_inplace_mat4(Mat4Buffer<T>& mat) -> void {
    std::swap(mat[0][1], mat[1][0]);
    std::swap(mat[0][2], mat[2][0]);
    std::swap(mat[0][3], mat[3][0]);
    std::swap(mat[1][2], mat[2][1]);
    std::swap(mat[1][3], mat[3][1]);
    std::swap(mat[2][3], mat[3][2]);
}

template <typename T, SFINAE_MAT4_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_trace_mat4(const Mat4Buffer<T>& mat) -> T {
    return mat[0][0] + mat[1][1] + mat[2][2] + mat[3][3];
}

template <typename T, SFINAE_MAT4_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_determinant_mat4(const Mat4Buffer<T>& mat) -> T {
    auto m00 = mat[0][0];
    auto m10 = mat[0][1];
    auto m20 = mat[0][2];
    auto m30 = mat[0][3];

    auto m01 = mat[1][0];
    auto m11 = mat[1][1];
    auto m21 = mat[1][2];
    auto m31 = mat[1][3];

    auto m02 = mat[2][0];
    auto m12 = mat[2][1];
    auto m22 = mat[2][2];
    auto m32 = mat[2][3];

    auto m03 = mat[3][0];
    auto m13 = mat[3][1];
    auto m23 = mat[3][2];
    auto m33 = mat[3][3];

    // Calculate minors of order 2
    auto m2323 = m22 * m33 - m32 * m23;
    auto m1323 = m12 * m33 - m32 * m13;
    auto m0323 = m02 * m33 - m32 * m03;
    auto m1223 = m12 * m23 - m22 * m13;
    auto m0223 = m02 * m23 - m22 * m03;
    auto m0123 = m02 * m13 - m12 * m03;

    return m00 * (m11 * m2323 - m21 * m1323 + m31 * m1223) -
           m10 * (m01 * m2323 - m21 * m0323 + m31 * m0223) +
           m20 * (m01 * m1323 - m11 * m0323 + m31 * m0123) -
           m30 * (m01 * m1223 - m11 * m0223 + m21 * m0123);
}

template <typename T, SFINAE_MAT4_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_inverse_mat4(Mat4Buffer<T>& dst, const Mat4Buffer<T>& src)
    -> void {
    auto m00 = src[0][0];
    auto m10 = src[0][1];
    auto m20 = src[0][2];
    auto m30 = src[0][3];

    auto m01 = src[1][0];
    auto m11 = src[1][1];
    auto m21 = src[1][2];
    auto m31 = src[1][3];

    auto m02 = src[2][0];
    auto m12 = src[2][1];
    auto m22 = src[2][2];
    auto m32 = src[2][3];

    auto m03 = src[3][0];
    auto m13 = src[3][1];
    auto m23 = src[3][2];
    auto m33 = src[3][3];

    // Calculate minors of order 2
    auto m2323 = m22 * m33 - m32 * m23;
    auto m1323 = m12 * m33 - m32 * m13;
    auto m0323 = m02 * m33 - m32 * m03;
    auto m1223 = m12 * m23 - m22 * m13;
    auto m0223 = m02 * m23 - m22 * m03;
    auto m0123 = m02 * m13 - m12 * m03;

    auto m1201 = m10 * m21 - m20 * m11;
    auto m1301 = m10 * m31 - m30 * m11;
    auto m2301 = m20 * m31 - m30 * m21;
    auto m0201 = m00 * m21 - m20 * m01;
    auto m0301 = m00 * m31 - m30 * m01;
    auto m0101 = m00 * m11 - m10 * m01;

    auto det = m00 * (m11 * m2323 - m21 * m1323 + m31 * m1223) -
               m10 * (m01 * m2323 - m21 * m0323 + m31 * m0223) +
               m20 * (m01 * m1323 - m11 * m0323 + m31 * m0123) -
               m30 * (m01 * m1223 - m11 * m0223 + m21 * m0123);

    auto inv_det = static_cast<T>(1.0) / det;

    // The inverse is the adjoint (transpose of cofactors matrix) divided by det
    dst[0][0] = (m11 * m2323 - m21 * m1323 + m31 * m1223) * inv_det;
    dst[0][1] = (m10 * m2323 - m20 * m1323 + m30 * m1223) * -inv_det;
    dst[0][2] = (m33 * m1201 - m23 * m1301 + m13 * m2301) * inv_det;
    dst[0][3] = (m32 * m1201 - m22 * m1301 + m12 * m2301) * -inv_det;

    dst[1][0] = (m01 * m2323 - m21 * m0323 + m31 * m0223) * -inv_det;
    dst[1][1] = (m00 * m2323 - m20 * m0323 + m30 * m0223) * inv_det;
    dst[1][2] = (m33 * m0201 - m23 * m0301 + m03 * m2301) * -inv_det;
    dst[1][3] = (m32 * m0201 - m22 * m0301 + m02 * m2301) * inv_det;

    dst[2][0] = (m01 * m1323 - m11 * m0323 + m31 * m0123) * inv_det;
    dst[2][1] = (m00 * m1323 - m10 * m0323 + m30 * m0123) * -inv_det;
    dst[2][2] = (m33 * m0101 - m13 * m0301 + m03 * m1301) * inv_det;
    dst[2][3] = (m32 * m0101 - m12 * m0301 + m02 * m1301) * -inv_det;

    dst[3][0] = (m01 * m1223 - m11 * m0223 + m21 * m0123) * -inv_det;
    dst[3][1] = (m00 * m1223 - m10 * m0223 + m20 * m0123) * inv_det;
    dst[3][2] = (m23 * m0101 - m13 * m0201 + m03 * m1201) * -inv_det;
    dst[3][3] = (m22 * m0101 - m12 * m0201 + m02 * m1201) * inv_det;
}

template <typename T, SFINAE_MAT4_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_mat4(Mat4Buffer<T>& dst, const Mat4Buffer<T>& lhs,
                               const Mat4Buffer<T>& rhs) -> void {
    for (uint32_t col = 0; col < Matrix4<T>::MATRIX_SIZE; ++col) {
        for (uint32_t idx = 0; idx < Matrix4<T>::MATRIX_SIZE; ++idx) {
            dst[col][idx] = lhs[col][idx] + rhs[col][idx];
        }
    }
}

template <typename T, SFINAE_MAT4_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_mat4(Mat4Buffer<T>& dst, const Mat4Buffer<T>& lhs,
                               const Mat4Buffer<T>& rhs) -> void {
    for (uint32_t col = 0; col < Matrix4<T>::MATRIX_SIZE; ++col) {
        for (uint32_t idx = 0; idx < Matrix4<T>::MATRIX_SIZE; ++idx) {
            dst[col][idx] = lhs[col][idx] - rhs[col][idx];
        }
    }
}

template <typename T, SFINAE_MAT4_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_mat4(Mat4Buffer<T>& dst, T scale,
                                 const Mat4Buffer<T>& mat) -> void {
    for (uint32_t col = 0; col < Matrix4<T>::MATRIX_SIZE; ++col) {
        for (uint32_t idx = 0; idx < Matrix4<T>::MATRIX_SIZE; ++idx) {
            dst[col][idx] = scale * mat[col][idx];
        }
    }
}

template <typename T, SFINAE_MAT4_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_mat4(Mat4Buffer<T>& dst, const Mat4Buffer<T>& lhs,
                                  const Mat4Buffer<T>& rhs) -> void {
    // We're assumming that dst is zero-initialized (default-constructor)
    for (uint32_t col = 0; col < Matrix4<T>::MATRIX_SIZE; ++col) {
        for (uint32_t row = 0; row < Matrix4<T>::MATRIX_SIZE; ++row) {
            for (uint32_t k = 0; k < Matrix4<T>::MATRIX_SIZE; ++k) {
                dst[col][row] += lhs[k][row] * rhs[col][k];
            }
        }
    }
}

template <typename T, SFINAE_MAT4_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_vec_mat4(Vec4Buffer<T>& dst,
                                      const Mat4Buffer<T>& mat,
                                      const Vec4Buffer<T>& vec) -> void {
    dst[0] = mat[0][0] * vec[0] + mat[1][0] * vec[1] + mat[2][0] * vec[2] +
             mat[3][0] * vec[3];
    dst[1] = mat[0][1] * vec[0] + mat[1][1] * vec[1] + mat[2][1] * vec[2] +
             mat[3][1] * vec[3];
    dst[2] = mat[0][2] * vec[0] + mat[1][2] * vec[1] + mat[2][2] * vec[2] +
             mat[3][2] * vec[3];
    dst[3] = mat[0][3] * vec[0] + mat[1][3] * vec[1] + mat[2][3] * vec[2] +
             mat[3][3] * vec[3];
}

template <typename T, SFINAE_MAT4_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_hadamard_mat4(Mat4Buffer<T>& dst,
                                    const Mat4Buffer<T>& lhs,
                                    const Mat4Buffer<T>& rhs) -> void {
    for (uint32_t col = 0; col < Matrix4<T>::MATRIX_SIZE; ++col) {
        for (uint32_t idx = 0; idx < Matrix4<T>::MATRIX_SIZE; ++idx) {
            dst[col][idx] = lhs[col][idx] * rhs[col][idx];
        }
    }
}

template <typename T, SFINAE_MAT4_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_compare_eq_mat4(const Mat4Buffer<T>& lhs,
                                      const Mat4Buffer<T>& rhs) -> bool {
    for (uint32_t col = 0; col < Matrix4<T>::MATRIX_SIZE; ++col) {
        for (uint32_t idx = 0; idx < Matrix4<T>::MATRIX_SIZE; ++idx) {
            if (std::abs(lhs[col][idx] - rhs[col][idx]) >
                static_cast<T>(math::EPS)) {
                return false;
            }
        }
    }
    return true;
}

}  // namespace scalar
}  // namespace math
