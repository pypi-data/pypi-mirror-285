#pragma once

#if defined(MATH_SSE_ENABLED)

#include <emmintrin.h>
#include <smmintrin.h>
#include <xmmintrin.h>

#include <math/mat2_t_decl.hpp>

#if defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wcomment"
#endif

/**
 * SSE instruction sets required for each kernel:
 *
 * - kernel_add_mat2                : SSE|SSE2
 * - kernel_sub_mat2                : SSE|SSE2
 * - kernel_scale_mat2              : SSE|SSE2
 * - kernel_hadamard_mat2           : SSE|SSE2
 *   kernel_matmul_mat2             : SSE|SSE2|FMA?(if available)
 *   kernel_matmul_vec_mat2         : SSE|SSE2|FMA?(if available)
 *
 * Notes:
 * 0. Matrix order:
 *    Our matrices' internal storage layout is column-major order
 *
 * 1. For SSE-float32:
 *    The columns of the matrix can all be stored in a single xmm register
 *    (4xf32 fits into 128bit xmm reg.)
 *
 * 2. For SSE-float64:
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
namespace sse {

template <typename T>
using Mat2Buffer = typename Matrix2<T>::BufferType;

template <typename T>
using Vec2Buffer = typename Vector2<T>::BufferType;

template <typename T>
using SFINAE_MAT2_F32_SSE_GUARD =
    typename std::enable_if<CpuHasSSE<T>::value && IsFloat32<T>::value>::type*;

template <typename T>
using SFINAE_MAT2_F64_SSE_GUARD =
    typename std::enable_if<CpuHasSSE<T>::value && IsFloat64<T>::value>::type*;

// ***************************************************************************//
//                   Dispatch SSE-kernel for matrix addition                  //
// ***************************************************************************//

template <typename T, SFINAE_MAT2_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_mat2(Mat2Buffer<T>& dst, const Mat2Buffer<T>& lhs,
                               const Mat2Buffer<T>& rhs) -> void {
    // For a matrix M = [m00  m01] all f32 entries fit into a single xmm
    //                  [m10  m11]
    // register, as follows: [m00 m10 m01 m11] (in column-major order). So just
    auto xmm_mat_lhs = _mm_loadu_ps(static_cast<const float*>(lhs[0].data()));
    auto xmm_mat_rhs = _mm_loadu_ps(static_cast<const float*>(rhs[0].data()));
    auto xmm_mat_result = _mm_add_ps(xmm_mat_lhs, xmm_mat_rhs);
    _mm_storeu_ps(static_cast<float*>(dst[0].data()), xmm_mat_result);
}

template <typename T, SFINAE_MAT2_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_mat2(Mat2Buffer<T>& dst, const Mat2Buffer<T>& lhs,
                               const Mat2Buffer<T>& rhs) -> void {
    // Half a matrix (col0 or col1) enter in a single xmm_register, so we'll
    // handle the split accordingly
    auto xmm_mat_lhs_col0 =
        _mm_loadu_pd(static_cast<const double*>(lhs[0].data()));
    auto xmm_mat_rhs_col0 =
        _mm_loadu_pd(static_cast<const double*>(rhs[0].data()));
    auto xmm_mat_result_col0 = _mm_add_pd(xmm_mat_lhs_col0, xmm_mat_rhs_col0);

    auto xmm_mat_lhs_col1 =
        _mm_loadu_pd(static_cast<const double*>(lhs[1].data()));
    auto xmm_mat_rhs_col1 =
        _mm_loadu_pd(static_cast<const double*>(rhs[1].data()));
    auto xmm_mat_result_col1 = _mm_add_pd(xmm_mat_lhs_col1, xmm_mat_rhs_col1);

    _mm_storeu_pd(static_cast<double*>(dst[0].data()), xmm_mat_result_col0);
    _mm_storeu_pd(static_cast<double*>(dst[1].data()), xmm_mat_result_col1);
}

// ***************************************************************************//
//                 Dispatch SSE-kernel for matrix substraction                //
// ***************************************************************************//

template <typename T, SFINAE_MAT2_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_mat2(Mat2Buffer<T>& dst, const Mat2Buffer<T>& lhs,
                               const Mat2Buffer<T>& rhs) -> void {
    // Similar approach to matrix addition
    auto xmm_mat_lhs = _mm_loadu_ps(static_cast<const float*>(lhs[0].data()));
    auto xmm_mat_rhs = _mm_loadu_ps(static_cast<const float*>(rhs[0].data()));
    auto xmm_mat_result = _mm_sub_ps(xmm_mat_lhs, xmm_mat_rhs);
    _mm_storeu_ps(static_cast<float*>(dst[0].data()), xmm_mat_result);
}

template <typename T, SFINAE_MAT2_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_mat2(Mat2Buffer<T>& dst, const Mat2Buffer<T>& lhs,
                               const Mat2Buffer<T>& rhs) -> void {
    // Similar approach to matrix addition
    auto xmm_mat_lhs_col0 =
        _mm_loadu_pd(static_cast<const double*>(lhs[0].data()));
    auto xmm_mat_rhs_col0 =
        _mm_loadu_pd(static_cast<const double*>(rhs[0].data()));
    auto xmm_mat_lhs_col1 =
        _mm_loadu_pd(static_cast<const double*>(lhs[1].data()));
    auto xmm_mat_rhs_col1 =
        _mm_loadu_pd(static_cast<const double*>(rhs[1].data()));

    auto xmm_mat_result_col0 = _mm_sub_pd(xmm_mat_lhs_col0, xmm_mat_rhs_col0);
    auto xmm_mat_result_col1 = _mm_sub_pd(xmm_mat_lhs_col1, xmm_mat_rhs_col1);

    _mm_storeu_pd(static_cast<double*>(dst[0].data()), xmm_mat_result_col0);
    _mm_storeu_pd(static_cast<double*>(dst[1].data()), xmm_mat_result_col1);
}

// ***************************************************************************//
//                Dispatch SSE-kernel for matrix-scalar product               //
// ***************************************************************************//

template <typename T, SFINAE_MAT2_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_mat2(Mat2Buffer<T>& dst, T scale,
                                 const Mat2Buffer<T>& src) -> void {
    // All matrix entries fit into single xmm register, so just scale it by
    // another xmm register that has the scale
    auto xmm_src = _mm_loadu_ps(static_cast<const float*>(src[0].data()));
    auto xmm_scale = _mm_set1_ps(scale);
    auto xmm_result = _mm_mul_ps(xmm_src, xmm_scale);
    _mm_storeu_ps(static_cast<float*>(dst[0].data()), xmm_result);
}

template <typename T, SFINAE_MAT2_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_mat2(Mat2Buffer<T>& dst, T scale,
                                 const Mat2Buffer<T>& src) -> void {
    // Same approach as previous case, but one column at a time
    auto xmm_src_col0 = _mm_loadu_pd(static_cast<const double*>(src[0].data()));
    auto xmm_src_col1 = _mm_loadu_pd(static_cast<const double*>(src[1].data()));
    auto xmm_scale = _mm_set1_pd(scale);

    auto xmm_result_col0 = _mm_mul_pd(xmm_src_col0, xmm_scale);
    auto xmm_result_col1 = _mm_mul_pd(xmm_src_col1, xmm_scale);

    _mm_storeu_pd(static_cast<double*>(dst[0].data()), xmm_result_col0);
    _mm_storeu_pd(static_cast<double*>(dst[1].data()), xmm_result_col1);
}

// ***************************************************************************//
//                Dispatch SSE-kernel for matrix-matrix product               //
// ***************************************************************************//

template <typename T, SFINAE_MAT2_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_mat2(Mat2Buffer<T>& dst, const Mat2Buffer<T>& lhs,
                                  const Mat2Buffer<T>& rhs) -> void {
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
    //        /            |
    // [b00,b00,b01,b01]  [b10,b10,b11,b11]
    //         x                  x
    // [a00,a10,a00,a10]  [a01,a11,a01,a11]
    //          |               |
    //          |              |
    //          [matmul result]
    auto xmm_rhs_mix_0 = _mm_shuffle_ps(xmm_mat_rhs, xmm_mat_rhs, 0xa0);
    auto xmm_rhs_mix_1 = _mm_shuffle_ps(xmm_mat_rhs, xmm_mat_rhs, 0xf5);
    auto xmm_lhs_mix_0 = _mm_shuffle_ps(xmm_mat_lhs, xmm_mat_lhs, 0x44);
    auto xmm_lhs_mix_1 = _mm_shuffle_ps(xmm_mat_lhs, xmm_mat_lhs, 0xee);

    auto xmm_result_mix_0 = _mm_mul_ps(xmm_lhs_mix_0, xmm_rhs_mix_0);
    auto xmm_result_mix_1 = _mm_mul_ps(xmm_lhs_mix_1, xmm_rhs_mix_1);
    auto xmm_result = _mm_add_ps(xmm_result_mix_0, xmm_result_mix_1);
    _mm_storeu_ps(static_cast<float*>(dst[0].data()), xmm_result);
}

template <typename T, SFINAE_MAT2_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_mat2(Mat2Buffer<T>& dst, const Mat2Buffer<T>& lhs,
                                  const Mat2Buffer<T>& rhs) -> void {
    auto xmm_mat_lhs_col0 =
        _mm_loadu_pd(static_cast<const double*>(lhs[0].data()));
    auto xmm_mat_lhs_col1 =
        _mm_loadu_pd(static_cast<const double*>(lhs[1].data()));
    // Take the column-space view of the  matmul (generating first column)
    auto xmm_scalar_rhs_00 = _mm_set1_pd(rhs[0][0]);
    auto xmm_scalar_rhs_10 = _mm_set1_pd(rhs[0][1]);
    auto xmm_scaled_lhs_col0 = _mm_mul_pd(xmm_scalar_rhs_00, xmm_mat_lhs_col0);
    auto xmm_scaled_lhs_col1 = _mm_mul_pd(xmm_scalar_rhs_10, xmm_mat_lhs_col1);
    auto xmm_result_col0 = _mm_add_pd(xmm_scaled_lhs_col0, xmm_scaled_lhs_col1);

    // Take the column-space view of the matmul (generating second column)
    auto xmm_scalar_rhs_01 = _mm_set1_pd(rhs[1][0]);
    auto xmm_scalar_rhs_11 = _mm_set1_pd(rhs[1][1]);
    xmm_scaled_lhs_col0 = _mm_mul_pd(xmm_scalar_rhs_01, xmm_mat_lhs_col0);
    xmm_scaled_lhs_col1 = _mm_mul_pd(xmm_scalar_rhs_11, xmm_mat_lhs_col1);
    auto xmm_result_col1 = _mm_add_pd(xmm_scaled_lhs_col0, xmm_scaled_lhs_col1);

    // Store our results :D (one column at a time)
    _mm_storeu_pd(static_cast<double*>(dst[0].data()), xmm_result_col0);
    _mm_storeu_pd(static_cast<double*>(dst[1].data()), xmm_result_col1);
}

// ***************************************************************************//
//                Dispatch SSE-kernel for matrix-vector product               //
// ***************************************************************************//

template <typename T, SFINAE_MAT2_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_vec_mat2(Vec2Buffer<T>& dst,
                                      const Mat2Buffer<T>& mat,
                                      const Vec2Buffer<T>& vec) -> void {
    // SORRY, can't come up with a way to do it for the moment :(. Will use
    // scalar version instead TODO(wilbert)
    dst[0] = mat[0][0] * vec[0] + mat[1][0] * vec[1];
    dst[1] = mat[0][1] * vec[0] + mat[1][1] * vec[1];
}

template <typename T, SFINAE_MAT2_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_matmul_vec_mat2(Vec2Buffer<T>& dst,
                                      const Mat2Buffer<T>& mat,
                                      const Vec2Buffer<T>& vec) -> void {
    auto xmm_mat_col0 = _mm_loadu_pd(static_cast<const double*>(mat[0].data()));
    auto xmm_mat_col1 = _mm_loadu_pd(static_cast<const double*>(mat[1].data()));

    auto xmm_vec_scalar_0 = _mm_set1_pd(vec[0]);
    auto xmm_vec_scalar_1 = _mm_set1_pd(vec[1]);

    auto xmm_mat_scaled_col0 = _mm_mul_pd(xmm_vec_scalar_0, xmm_mat_col0);
    auto xmm_mat_scaled_col1 = _mm_mul_pd(xmm_vec_scalar_1, xmm_mat_col1);
    auto xmm_result = _mm_add_pd(xmm_mat_scaled_col0, xmm_mat_scaled_col1);
    _mm_storeu_pd(static_cast<double*>(dst.data()), xmm_result);
}

// ***************************************************************************//
//             Dispatch SSE-kernel for matrix element-wise product            //
// ***************************************************************************//

template <typename T, SFINAE_MAT2_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_hadamard_mat2(Mat2Buffer<T>& dst,
                                    const Mat2Buffer<T>& lhs,
                                    const Mat2Buffer<T>& rhs) -> void {
    auto xmm_mat_lhs = _mm_loadu_ps(static_cast<const float*>(lhs[0].data()));
    auto xmm_mat_rhs = _mm_loadu_ps(static_cast<const float*>(rhs[0].data()));
    auto xmm_result = _mm_mul_ps(xmm_mat_lhs, xmm_mat_rhs);
    _mm_storeu_ps(static_cast<float*>(dst[0].data()), xmm_result);
}

template <typename T, SFINAE_MAT2_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_hadamard_mat2(Mat2Buffer<T>& dst,
                                    const Mat2Buffer<T>& lhs,
                                    const Mat2Buffer<T>& rhs) -> void {
    auto xmm_mat_lhs_col0 =
        _mm_loadu_pd(static_cast<const double*>(lhs[0].data()));
    auto xmm_mat_lhs_col1 =
        _mm_loadu_pd(static_cast<const double*>(lhs[1].data()));
    auto xmm_mat_rhs_col0 =
        _mm_loadu_pd(static_cast<const double*>(rhs[0].data()));
    auto xmm_mat_rhs_col1 =
        _mm_loadu_pd(static_cast<const double*>(rhs[1].data()));

    auto xmm_result_col0 = _mm_mul_pd(xmm_mat_lhs_col0, xmm_mat_rhs_col0);
    auto xmm_result_col1 = _mm_mul_pd(xmm_mat_lhs_col1, xmm_mat_rhs_col1);

    _mm_storeu_pd(static_cast<double*>(dst[0].data()), xmm_result_col0);
    _mm_storeu_pd(static_cast<double*>(dst[1].data()), xmm_result_col1);
}

}  // namespace sse
}  // namespace math

#if defined(__GNUC__)
#pragma GCC diagnostic pop
#endif

#endif  // MATH_SSE_ENABLED
