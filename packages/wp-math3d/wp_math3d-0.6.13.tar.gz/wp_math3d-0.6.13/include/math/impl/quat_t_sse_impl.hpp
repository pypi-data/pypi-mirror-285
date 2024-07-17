#pragma once

#if defined(MATH_SSE_ENABLED)

#include <emmintrin.h>
#include <smmintrin.h>
#include <xmmintrin.h>

#include <math/quat_t_decl.hpp>

namespace math {
namespace sse {

template <typename T>
using QuatBuffer = typename Quaternion<T>::BufferType;

template <typename T>
using SFINAE_QUAT_F32_SSE_GUARD =
    typename std::enable_if<CpuHasSSE<T>::value && IsFloat32<T>::value>::type*;

template <typename T>
using SFINAE_QUAT_F64_SSE_GUARD =
    typename std::enable_if<CpuHasSSE<T>::value && IsFloat64<T>::value>::type*;

template <typename T, SFINAE_QUAT_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_quat(QuatBuffer<T>& dst, const QuatBuffer<T>& lhs,
                               const QuatBuffer<T>& rhs) -> void {
    auto xmm_lhs = _mm_loadu_ps(lhs.data());
    auto xmm_rhs = _mm_loadu_ps(rhs.data());
    auto xmm_result = _mm_add_ps(xmm_lhs, xmm_rhs);
    _mm_storeu_ps(dst.data(), xmm_result);
}

template <typename T, SFINAE_QUAT_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_quat(QuatBuffer<T>& dst, const QuatBuffer<T>& lhs,
                               const QuatBuffer<T>& rhs) -> void {
    auto xmm_lhs_lo = _mm_loadu_pd(lhs.data());
    auto xmm_lhs_hi = _mm_loadu_pd(lhs.data() + 2);
    auto xmm_rhs_lo = _mm_loadu_pd(rhs.data());
    auto xmm_rhs_hi = _mm_loadu_pd(rhs.data() + 2);
    auto xmm_result_lo = _mm_add_pd(xmm_lhs_lo, xmm_rhs_lo);
    auto xmm_result_hi = _mm_add_pd(xmm_lhs_hi, xmm_rhs_hi);
    _mm_storeu_pd(dst.data(), xmm_result_lo);
    _mm_storeu_pd(dst.data() + 2, xmm_result_hi);
}

template <typename T, SFINAE_QUAT_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_quat(QuatBuffer<T>& dst, const QuatBuffer<T>& lhs,
                               const QuatBuffer<T>& rhs) -> void {
    auto xmm_lhs = _mm_loadu_ps(lhs.data());
    auto xmm_rhs = _mm_loadu_ps(rhs.data());
    auto xmm_result = _mm_sub_ps(xmm_lhs, xmm_rhs);
    _mm_storeu_ps(dst.data(), xmm_result);
}

template <typename T, SFINAE_QUAT_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_quat(QuatBuffer<T>& dst, const QuatBuffer<T>& lhs,
                               const QuatBuffer<T>& rhs) -> void {
    auto xmm_lhs_lo = _mm_loadu_pd(lhs.data());
    auto xmm_lhs_hi = _mm_loadu_pd(lhs.data() + 2);
    auto xmm_rhs_lo = _mm_loadu_pd(rhs.data());
    auto xmm_rhs_hi = _mm_loadu_pd(rhs.data() + 2);
    auto xmm_result_lo = _mm_sub_pd(xmm_lhs_lo, xmm_rhs_lo);
    auto xmm_result_hi = _mm_sub_pd(xmm_lhs_hi, xmm_rhs_hi);
    _mm_storeu_pd(dst.data(), xmm_result_lo);
    _mm_storeu_pd(dst.data() + 2, xmm_result_hi);
}

template <typename T, SFINAE_QUAT_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_quat(QuatBuffer<T>& dst, T scale,
                                 const QuatBuffer<T>& quat) -> void {
    auto xmm_scale = _mm_set1_ps(scale);
    auto xmm_quat = _mm_loadu_ps(quat.data());
    auto xmm_result = _mm_mul_ps(xmm_scale, xmm_quat);
    _mm_storeu_ps(dst.data(), xmm_result);
}

template <typename T, SFINAE_QUAT_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_quat(QuatBuffer<T>& dst, T scale,
                                 const QuatBuffer<T>& quat) -> void {
    auto xmm_scale = _mm_set1_pd(scale);
    auto xmm_quat_lo = _mm_loadu_pd(quat.data());
    auto xmm_quat_hi = _mm_loadu_pd(quat.data() + 2);
    auto xmm_result_lo = _mm_mul_pd(xmm_scale, xmm_quat_lo);
    auto xmm_result_hi = _mm_mul_pd(xmm_scale, xmm_quat_hi);
    _mm_storeu_pd(dst.data(), xmm_result_lo);
    _mm_storeu_pd(dst.data() + 2, xmm_result_hi);
}

template <typename T, SFINAE_QUAT_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_square_quat(const QuatBuffer<T>& quat) -> T {
    auto xmm_q = _mm_loadu_ps(static_cast<const float*>(quat.data()));
    auto xmm_square_sum = _mm_dp_ps(xmm_q, xmm_q, 0xf1);
    return _mm_cvtss_f32(xmm_square_sum);
}

template <typename T, SFINAE_QUAT_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_square_quat(const QuatBuffer<T>& quat) -> T {
    auto xmm_q_lo = _mm_loadu_pd(static_cast<const double*>(quat.data()));
    auto xmm_q_hi = _mm_loadu_pd(static_cast<const double*>(quat.data() + 2));
    auto xmm_square_sum_lo = _mm_dp_pd(xmm_q_lo, xmm_q_lo, 0x31);
    auto xmm_square_sum_hi = _mm_dp_pd(xmm_q_hi, xmm_q_hi, 0x31);
    auto xmm_square_sum = _mm_add_pd(xmm_square_sum_lo, xmm_square_sum_hi);
    return _mm_cvtsd_f64(xmm_square_sum);
}

template <typename T, SFINAE_QUAT_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_quat(const QuatBuffer<T>& quat) -> T {
    auto xmm_q = _mm_loadu_ps(static_cast<const float*>(quat.data()));
    auto xmm_square_sum = _mm_dp_ps(xmm_q, xmm_q, 0xf1);
    return _mm_cvtss_f32(_mm_sqrt_ss(xmm_square_sum));
}

template <typename T, SFINAE_QUAT_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_quat(const QuatBuffer<T>& quat) -> T {
    auto xmm_q_lo = _mm_loadu_pd(static_cast<const double*>(quat.data()));
    auto xmm_q_hi = _mm_loadu_pd(static_cast<const double*>(quat.data() + 2));
    auto xmm_square_sum_lo = _mm_dp_pd(xmm_q_lo, xmm_q_lo, 0x31);
    auto xmm_square_sum_hi = _mm_dp_pd(xmm_q_hi, xmm_q_hi, 0x31);
    auto xmm_square_sum = _mm_add_pd(xmm_square_sum_lo, xmm_square_sum_hi);
    return _mm_cvtsd_f64(_mm_sqrt_sd(xmm_square_sum, xmm_square_sum));
}

template <typename T, SFINAE_QUAT_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_normalize_in_place_quat(QuatBuffer<T>& quat) -> void {
    auto xmm_v = _mm_loadu_ps(static_cast<const float*>(quat.data()));
    auto xmm_square_sums = _mm_dp_ps(xmm_v, xmm_v, 0xff);
    auto xmm_lengths = _mm_sqrt_ps(xmm_square_sums);
    auto xmm_v_norm = _mm_div_ps(xmm_v, xmm_lengths);
    _mm_storeu_ps(static_cast<float*>(quat.data()), xmm_v_norm);
}

template <typename T, SFINAE_QUAT_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_normalize_in_place_quat(QuatBuffer<T>& quat) -> void {
    auto xmm_v_lo = _mm_loadu_pd(static_cast<const double*>(quat.data()));
    auto xmm_v_hi = _mm_loadu_pd(static_cast<const double*>(quat.data() + 2));
    auto xmm_square_sums_lo = _mm_dp_pd(xmm_v_lo, xmm_v_lo, 0x33);
    auto xmm_square_sums_hi = _mm_dp_pd(xmm_v_hi, xmm_v_hi, 0x33);
    auto xmm_square_sums = _mm_add_pd(xmm_square_sums_lo, xmm_square_sums_hi);
    auto xmm_lengths = _mm_sqrt_pd(xmm_square_sums);
    auto xmm_v_norm_lo = _mm_div_pd(xmm_v_lo, xmm_lengths);
    auto xmm_v_norm_hi = _mm_div_pd(xmm_v_hi, xmm_lengths);
    _mm_storeu_pd(static_cast<double*>(quat.data()), xmm_v_norm_lo);
    _mm_storeu_pd(static_cast<double*>(quat.data() + 2), xmm_v_norm_hi);
}

}  // namespace sse
}  // namespace math

#endif  // MATH_SSE_ENABLED
