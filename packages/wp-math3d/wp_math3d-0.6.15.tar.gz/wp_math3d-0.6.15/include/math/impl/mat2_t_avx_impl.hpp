#pragma once

#if defined(MATH_AVX_ENABLED)

#include <immintrin.h>

#include <math/mat2_t_decl.hpp>

#if defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wcomment"
#endif

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
 *    The whole matrix fits into an xmm register
 *
 * 2. For AVX-float64:
 *    The whole matrix fits into a ymm register
 */

namespace math {
namespace avx {

template <typename T>
using Mat2Buffer = typename Matrix2<T>::BufferType;

template <typename T>
using Vec2Buffer = typename Vector2<T>::BufferType;

template <typename T>
using SFINAE_MAT2_F32_AVX_GUARD =
    typename std::enable_if<CpuHasAVX<T>::value && IsFloat32<T>::value>::type*;

template <typename T>
using SFINAE_MAT2_F64_AVX_GUARD =
    typename std::enable_if<CpuHasAVX<T>::value && IsFloat64<T>::value>::type*;

// ***************************************************************************//
//                    Dispatch AVX-kernel for matrix addition                 //
// ***************************************************************************//

template <typename T, SFINAE_MAT2_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_mat2(Mat2Buffer<T>& dst, const Mat2Buffer<T>& lhs,
                               const Mat2Buffer<T>& rhs) -> void {
    // [c0,c1] both columns (2x2 f32) fit into a single xmm register
    auto xmm_mat_lhs = _mm_loadu_ps(static_cast<const float*>(lhs[0].data()));
    auto xmm_mat_rhs = _mm_loadu_ps(static_cast<const float*>(rhs[0].data()));

    auto xmm_result = _mm_add_ps(xmm_mat_lhs, xmm_mat_rhs);
    _mm_storeu_ps(static_cast<float*>(dst[0].data()), xmm_result);
}

template <typename T, SFINAE_MAT2_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_mat2(Mat2Buffer<T>& dst, const Mat2Buffer<T>& lhs,
                               const Mat2Buffer<T>& rhs) -> void {
    // [c0, c1] both columns (2x2 f64) fit into a single ymm register
    auto ymm_mat_lhs =
        _mm256_loadu_pd(static_cast<const double*>(lhs[0].data()));
    auto ymm_mat_rhs =
        _mm256_loadu_pd(static_cast<const double*>(rhs[0].data()));

    auto ymm_result = _mm256_add_pd(ymm_mat_lhs, ymm_mat_rhs);
    _mm256_storeu_pd(static_cast<double*>(dst[0].data()), ymm_result);
}

// ***************************************************************************//
//                 Dispatch AVX-kernel for matrix substraction                //
// ***************************************************************************//

template <typename T, SFINAE_MAT2_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_mat2(Mat2Buffer<T>& dst, const Mat2Buffer<T>& lhs,
                               const Mat2Buffer<T>& rhs) -> void {
    auto xmm_mat_lhs = _mm_loadu_ps(static_cast<const float*>(lhs[0].data()));
    auto xmm_mat_rhs = _mm_loadu_ps(static_cast<const float*>(rhs[0].data()));

    auto xmm_result = _mm_sub_ps(xmm_mat_lhs, xmm_mat_rhs);
    _mm_storeu_ps(static_cast<float*>(dst[0].data()), xmm_result);
}

template <typename T, SFINAE_MAT2_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_mat2(Mat2Buffer<T>& dst, const Mat2Buffer<T>& lhs,
                               const Mat2Buffer<T>& rhs) -> void {
    auto ymm_mat_lhs =
        _mm256_loadu_pd(static_cast<const double*>(lhs[0].data()));
    auto ymm_mat_rhs =
        _mm256_loadu_pd(static_cast<const double*>(rhs[0].data()));

    auto ymm_result = _mm256_sub_pd(ymm_mat_lhs, ymm_mat_rhs);
    _mm256_storeu_pd(static_cast<double*>(dst[0].data()), ymm_result);
}

// ***************************************************************************//
//                Dispatch AVX-kernel for matrix-scalar product               //
// ***************************************************************************//

template <typename T, SFINAE_MAT2_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_mat2(Mat2Buffer<T>& dst, T scale,
                                 const Mat2Buffer<T>& src) -> void {
    auto xmm_scale = _mm_set1_ps(scale);
    auto xmm_mat = _mm_loadu_ps(static_cast<const float*>(src[0].data()));

    auto xmm_mat_scaled = _mm_mul_ps(xmm_scale, xmm_mat);
    _mm_storeu_ps(static_cast<float*>(dst[0].data()), xmm_mat_scaled);
}

template <typename T, SFINAE_MAT2_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_mat2(Mat2Buffer<T>& dst, T scale,
                                 const Mat2Buffer<T>& src) -> void {
    auto ymm_scale = _mm256_set1_pd(scale);
    auto ymm_mat = _mm256_loadu_pd(static_cast<const double*>(src[0].data()));

    auto ymm_mat_scaled = _mm256_mul_pd(ymm_scale, ymm_mat);
    _mm256_storeu_pd(static_cast<double*>(dst[0].data()), ymm_mat_scaled);
}

// ***************************************************************************//
//                Dispatch AVX-kernel for matrix-matrix product               //
// ***************************************************************************//

template <typename T, SFINAE_MAT2_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_mat2(Mat2Buffer<T>& dst, const Mat2Buffer<T>& lhs,
                                  const Mat2Buffer<T>& rhs) -> void {
    // Use the same kernel as in SSE for f32 case :)
    auto xmm_mat_lhs = _mm_loadu_ps(static_cast<const float*>(lhs[0].data()));
    auto xmm_mat_rhs = _mm_loadu_ps(static_cast<const float*>(rhs[0].data()));
    // We proceed by shuffling the vectors and aligning everything such that the
    // resulting products comes naturally as the matmul operation.
    // We have loaded on the xmm registers (lhs = a, rhs = b):
    //      [a00,a10,a01,a11]
    //      [b00,b10,b01,b11] (recall we use column-major)
    //
    // We need to shuffle in this way both lhs and rhs
    //      [b00,b10,b01,b11]
    //        |            |
    // [b00,b00,b01,b01]  [b10,b10,b11,b11]
    //         x                  x
    // [a00,a10,a00,a10]  [a01,a11,a01,a11]
    //         |                 |
    //          |               |
    //           [matmul result]
    auto xmm_rhs_mix_0 = _mm_shuffle_ps(xmm_mat_rhs, xmm_mat_rhs, 0xa0);
    auto xmm_rhs_mix_1 = _mm_shuffle_ps(xmm_mat_rhs, xmm_mat_rhs, 0xf5);
    auto xmm_lhs_mix_0 = _mm_shuffle_ps(xmm_mat_lhs, xmm_mat_lhs, 0x44);
    auto xmm_lhs_mix_1 = _mm_shuffle_ps(xmm_mat_lhs, xmm_mat_lhs, 0xee);

    auto xmm_result_mix_0 = _mm_mul_ps(xmm_lhs_mix_0, xmm_rhs_mix_0);
    auto xmm_result_mix_1 = _mm_mul_ps(xmm_lhs_mix_1, xmm_rhs_mix_1);
    auto xmm_result = _mm_add_ps(xmm_result_mix_0, xmm_result_mix_1);
    _mm_storeu_ps(static_cast<float*>(dst[0].data()), xmm_result);
}

template <typename T, SFINAE_MAT2_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_mat2(Mat2Buffer<T>& dst, const Mat2Buffer<T>& lhs,
                                  const Mat2Buffer<T>& rhs) -> void {
    // Use the same approach as in SSE, but use AVX instructions instead
    auto ymm_mat_lhs =
        _mm256_loadu_pd(static_cast<const double*>(lhs[0].data()));
    auto ymm_mat_rhs =
        _mm256_loadu_pd(static_cast<const double*>(rhs[0].data()));
    // We proceed by shuffling the vectors and aligning everything such that the
    // resulting products comes naturally as the matmul operation.
    // We have loaded on the xmm registers (lhs = a, rhs = b):
    //      [a00,a10,a01,a11]
    //      [b00,b10,b01,b11] (recall we use column-major)
    //
    // We need to shuffle in this way both lhs and rhs
    //      [b00,b10,b01,b11]
    //        |            |
    // [b00,b00,b01,b01]  [b10,b10,b11,b11]
    //         x                  x
    // [a00,a10,a00,a10]  [a01,a11,a01,a11]
    //         |                 |
    //          |               |
    //           [matmul result]
    auto ymm_rhs_mix_0 = _mm256_shuffle_pd(ymm_mat_rhs, ymm_mat_rhs, 0x00);
    auto ymm_rhs_mix_1 = _mm256_shuffle_pd(ymm_mat_rhs, ymm_mat_rhs, 0x0f);
    auto ymm_lhs_mix_0 = _mm256_permute2f128_pd(ymm_mat_lhs, ymm_mat_lhs, 0x00);
    auto ymm_lhs_mix_1 = _mm256_permute2f128_pd(ymm_mat_lhs, ymm_mat_lhs, 0x11);

    auto ymm_result_mix_0 = _mm256_mul_pd(ymm_lhs_mix_0, ymm_rhs_mix_0);
    auto ymm_result_mix_1 = _mm256_mul_pd(ymm_lhs_mix_1, ymm_rhs_mix_1);
    auto ymm_result = _mm256_add_pd(ymm_result_mix_0, ymm_result_mix_1);
    _mm256_storeu_pd(static_cast<double*>(dst[0].data()), ymm_result);
}

// ***************************************************************************//
//                Dispatch SSE-kernel for matrix-vector product               //
// ***************************************************************************//

template <typename T, SFINAE_MAT2_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_vec_mat2(Vec2Buffer<T>& dst,
                                      const Mat2Buffer<T>& mat,
                                      const Vec2Buffer<T>& vec) -> void {
    // TODO(wilbert): Sorry, couldn't figure out a way to exploit xmm-128 or
    // ymm-256 bit registers. Will use the scalar version at the moment
    dst[0] = mat[0][0] * vec[0] + mat[1][0] * vec[1];
    dst[1] = mat[0][1] * vec[0] + mat[1][1] * vec[1];
}

template <typename T, SFINAE_MAT2_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_vec_mat2(Vec2Buffer<T>& dst,
                                      const Mat2Buffer<T>& mat,
                                      const Vec2Buffer<T>& vec) -> void {
    auto xmm_mat_col0 = _mm_loadu_pd(static_cast<const double*>(mat[0].data()));
    auto xmm_mat_col1 = _mm_loadu_pd(static_cast<const double*>(mat[1].data()));

    auto xmm_vec_scalar0 = _mm_set1_pd(vec[0]);
    auto xmm_vec_scalar1 = _mm_set1_pd(vec[1]);

    auto xmm_mat_scaled_col0 = _mm_mul_pd(xmm_vec_scalar0, xmm_mat_col0);
    auto xmm_mat_scaled_col1 = _mm_mul_pd(xmm_vec_scalar1, xmm_mat_col1);
    auto xmm_result = _mm_add_pd(xmm_mat_scaled_col0, xmm_mat_scaled_col1);
    _mm_storeu_pd(static_cast<double*>(dst.data()), xmm_result);
}

// ***************************************************************************//
//             Dispatch SSE-kernel for matrix element-wise product            //
// ***************************************************************************//

template <typename T, SFINAE_MAT2_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_hadamard_mat2(Mat2Buffer<T>& dst,
                                    const Mat2Buffer<T>& lhs,
                                    const Mat2Buffer<T>& rhs) -> void {
    auto xmm_mat_lhs = _mm_loadu_ps(static_cast<const float*>(lhs[0].data()));
    auto xmm_mat_rhs = _mm_loadu_ps(static_cast<const float*>(rhs[0].data()));
    auto xmm_result = _mm_mul_ps(xmm_mat_lhs, xmm_mat_rhs);
    _mm_storeu_ps(static_cast<float*>(dst[0].data()), xmm_result);
}

template <typename T, SFINAE_MAT2_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_hadamard_mat2(Mat2Buffer<T>& dst,
                                    const Mat2Buffer<T>& lhs,
                                    const Mat2Buffer<T>& rhs) -> void {
    auto ymm_mat_lhs =
        _mm256_loadu_pd(static_cast<const double*>(lhs[0].data()));
    auto ymm_mat_rhs =
        _mm256_loadu_pd(static_cast<const double*>(rhs[0].data()));
    auto ymm_result = _mm256_mul_pd(ymm_mat_lhs, ymm_mat_rhs);
    _mm256_storeu_pd(static_cast<double*>(dst[0].data()), ymm_result);
}

}  // namespace avx
}  // namespace math

#if defined(__GNUC__)
#pragma GCC diagnostic pop
#endif

#endif  // MATH_AVX_ENABLED
