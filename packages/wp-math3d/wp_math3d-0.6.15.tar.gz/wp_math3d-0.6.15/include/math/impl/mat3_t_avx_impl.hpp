#pragma once

#if defined(MATH_AVX_ENABLED)

#include <immintrin.h>

#include <math/mat3_t_decl.hpp>

/**
 * SSE instruction sets required for each kernel:
 *
 * - kernel_add_mat4                : AVX
 * - kernel_sub_mat4                : AVX
 * - kernel_scale_mat4              : AVX
 * - kernel_hadamard_mat4           : AVX
 *   kernel_matmul_mat4             : AVX
 *   kernel_matmul_vec_mat4         : AVX
 *
 * Notes:
 * 0. Matrix order:
 *    Our matrices' internal storage layout is column-major order
 *
 * 1. For AVX-float32:
 *    The columns of the matrix can each one be stored in an xmm register (4xf32
 *    fits into 128bit xmm reg.). Or we could use fit more into a ymm register
 *    (up to 8 floats, which is exactly 2 columns)
 *
 * 2. For AVX-float64:
 *    We can only store full columns into the ymm registers
 */

namespace math {
namespace avx {

template <typename T>
using Mat3Buffer = typename Matrix3<T>::BufferType;

template <typename T>
using Vec3Buffer = typename Vector3<T>::BufferType;

template <typename T>
using SFINAE_MAT3_F32_AVX_GUARD =
    typename std::enable_if<CpuHasAVX<T>::value && IsFloat32<T>::value>::type*;

template <typename T>
using SFINAE_MAT3_F64_AVX_GUARD =
    typename std::enable_if<CpuHasAVX<T>::value && IsFloat64<T>::value>::type*;

// ***************************************************************************//
//                    Dispatch AVX-kernel for matrix addition                 //
// ***************************************************************************//

template <typename T, SFINAE_MAT3_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_mat3(Mat3Buffer<T>& dst, const Mat3Buffer<T>& lhs,
                               const Mat3Buffer<T>& rhs) -> void {
    // Will use avx instructions (ymm-regs) for the first group of 2 columns,
    // and then sse instructions (xmm-regs) for the remaining column :)
    auto ymm_lhs_cols_01 =
        _mm256_loadu_ps(static_cast<const float*>(lhs[0].data()));
    auto ymm_rhs_cols_01 =
        _mm256_loadu_ps(static_cast<const float*>(rhs[0].data()));
    auto ymm_sum_cols_01 = _mm256_add_ps(ymm_lhs_cols_01, ymm_rhs_cols_01);

    auto xmm_lhs_col_2 = _mm_loadu_ps(static_cast<const float*>(lhs[2].data()));
    auto xmm_rhs_col_2 = _mm_loadu_ps(static_cast<const float*>(rhs[2].data()));
    auto xmm_sum_col_2 = _mm_add_ps(xmm_lhs_col_2, xmm_rhs_col_2);

    _mm256_storeu_ps(static_cast<float*>(dst[0].data()), ymm_sum_cols_01);
    _mm_storeu_ps(static_cast<float*>(dst[2].data()), xmm_sum_col_2);
}

template <typename T, SFINAE_MAT3_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_mat3(Mat3Buffer<T>& dst, const Mat3Buffer<T>& lhs,
                               const Mat3Buffer<T>& rhs) -> void {
    // A single column fits into a ymm register ((3+1)xf64 <> 256-bit reg.)
    for (uint32_t j = 0; j < Matrix3<T>::MATRIX_SIZE; ++j) {
        auto ymm_lhs_col_j =
            _mm256_loadu_pd(static_cast<const double*>(lhs[j].data()));
        auto ymm_rhs_col_j =
            _mm256_loadu_pd(static_cast<const double*>(rhs[j].data()));
        auto ymm_sum_cols_j = _mm256_add_pd(ymm_lhs_col_j, ymm_rhs_col_j);
        _mm256_storeu_pd(static_cast<double*>(dst[j].data()), ymm_sum_cols_j);
    }
}

// ***************************************************************************//
//                 Dispatch AVX-kernel for matrix substraction                //
// ***************************************************************************//

template <typename T, SFINAE_MAT3_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_mat3(Mat3Buffer<T>& dst, const Mat3Buffer<T>& lhs,
                               const Mat3Buffer<T>& rhs) -> void {
    // Proceed the same way we used the addition kernel
    auto ymm_lhs_cols_01 =
        _mm256_loadu_ps(static_cast<const float*>(lhs[0].data()));
    auto ymm_rhs_cols_01 =
        _mm256_loadu_ps(static_cast<const float*>(rhs[0].data()));
    auto ymm_sum_cols_01 = _mm256_sub_ps(ymm_lhs_cols_01, ymm_rhs_cols_01);

    auto xmm_lhs_col_2 = _mm_loadu_ps(static_cast<const float*>(lhs[2].data()));
    auto xmm_rhs_col_2 = _mm_loadu_ps(static_cast<const float*>(rhs[2].data()));
    auto xmm_sub_col_2 = _mm_sub_ps(xmm_lhs_col_2, xmm_rhs_col_2);

    _mm256_storeu_ps(static_cast<float*>(dst[0].data()), ymm_sum_cols_01);
    _mm_storeu_ps(static_cast<float*>(dst[2].data()), xmm_sub_col_2);
}

template <typename T, SFINAE_MAT3_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_mat3(Mat3Buffer<T>& dst, const Mat3Buffer<T>& lhs,
                               const Mat3Buffer<T>& rhs) -> void {
    for (uint32_t j = 0; j < Matrix3<T>::MATRIX_SIZE; ++j) {
        auto ymm_lhs_col_j =
            _mm256_loadu_pd(static_cast<const double*>(lhs[j].data()));
        auto ymm_rhs_col_j =
            _mm256_loadu_pd(static_cast<const double*>(rhs[j].data()));
        auto ymm_sub_col_j = _mm256_sub_pd(ymm_lhs_col_j, ymm_rhs_col_j);
        _mm256_storeu_pd(static_cast<double*>(dst[j].data()), ymm_sub_col_j);
    }
}

// ***************************************************************************//
//                Dispatch AVX-kernel for matrix-scalar product               //
// ***************************************************************************//

template <typename T, SFINAE_MAT3_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_mat3(Mat3Buffer<T>& dst, T scale,
                                 const Mat3Buffer<T>& src) -> void {
    // Similarly, scale 8xf32 (ymm) and then 4xf32 (xmm)
    auto ymm_scale = _mm256_set1_ps(scale);
    auto ymm_mat_cols_01 =
        _mm256_loadu_ps(static_cast<const float*>(src[0].data()));
    auto ymm_mat_scaled_cols_01 = _mm256_mul_ps(ymm_scale, ymm_mat_cols_01);

    auto xmm_scale = _mm_set1_ps(scale);
    auto xmm_mat_col_2 = _mm_loadu_ps(static_cast<const float*>(src[2].data()));
    auto xmm_mat_scaled_col_2 = _mm_mul_ps(xmm_scale, xmm_mat_col_2);

    _mm256_storeu_ps(static_cast<float*>(dst[0].data()),
                     ymm_mat_scaled_cols_01);
    _mm_storeu_ps(static_cast<float*>(dst[2].data()), xmm_mat_scaled_col_2);
}

template <typename T, SFINAE_MAT3_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_mat3(Mat3Buffer<T>& dst, T scale,
                                 const Mat3Buffer<T>& src) -> void {
    auto ymm_scale = _mm256_set1_pd(scale);
    for (uint32_t j = 0; j < Matrix3<T>::MATRIX_SIZE; ++j) {
        auto ymm_mat_col_j =
            _mm256_loadu_pd(static_cast<const double*>(src[j].data()));
        auto ymm_mat_scaled_col_j = _mm256_mul_pd(ymm_scale, ymm_mat_col_j);
        _mm256_storeu_pd(static_cast<double*>(dst[j].data()),
                         ymm_mat_scaled_col_j);
    }
}

// ***************************************************************************//
//                Dispatch AVX-kernel for matrix-matrix product               //
// ***************************************************************************//

template <typename T, SFINAE_MAT3_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_mat3(Mat3Buffer<T>& dst, const Mat3Buffer<T>& lhs,
                                  const Mat3Buffer<T>& rhs) -> void {
    for (uint32_t k = 0; k < Matrix3<T>::MATRIX_SIZE; ++k) {
        auto xmm_result_col_k = _mm_setzero_ps();
        for (uint32_t j = 0; j < Matrix3<T>::MATRIX_SIZE; ++j) {
            auto xmm_scalar_rhs_jk = _mm_set1_ps(rhs[k][j]);
            auto xmm_lhs_col_j =
                _mm_loadu_ps(static_cast<const float*>(lhs[j].data()));
            xmm_result_col_k = _mm_add_ps(
                xmm_result_col_k, _mm_mul_ps(xmm_scalar_rhs_jk, xmm_lhs_col_j));
        }
        _mm_storeu_ps(static_cast<float*>(dst[k].data()), xmm_result_col_k);
    }
}

template <typename T, SFINAE_MAT3_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_mat3(Mat3Buffer<T>& dst, const Mat3Buffer<T>& lhs,
                                  const Mat3Buffer<T>& rhs) -> void {
    for (uint32_t k = 0; k < Matrix3<T>::MATRIX_SIZE; ++k) {
        auto ymm_result_col_k = _mm256_setzero_pd();
        for (uint32_t j = 0; j < Matrix3<T>::MATRIX_SIZE; ++j) {
            auto ymm_scalar_rhs_jk = _mm256_set1_pd(rhs[k][j]);
            auto ymm_lhs_col_j =
                _mm256_loadu_pd(static_cast<const double*>(lhs[j].data()));
            ymm_result_col_k =
                _mm256_add_pd(ymm_result_col_k,
                              _mm256_mul_pd(ymm_scalar_rhs_jk, ymm_lhs_col_j));
        }
        _mm256_storeu_pd(static_cast<double*>(dst[k].data()), ymm_result_col_k);
    }
}

// ***************************************************************************//
//                Dispatch AVX-kernel for matrix-vector product               //
// ***************************************************************************//

template <typename T, SFINAE_MAT3_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_vec_mat3(Vec3Buffer<T>& dst,
                                      const Mat3Buffer<T>& mat,
                                      const Vec3Buffer<T>& vec) -> void {
    auto xmm_result = _mm_setzero_ps();
    for (uint32_t j = 0; j < Matrix3<T>::MATRIX_SIZE; ++j) {
        auto xmm_vec_scalar_j = _mm_set1_ps(vec[j]);
        auto xmm_mat_col_j =
            _mm_loadu_ps(static_cast<const float*>(mat[j].data()));
        xmm_result =
            _mm_add_ps(xmm_result, _mm_mul_ps(xmm_vec_scalar_j, xmm_mat_col_j));
    }
    _mm_storeu_ps(static_cast<float*>(dst.data()), xmm_result);
}

template <typename T, SFINAE_MAT3_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_vec_mat3(Vec3Buffer<T>& dst,
                                      const Mat3Buffer<T>& mat,
                                      const Vec3Buffer<T>& vec) -> void {
    auto ymm_result = _mm256_setzero_pd();
    for (uint32_t j = 0; j < Matrix3<T>::MATRIX_SIZE; ++j) {
        auto ymm_vec_scalar_j = _mm256_set1_pd(vec[j]);
        auto ymm_mat_col_j =
            _mm256_loadu_pd(static_cast<const double*>(mat[j].data()));
        ymm_result = _mm256_add_pd(
            ymm_result, _mm256_mul_pd(ymm_vec_scalar_j, ymm_mat_col_j));
    }
    _mm256_storeu_pd(static_cast<double*>(dst.data()), ymm_result);
}

// ***************************************************************************//
//             Dispatch AVX-kernel for matrix element-wise product            //
// ***************************************************************************//

template <typename T, SFINAE_MAT3_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_hadamard_mat3(Mat3Buffer<T>& dst,
                                    const Mat3Buffer<T>& lhs,
                                    const Mat3Buffer<T>& rhs) -> void {
    auto ymm_lhs_cols_01 =
        _mm256_loadu_ps(static_cast<const float*>(lhs[0].data()));
    auto ymm_rhs_cols_01 =
        _mm256_loadu_ps(static_cast<const float*>(rhs[0].data()));
    auto ymm_mul_cols_01 = _mm256_mul_ps(ymm_lhs_cols_01, ymm_rhs_cols_01);

    auto xmm_lhs_col_2 = _mm_loadu_ps(static_cast<const float*>(lhs[2].data()));
    auto xmm_rhs_col_2 = _mm_loadu_ps(static_cast<const float*>(rhs[2].data()));
    auto xmm_mul_col_2 = _mm_mul_ps(xmm_lhs_col_2, xmm_rhs_col_2);

    _mm256_storeu_ps(static_cast<float*>(dst[0].data()), ymm_mul_cols_01);
    _mm_storeu_ps(static_cast<float*>(dst[2].data()), xmm_mul_col_2);
}

template <typename T, SFINAE_MAT3_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_hadamard_mat3(Mat3Buffer<T>& dst,
                                    const Mat3Buffer<T>& lhs,
                                    const Mat3Buffer<T>& rhs) -> void {
    for (uint32_t j = 0; j < Matrix3<T>::MATRIX_SIZE; ++j) {
        auto ymm_lhs_col_j =
            _mm256_loadu_pd(static_cast<const double*>(lhs[j].data()));
        auto ymm_rhs_col_j =
            _mm256_loadu_pd(static_cast<const double*>(rhs[j].data()));
        auto ymm_mul_col_j = _mm256_mul_pd(ymm_lhs_col_j, ymm_rhs_col_j);
        _mm256_storeu_pd(static_cast<double*>(dst[j].data()), ymm_mul_col_j);
    }
}

}  // namespace avx
}  // namespace math

#endif  // MATH_AVX_ENABLED
