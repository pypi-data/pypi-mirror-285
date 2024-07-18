#pragma once

#include <cmath>
#include <utility>

#include <math/mat2_t_decl.hpp>

// TODO(wilbert): Check that loops are unrolled (otherwise unroll manually)

namespace math {
namespace scalar {

template <typename T>
using Mat2Buffer = typename Matrix2<T>::BufferType;

template <typename T>
using Vec2Buffer = typename Vector2<T>::BufferType;

template <typename T>
using SFINAE_MAT2_SCALAR_GUARD =
    typename std::enable_if<IsScalar<T>::value>::type*;

template <typename T, SFINAE_MAT2_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_transpose_inplace_mat2(Mat2Buffer<T>& cols) -> void {
    for (uint32_t col = 1; col < Matrix2<T>::MATRIX_SIZE; ++col) {
        for (uint32_t row = 0; row < Matrix2<T>::MATRIX_SIZE; ++row) {
            std::swap(cols[col][row], cols[row][col]);
        }
    }
}

template <typename T, SFINAE_MAT2_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_trace_mat2(const Mat2Buffer<T>& mat) -> T {
    return mat[0][0] + mat[1][1];
}

template <typename T, SFINAE_MAT2_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_determinant_mat2(const Mat2Buffer<T>& mat) -> T {
    auto m00 = mat[0][0];
    auto m10 = mat[0][1];
    auto m01 = mat[1][0];
    auto m11 = mat[1][1];

    return m00 * m11 - m10 * m01;
}

template <typename T, SFINAE_MAT2_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_inverse_mat2(Mat2Buffer<T>& dst, const Mat2Buffer<T>& src)
    -> void {
    auto m00 = src[0][0];
    auto m01 = src[1][0];
    auto m10 = src[0][1];
    auto m11 = src[1][1];

    auto det = m00 * m11 - m10 * m01;

    dst[0][0] = m11 / det;
    dst[0][1] = -m10 / det;
    dst[1][0] = -m01 / det;
    dst[1][1] = m00 / det;
}

template <typename T, SFINAE_MAT2_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_mat2(Mat2Buffer<T>& dst, const Mat2Buffer<T>& lhs,
                               const Mat2Buffer<T>& rhs) -> void {
    for (uint32_t col = 0; col < Matrix2<T>::MATRIX_SIZE; ++col) {
        for (uint32_t idx = 0; idx < Matrix2<T>::MATRIX_SIZE; ++idx) {
            dst[col][idx] = lhs[col][idx] + rhs[col][idx];
        }
    }
}

template <typename T, SFINAE_MAT2_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_mat2(Mat2Buffer<T>& dst, const Mat2Buffer<T>& lhs,
                               const Mat2Buffer<T>& rhs) -> void {
    for (uint32_t col = 0; col < Matrix2<T>::MATRIX_SIZE; ++col) {
        for (uint32_t idx = 0; idx < Matrix2<T>::MATRIX_SIZE; ++idx) {
            dst[col][idx] = lhs[col][idx] - rhs[col][idx];
        }
    }
}

template <typename T, SFINAE_MAT2_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_mat2(Mat2Buffer<T>& dst, T scale,
                                 const Mat2Buffer<T>& mat) -> void {
    for (uint32_t col = 0; col < Matrix2<T>::MATRIX_SIZE; ++col) {
        for (uint32_t idx = 0; idx < Matrix2<T>::MATRIX_SIZE; ++idx) {
            dst[col][idx] = scale * mat[col][idx];
        }
    }
}

template <typename T, SFINAE_MAT2_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_mat2(Mat2Buffer<T>& dst, const Mat2Buffer<T>& lhs,
                                  const Mat2Buffer<T>& rhs) -> void {
    // We're assumming that dst is zero-initialized (default-constructor)
    for (uint32_t col = 0; col < Matrix2<T>::MATRIX_SIZE; ++col) {
        for (uint32_t row = 0; row < Matrix2<T>::MATRIX_SIZE; ++row) {
            for (uint32_t k = 0; k < Matrix2<T>::MATRIX_SIZE; ++k) {
                dst[col][row] += lhs[k][row] * rhs[col][k];
            }
        }
    }
}

template <typename T, SFINAE_MAT2_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_vec_mat2(Vec2Buffer<T>& dst,
                                      const Mat2Buffer<T>& mat,
                                      const Vec2Buffer<T>& vec) -> void {
    dst[0] = mat[0][0] * vec[0] + mat[1][0] * vec[1];
    dst[1] = mat[0][1] * vec[0] + mat[1][1] * vec[1];
}

template <typename T, SFINAE_MAT2_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_hadamard_mat2(Mat2Buffer<T>& dst,
                                    const Mat2Buffer<T>& lhs,
                                    const Mat2Buffer<T>& rhs) -> void {
    for (uint32_t col = 0; col < Matrix2<T>::MATRIX_SIZE; ++col) {
        for (uint32_t idx = 0; idx < Matrix2<T>::MATRIX_SIZE; ++idx) {
            dst[col][idx] = lhs[col][idx] * rhs[col][idx];
        }
    }
}

template <typename T, SFINAE_MAT2_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_compare_eq_mat2(const Mat2Buffer<T>& lhs,
                                      const Mat2Buffer<T>& rhs) -> bool {
    for (uint32_t col = 0; col < Matrix2<T>::MATRIX_SIZE; ++col) {
        for (uint32_t idx = 0; idx < Matrix2<T>::MATRIX_SIZE; ++idx) {
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
