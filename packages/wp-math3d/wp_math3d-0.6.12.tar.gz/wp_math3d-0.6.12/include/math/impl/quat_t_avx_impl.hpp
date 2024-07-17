#pragma once

#if defined(MATH_AVX_ENABLED)

#include <immintrin.h>

#include <math/quat_t_decl.hpp>

namespace math {
namespace avx {

template <typename T>
using QuatBuffer = typename Quaternion<T>::BufferType;

template <typename T>
using SFINAE_QUAT_F32_AVX_GUARD =
    typename std::enable_if<CpuHasAVX<T>::value && IsFloat32<T>::value>::type*;

template <typename T>
using SFINAE_QUAT_F64_AVX_GUARD =
    typename std::enable_if<CpuHasAVX<T>::value && IsFloat64<T>::value>::type*;

template <typename T, SFINAE_QUAT_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_quat(QuatBuffer<T>& dst, const QuatBuffer<T>& lhs,
                               const QuatBuffer<T>& rhs) -> void {
    auto xmm_lhs = _mm_loadu_ps(lhs.data());
    auto xmm_rhs = _mm_loadu_ps(rhs.data());
    auto xmm_result = _mm_add_ps(xmm_lhs, xmm_rhs);
    _mm_storeu_ps(dst.data(), xmm_result);
}

template <typename T, SFINAE_QUAT_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_quat(QuatBuffer<T>& dst, const QuatBuffer<T>& lhs,
                               const QuatBuffer<T>& rhs) -> void {
    auto ymm_lhs = _mm256_loadu_pd(lhs.data());
    auto ymm_rhs = _mm256_loadu_pd(rhs.data());
    auto ymm_result = _mm256_add_pd(ymm_lhs, ymm_rhs);
    _mm256_storeu_pd(dst.data(), ymm_result);
}

template <typename T, SFINAE_QUAT_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_quat(QuatBuffer<T>& dst, const QuatBuffer<T>& lhs,
                               const QuatBuffer<T>& rhs) -> void {
    auto xmm_lhs = _mm_loadu_ps(lhs.data());
    auto xmm_rhs = _mm_loadu_ps(rhs.data());
    auto xmm_result = _mm_sub_ps(xmm_lhs, xmm_rhs);
    _mm_storeu_ps(dst.data(), xmm_result);
}

template <typename T, SFINAE_QUAT_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_quat(QuatBuffer<T>& dst, const QuatBuffer<T>& lhs,
                               const QuatBuffer<T>& rhs) -> void {
    auto ymm_lhs = _mm256_loadu_pd(lhs.data());
    auto ymm_rhs = _mm256_loadu_pd(rhs.data());
    auto ymm_result = _mm256_sub_pd(ymm_lhs, ymm_rhs);
    _mm256_storeu_pd(dst.data(), ymm_result);
}

template <typename T, SFINAE_QUAT_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_quat(QuatBuffer<T>& dst, T scale,
                                 const QuatBuffer<T>& quat) -> void {
    auto xmm_scale = _mm_set1_ps(scale);
    auto xmm_vector = _mm_loadu_ps(quat.data());
    auto xmm_result = _mm_mul_ps(xmm_scale, xmm_vector);
    _mm_storeu_ps(dst.data(), xmm_result);
}

template <typename T, SFINAE_QUAT_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_quat(QuatBuffer<T>& dst, T scale,
                                 const QuatBuffer<T>& quat) -> void {
    auto ymm_scale = _mm256_set1_pd(scale);
    auto ymm_quat = _mm256_loadu_pd(quat.data());
    auto ymm_result = _mm256_mul_pd(ymm_scale, ymm_quat);
    _mm256_storeu_pd(dst.data(), ymm_result);
}

template <typename T, SFINAE_QUAT_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_square_quat(const QuatBuffer<T>& quat) -> T {
    auto xmm_q = _mm_loadu_ps(static_cast<const float*>(quat.data()));
    auto xmm_square_sum = _mm_dp_ps(xmm_q, xmm_q, 0xf1);
    return _mm_cvtss_f32(xmm_square_sum);
}

template <typename T, SFINAE_QUAT_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_square_quat(const QuatBuffer<T>& quat) -> T {
    auto ymm_q = _mm256_loadu_pd(static_cast<const double*>(quat.data()));
    auto ymm_prod = _mm256_mul_pd(ymm_q, ymm_q);
    auto ymm_hsum = _mm256_hadd_pd(ymm_prod, ymm_prod);
    auto xmm_sum_lo = _mm256_extractf128_pd(ymm_hsum, 0);
    auto xmm_sum_hi = _mm256_extractf128_pd(ymm_hsum, 1);
    auto xmm_square_sum = _mm_add_pd(xmm_sum_lo, xmm_sum_hi);
    return _mm_cvtsd_f64(xmm_square_sum);
}

template <typename T, SFINAE_QUAT_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_quat(const QuatBuffer<T>& quat) -> T {
    auto xmm_q = _mm_loadu_ps(static_cast<const float*>(quat.data()));
    auto xmm_square_sum = _mm_dp_ps(xmm_q, xmm_q, 0xf1);
    return _mm_cvtss_f32(_mm_sqrt_ss(xmm_square_sum));
}

template <typename T, SFINAE_QUAT_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_quat(const QuatBuffer<T>& quat) -> T {
    auto ymm_q = _mm256_loadu_pd(static_cast<const double*>(quat.data()));
    auto ymm_prod = _mm256_mul_pd(ymm_q, ymm_q);
    auto ymm_hsum = _mm256_hadd_pd(ymm_prod, ymm_prod);
    auto xmm_sum_lo = _mm256_extractf128_pd(ymm_hsum, 0);
    auto xmm_sum_hi = _mm256_extractf128_pd(ymm_hsum, 1);
    auto xmm_square_sum = _mm_add_pd(xmm_sum_lo, xmm_sum_hi);
    return _mm_cvtsd_f64(_mm_sqrt_sd(xmm_square_sum, xmm_square_sum));
}

template <typename T, SFINAE_QUAT_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_normalize_in_place_quat(QuatBuffer<T>& quat) -> void {
    // Whole quaternion fits into a single xmm register, so use SSE instructions
    auto xmm_v = _mm_loadu_ps(static_cast<const float*>(quat.data()));
    auto xmm_squares_sum = _mm_dp_ps(xmm_v, xmm_v, 0xff);
    auto xmm_lengths = _mm_sqrt_ps(xmm_squares_sum);
    auto xmm_v_norm = _mm_div_ps(xmm_v, xmm_lengths);
    _mm_storeu_ps(static_cast<float*>(quat.data()), xmm_v_norm);
}

template <typename T, SFINAE_QUAT_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_normalize_in_place_quat(QuatBuffer<T>& quat) -> void {
    // Whole quaternion fits into a single ymm register, so use AVX instructions
    // Note that we're not using _mm256_dp_ , as it does something different in
    // this instruction set, compared to its SSE counterpart. That's why we're
    // using permutations and half adds to obtain the same behaviour
    auto ymm_v = _mm256_loadu_pd(static_cast<const double*>(quat.data()));
    auto ymm_squares = _mm256_mul_pd(ymm_v, ymm_v);
    // Construct the sum of squares into each double of a 256-bit register
    auto ymm_tmp0 = _mm256_permute2f128_pd(ymm_squares, ymm_squares, 0x21);
    auto ymm_tmp1 = _mm256_hadd_pd(ymm_squares, ymm_tmp0);
    auto ymm_squares_sum = _mm256_hadd_pd(ymm_tmp1, ymm_tmp1);
    // Compute the normalized vector
    auto ymm_lengths = _mm256_sqrt_pd(ymm_squares_sum);
    auto ymm_v_norm = _mm256_div_pd(ymm_v, ymm_lengths);
    _mm256_storeu_pd(static_cast<double*>(quat.data()), ymm_v_norm);
}

}  // namespace avx
}  // namespace math

#endif  // MATH_AVX_ENABLED
