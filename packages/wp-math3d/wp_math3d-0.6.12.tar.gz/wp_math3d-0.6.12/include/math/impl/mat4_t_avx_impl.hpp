#pragma once

#if defined(MATH_AVX_ENABLED)

#include <immintrin.h>

#include <math/mat4_t_decl.hpp>

/**
 * SSE instruction sets required for each kernel:
 *
 * - kernel_add_mat4                : AVX
 * - kernel_sub_mat4                : AVX
 * - kernel_scale_mat4              : AVX
 * - kernel_hadamard_mat4           : AVX
 *   kernel_matmul_mat4             : AVX|FMA?(if available)
 *   kernel_matmul_vec_mat4         : AVX|FMA?(if available)
 *
 * Notes:
 * 0. Matrix order:
 *    Our matrices' internal storage layout is column-major order
 *
 * 1. For AVX-float32:
 *    The columns of the matrix can each one be stored in an xmm register (4xf32
 *    fits into 128bit xmm reg.)
 *
 * 2. For AVX-float64:
 *    We can only store half of a column of the matrices into an xmm register,
 *    so we have to use both lo-hi halves in 2 separate xmm registers for an op
 *
 * 3. If FMA is available:
 *    We could potentially benefit of these instructions (float-multiply-add) in
 *    the kernels mentioned above, but it'd require for the matrix storage
 *    layout to be row-major :/, unless it can be done in the linear-combination
 *    view of matrices and vectors
 */

namespace math {
namespace avx {

template <typename T>
using Mat4Buffer = typename Matrix4<T>::BufferType;

template <typename T>
using Vec4Buffer = typename Vector4<T>::BufferType;

template <typename T>
using SFINAE_MAT4_F32_AVX_GUARD =
    typename std::enable_if<CpuHasAVX<T>::value && IsFloat32<T>::value>::type*;

template <typename T>
using SFINAE_MAT4_F64_AVX_GUARD =
    typename std::enable_if<CpuHasAVX<T>::value && IsFloat64<T>::value>::type*;

// ***************************************************************************//
//                    Dispatch AVX-kernel for matrix addition                 //
// ***************************************************************************//

template <typename T, SFINAE_MAT4_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_mat4(Mat4Buffer<T>& dst, const Mat4Buffer<T>& lhs,
                               const Mat4Buffer<T>& rhs) -> void {
    // [c0, c1, c2, c3] -> column-major order (in storage), each with 4 x f32
    // So, we can send two columns to a YMM register, as the data is contiguous,
    // i.e. [c0, c1] are right next to each other (so can fit into ymm register)
    // Also, don't unroll the loop, as it most likely be optimized by the
    // compiler and unroll it for us
    // @todo(wilbert): check that the compiler does loop unrolling in this case
    constexpr uint32_t NUM_PASSES = Matrix4<T>::MATRIX_SIZE / 2;
    for (uint32_t k = 0; k < NUM_PASSES; ++k) {
        auto ymm_lhs_cols = _mm256_loadu_ps(lhs[2 * k].data());
        auto ymm_rhs_cols = _mm256_loadu_ps(rhs[2 * k].data());
        _mm256_storeu_ps(dst[2 * k].data(),
                         _mm256_add_ps(ymm_lhs_cols, ymm_rhs_cols));
    }
}

template <typename T, SFINAE_MAT4_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_mat4(Mat4Buffer<T>& dst, const Mat4Buffer<T>& lhs,
                               const Mat4Buffer<T>& rhs) -> void {
    // [c0, c1, c2, c3] -> column-major order (in storage), each with 4 x f64,
    // so we can send each column to an YMM register
    for (uint32_t j = 0; j < Matrix4<T>::MATRIX_SIZE; ++j) {
        auto ymm_lhs_col_j = _mm256_loadu_pd(lhs[j].data());
        auto ymm_rhs_col_j = _mm256_loadu_pd(rhs[j].data());
        _mm256_storeu_pd(dst[j].data(),
                         _mm256_add_pd(ymm_lhs_col_j, ymm_rhs_col_j));
    }
}

// ***************************************************************************//
//                 Dispatch AVX-kernel for matrix substraction                //
// ***************************************************************************//

template <typename T, SFINAE_MAT4_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_mat4(Mat4Buffer<T>& dst, const Mat4Buffer<T>& lhs,
                               const Mat4Buffer<T>& rhs) -> void {
    constexpr uint32_t NUM_PASSES = Matrix4<T>::MATRIX_SIZE / 2;
    for (uint32_t k = 0; k < NUM_PASSES; ++k) {
        auto ymm_lhs_cols = _mm256_loadu_ps(lhs[2 * k].data());
        auto ymm_rhs_cols = _mm256_loadu_ps(rhs[2 * k].data());
        _mm256_storeu_ps(dst[2 * k].data(),
                         _mm256_sub_ps(ymm_lhs_cols, ymm_rhs_cols));
    }
}

template <typename T, SFINAE_MAT4_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_mat4(Mat4Buffer<T>& dst, const Mat4Buffer<T>& lhs,
                               const Mat4Buffer<T>& rhs) -> void {
    for (uint32_t j = 0; j < Matrix4<T>::MATRIX_SIZE; ++j) {
        auto ymm_lhs_col_j = _mm256_loadu_pd(lhs[j].data());
        auto ymm_rhs_col_j = _mm256_loadu_pd(rhs[j].data());
        _mm256_storeu_pd(dst[j].data(),
                         _mm256_sub_pd(ymm_lhs_col_j, ymm_rhs_col_j));
    }
}

// ***************************************************************************//
//                Dispatch AVX-kernel for matrix-scalar product               //
// ***************************************************************************//

template <typename T, SFINAE_MAT4_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_mat4(Mat4Buffer<T>& dst, T scale,
                                 const Mat4Buffer<T>& mat) -> void {
    constexpr uint32_t NUM_PASSES = Matrix4<T>::MATRIX_SIZE / 2;
    auto ymm_scale = _mm256_set1_ps(scale);
    for (uint32_t k = 0; k < NUM_PASSES; ++k) {
        // Should load all 8 floats of contiguous memory corresponding to
        // 2xVec4f columns of the matrix given
        auto ymm_mat_cols = _mm256_loadu_ps(mat[2 * k].data());
        _mm256_storeu_ps(dst[2 * k].data(),
                         _mm256_mul_ps(ymm_scale, ymm_mat_cols));
    }
}

template <typename T, SFINAE_MAT4_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_mat4(Mat4Buffer<T>& dst, T scale,
                                 const Mat4Buffer<T>& mat) -> void {
    auto ymm_scale = _mm256_set1_pd(scale);
    for (uint32_t j = 0; j < Matrix4<T>::MATRIX_SIZE; ++j) {
        auto ymm_mat_col_j = _mm256_loadu_pd(mat[j].data());
        _mm256_storeu_pd(dst[j].data(),
                         _mm256_mul_pd(ymm_scale, ymm_mat_col_j));
    }
}

// ***************************************************************************//
//                Dispatch AVX-kernel for matrix-matrix product               //
// ***************************************************************************//

template <typename T, SFINAE_MAT4_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_mat4(Mat4Buffer<T>& dst, const Mat4Buffer<T>& lhs,
                                  const Mat4Buffer<T>& rhs) -> void {
    // Use the SSE version as fallback (our previous implementation fails in
    // some cases where the matrix seem poorly conditioned)
    for (uint32_t k = 0; k < Matrix4<T>::MATRIX_SIZE; ++k) {
        // Compute each resulting column, as in the  "matmul_vec" kernel
        auto xmm_result_col_k = _mm_setzero_ps();
        for (uint32_t j = 0; j < Matrix4<T>::MATRIX_SIZE; ++j) {
            //                              k=4            [      |     ]
            // A * v = (lhs * rhs)[:,k] = SUM   rhs[j,k] * |  lhs[:,j]  ]
            //                              k=0            [      |     ]
            auto xmm_scalar_rhs_jk = _mm_set1_ps(rhs[k][j]);
            auto xmm_lhs_col_j = _mm_loadu_ps(lhs[j].data());
            xmm_result_col_k = _mm_add_ps(
                xmm_result_col_k, _mm_mul_ps(xmm_scalar_rhs_jk, xmm_lhs_col_j));
        }
        _mm_storeu_ps(dst[k].data(), xmm_result_col_k);
    }
}

template <typename T, SFINAE_MAT4_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_mat4(Mat4Buffer<T>& dst, const Mat4Buffer<T>& lhs,
                                  const Mat4Buffer<T>& rhs) -> void {
    // Use the "linear combination view" of the matrix-vector product, and apply
    // it along all column vectors of the right-hand side
    for (uint32_t k = 0; k < Matrix4<T>::MATRIX_SIZE; ++k) {
        // Compute each resulting column, as in the  "matmul_vec" kernel
        auto ymm_result_col_k = _mm256_setzero_pd();
        for (uint32_t j = 0; j < Matrix4<T>::MATRIX_SIZE; ++j) {
            //                              k=4            [      |     ]
            // A * v = (lhs * rhs)[:,k] = SUM   rhs[j,k] * |  lhs[:,j]  ]
            //                              k=0            [      |     ]
            auto ymm_scalar_rhs_jk = _mm256_set1_pd(rhs[k][j]);
            auto ymm_lhs_col_j = _mm256_loadu_pd(lhs[j].data());
            ymm_result_col_k =
                _mm256_add_pd(ymm_result_col_k,
                              _mm256_mul_pd(ymm_scalar_rhs_jk, ymm_lhs_col_j));
        }
        _mm256_storeu_pd(dst[k].data(), ymm_result_col_k);
    }
}

// ***************************************************************************//
//                Dispatch AVX-kernel for matrix-vector product               //
// ***************************************************************************//

template <typename T, SFINAE_MAT4_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_vec_mat4(Vec4Buffer<T>& dst,
                                      const Mat4Buffer<T>& mat,
                                      const Vec4Buffer<T>& vec) -> void {
    // Use the SSE version as fallback (our previous implementation fails in
    // some cases where the matrix seem poorly conditioned)
    auto xmm_result = _mm_setzero_ps();
    for (uint32_t j = 0; j < Matrix4<T>::MATRIX_SIZE; ++j) {
        auto xmm_scalar_vj = _mm_set1_ps(vec[j]);
        auto xmm_mat_col_j = _mm_loadu_ps(mat[j].data());
        xmm_result =
            _mm_add_ps(xmm_result, _mm_mul_ps(xmm_scalar_vj, xmm_mat_col_j));
    }
    _mm_storeu_ps(dst.data(), xmm_result);
}

template <typename T, SFINAE_MAT4_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_vec_mat4(Vec4Buffer<T>& dst,
                                      const Mat4Buffer<T>& mat,
                                      const Vec4Buffer<T>& vec) -> void {
    // Use the "linear combination view" of the matrix-vector product
    //         [ |  |  |  |  ]
    // A * v = | a0 a1 a2 a3 | * [v0,v1,v2,v3]^T
    //         [ |  |  |  |  ]
    //
    //             [ |]       [ |]        [ |]        [ |]
    // A * v = v0 *|a0]+ v1 * |a1] + v2 * |a2] + v3 * |a3]
    //             [ |]       [ |]        [ |]        [ |]
    //
    // Each column A[:,j] contains 4xf64 of data, so it fits in a single YMM reg
    auto ymm_result = _mm256_setzero_pd();
    for (uint32_t j = 0; j < Matrix4<T>::MATRIX_SIZE; ++j) {
        auto ymm_scalar_vj = _mm256_set1_pd(vec[j]);
        auto ymm_mat_col_j = _mm256_loadu_pd(mat[j].data());
        ymm_result = _mm256_add_pd(ymm_result,
                                   _mm256_mul_pd(ymm_scalar_vj, ymm_mat_col_j));
    }
    _mm256_storeu_pd(dst.data(), ymm_result);
}

// ***************************************************************************//
//             Dispatch AVX-kernel for matrix element-wise product            //
// ***************************************************************************//

template <typename T, SFINAE_MAT4_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_hadamard_mat4(Mat4Buffer<T>& dst,
                                    const Mat4Buffer<T>& lhs,
                                    const Mat4Buffer<T>& rhs) -> void {
    constexpr uint32_t NUM_PASSES = Matrix4<T>::MATRIX_SIZE / 2;
    for (uint32_t k = 0; k < NUM_PASSES; ++k) {
        auto ymm_lhs_cols = _mm256_loadu_ps(lhs[2 * k].data());
        auto ymm_rhs_cols = _mm256_loadu_ps(rhs[2 * k].data());
        _mm256_storeu_ps(dst[2 * k].data(),
                         _mm256_mul_ps(ymm_lhs_cols, ymm_rhs_cols));
    }
}

template <typename T, SFINAE_MAT4_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_hadamard_mat4(Mat4Buffer<T>& dst,
                                    const Mat4Buffer<T>& lhs,
                                    const Mat4Buffer<T>& rhs) -> void {
    for (uint32_t j = 0; j < Matrix4<T>::MATRIX_SIZE; ++j) {
        auto ymm_lhs_col_j = _mm256_loadu_pd(lhs[j].data());
        auto ymm_rhs_col_j = _mm256_loadu_pd(rhs[j].data());
        _mm256_storeu_pd(dst[j].data(),
                         _mm256_mul_pd(ymm_lhs_col_j, ymm_rhs_col_j));
    }
}

}  // namespace avx
}  // namespace math

#endif  // MATH_AVX_ENABLED
