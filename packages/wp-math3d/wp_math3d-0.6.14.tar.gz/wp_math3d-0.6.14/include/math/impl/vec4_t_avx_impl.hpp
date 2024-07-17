#pragma once

#if defined(MATH_AVX_ENABLED)

#include <immintrin.h>

#include <math/vec4_t_decl.hpp>

/**
 * AVX instruction sets required for each kernel:
 *
 * - kernel_add_vec4        : SSE|AVX
 * - kernel_sub_vec4        : SSE|AVX
 * - kernel_scale_vec4      : SSE|AVX
 * - kernel_hadamard_vec4   : SSE|AVX
 * - kernel_dot_vec4        : SSE|AVX|SSE2
 *
 * Notes:
 * 1. For AVX float32:
 *    _mm256_store functions could potentially write contiguous data, so we
 *    rather use SSE instructions and let the compiler use AVX instructions
 *    mixed with XMM registers instead of YMM registers. Another option would
 *    be to use `maskload` instead of `load` to avoid these out-of-bounds writes
 */

namespace math {
namespace avx {

template <typename T>
using Vec4Buffer = typename Vector4<T>::BufferType;

template <typename T>
using SFINAE_VEC4_F32_AVX_GUARD =
    typename std::enable_if<CpuHasAVX<T>::value && IsFloat32<T>::value>::type*;

template <typename T>
using SFINAE_VEC4_F64_AVX_GUARD =
    typename std::enable_if<CpuHasAVX<T>::value && IsFloat64<T>::value>::type*;

template <typename T, SFINAE_VEC4_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_vec4(Vec4Buffer<T>& dst, const Vec4Buffer<T>& lhs,
                               const Vec4Buffer<T>& rhs) -> void {
    auto xmm_lhs = _mm_loadu_ps(lhs.data());
    auto xmm_rhs = _mm_loadu_ps(rhs.data());
    auto xmm_result = _mm_add_ps(xmm_lhs, xmm_rhs);
    _mm_storeu_ps(dst.data(), xmm_result);
}

template <typename T, SFINAE_VEC4_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_vec4(Vec4Buffer<T>& dst, const Vec4Buffer<T>& lhs,
                               const Vec4Buffer<T>& rhs) -> void {
    auto ymm_lhs = _mm256_loadu_pd(lhs.data());
    auto ymm_rhs = _mm256_loadu_pd(rhs.data());
    auto ymm_result = _mm256_add_pd(ymm_lhs, ymm_rhs);
    _mm256_storeu_pd(dst.data(), ymm_result);
}

template <typename T, SFINAE_VEC4_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_vec4(Vec4Buffer<T>& dst, const Vec4Buffer<T>& lhs,
                               const Vec4Buffer<T>& rhs) -> void {
    auto xmm_lhs = _mm_loadu_ps(lhs.data());
    auto xmm_rhs = _mm_loadu_ps(rhs.data());
    auto xmm_result = _mm_sub_ps(xmm_lhs, xmm_rhs);
    _mm_storeu_ps(dst.data(), xmm_result);
}

template <typename T, SFINAE_VEC4_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_vec4(Vec4Buffer<T>& dst, const Vec4Buffer<T>& lhs,
                               const Vec4Buffer<T>& rhs) -> void {
    auto ymm_lhs = _mm256_loadu_pd(lhs.data());
    auto ymm_rhs = _mm256_loadu_pd(rhs.data());
    auto ymm_result = _mm256_sub_pd(ymm_lhs, ymm_rhs);
    _mm256_storeu_pd(dst.data(), ymm_result);
}

template <typename T, SFINAE_VEC4_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_vec4(Vec4Buffer<T>& dst, T scale,
                                 const Vec4Buffer<T>& vec) -> void {
    auto xmm_scale = _mm_set1_ps(scale);
    auto xmm_vector = _mm_loadu_ps(vec.data());
    auto xmm_result = _mm_mul_ps(xmm_scale, xmm_vector);
    _mm_storeu_ps(dst.data(), xmm_result);
}

template <typename T, SFINAE_VEC4_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_vec4(Vec4Buffer<T>& dst, T scale,
                                 const Vec4Buffer<T>& vec) -> void {
    auto ymm_scale = _mm256_set1_pd(scale);
    auto ymm_vector = _mm256_loadu_pd(vec.data());
    auto ymm_result = _mm256_mul_pd(ymm_scale, ymm_vector);
    _mm256_storeu_pd(dst.data(), ymm_result);
}

template <typename T, SFINAE_VEC4_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_hadamard_vec4(Vec4Buffer<T>& dst,
                                    const Vec4Buffer<T>& lhs,
                                    const Vec4Buffer<T>& rhs) -> void {
    auto xmm_lhs = _mm_loadu_ps(lhs.data());
    auto xmm_rhs = _mm_loadu_ps(rhs.data());
    _mm_storeu_ps(dst.data(), _mm_mul_ps(xmm_lhs, xmm_rhs));
}

template <typename T, SFINAE_VEC4_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_hadamard_vec4(Vec4Buffer<T>& dst,
                                    const Vec4Buffer<T>& lhs,
                                    const Vec4Buffer<T>& rhs) -> void {
    auto ymm_lhs = _mm256_loadu_pd(lhs.data());
    auto ymm_rhs = _mm256_loadu_pd(rhs.data());
    _mm256_storeu_pd(dst.data(), _mm256_mul_pd(ymm_lhs, ymm_rhs));
}

template <typename T, SFINAE_VEC4_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_square_vec4(const Vec4Buffer<T>& vec) -> T {
    auto xmm_v = _mm_loadu_ps(vec.data());
    return _mm_cvtss_f32(_mm_dp_ps(xmm_v, xmm_v, 0xf1));
}

template <typename T, SFINAE_VEC4_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_square_vec4(const Vec4Buffer<T>& vec) -> T {
    // Implementation based on this post: https://bit.ly/3lt3ts4
    // Instruction-sets required (AVX, SSE2)
    // -------------------------
    // AVX:_mm256_loadu_pd,_mm256_mul_pd,_mm256_hadd_pd,_mm256_extractf128_pd
    // SSE2: _mm_add_pd, _mm_sqrt_pd, _mm_cvtsd_f64
    auto ymm_v = _mm256_loadu_pd(vec.data());
    auto ymm_prod = _mm256_mul_pd(ymm_v, ymm_v);
    auto ymm_hsum = _mm256_hadd_pd(ymm_prod, ymm_prod);
    auto xmm_lo_sum = _mm256_extractf128_pd(ymm_hsum, 0);
    auto xmm_hi_sum = _mm256_extractf128_pd(ymm_hsum, 1);
    auto xmm_result = _mm_add_pd(xmm_lo_sum, xmm_hi_sum);
    return _mm_cvtsd_f64(xmm_result);
}

template <typename T, SFINAE_VEC4_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_vec4(const Vec4Buffer<T>& vec) -> T {
    // Implementation based on this post: https://bit.ly/3FyZF0n
    auto xmm_v = _mm_loadu_ps(vec.data());
    return _mm_cvtss_f32(_mm_sqrt_ss(_mm_dp_ps(xmm_v, xmm_v, 0xf1)));
}

template <typename T, SFINAE_VEC4_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_vec4(const Vec4Buffer<T>& vec) -> T {
    // Implementation based on this post: https://bit.ly/3lt3ts4
    // Instruction-sets required (AVX, SSE2)
    // -------------------------
    // AVX: _mm256_loadu_pd,_mm256_mul_pd,_mm256_hadd_pd,_mm256_extractf128_pd
    // SSE2: _mm_add_pd,_mm_sqrt_pd,_mm_cvtsd_f64
    auto ymm_v = _mm256_loadu_pd(vec.data());
    auto ymm_prod = _mm256_mul_pd(ymm_v, ymm_v);
    auto ymm_hsum = _mm256_hadd_pd(ymm_prod, ymm_prod);
    auto xmm_lo_sum = _mm256_extractf128_pd(ymm_hsum, 0);
    auto xmm_hi_sum = _mm256_extractf128_pd(ymm_hsum, 1);
    auto xmm_result = _mm_sqrt_pd(_mm_add_pd(xmm_lo_sum, xmm_hi_sum));
    return _mm_cvtsd_f64(xmm_result);
}

template <typename T, SFINAE_VEC4_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_normalize_in_place_vec4(Vec4Buffer<T>& vec) -> void {
    // Implementation based on this post: https://bit.ly/3FyZF0n
    auto xmm_v = _mm_loadu_ps(vec.data());
    auto xmm_sums = _mm_dp_ps(xmm_v, xmm_v, 0xff);
    auto xmm_r_sqrt_sums = _mm_sqrt_ps(xmm_sums);
    auto xmm_v_norm = _mm_div_ps(xmm_v, xmm_r_sqrt_sums);
    _mm_storeu_ps(vec.data(), xmm_v_norm);
}

template <typename T, SFINAE_VEC4_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_normalize_in_place_vec4(Vec4Buffer<T>& vec) -> void {
    auto ymm_v = _mm256_loadu_pd(vec.data());
    auto ymm_prod = _mm256_mul_pd(ymm_v, ymm_v);
    // Construct the sum of squares into each double of a 256-bit register
    auto tmp_0 = _mm256_permute2f128_pd(ymm_prod, ymm_prod, 0x21);
    auto tmp_1 = _mm256_hadd_pd(ymm_prod, tmp_0);
    auto tmp_2 = _mm256_hadd_pd(tmp_1, tmp_1);  // here we have the {norm^2}
    // Construct a register with the norm in each entry (rsqrt quite imprecise)
    auto tmp_3 = _mm256_sqrt_pd(tmp_2);
    // Normalize the vector and store the result back
    auto ymm_normalized = _mm256_div_pd(ymm_v, tmp_3);
    _mm256_storeu_pd(vec.data(), ymm_normalized);
}

template <typename T, SFINAE_VEC4_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_dot_vec4(const Vec4Buffer<T>& lhs,
                               const Vec4Buffer<T>& rhs) -> T {
    auto xmm_lhs = _mm_loadu_ps(lhs.data());
    auto xmm_rhs = _mm_loadu_ps(rhs.data());
    auto xmm_cond_prod = _mm_dp_ps(xmm_lhs, xmm_rhs, 0xf1);
    return _mm_cvtss_f32(xmm_cond_prod);
}

template <typename T, SFINAE_VEC4_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_dot_vec4(const Vec4Buffer<T>& lhs,
                               const Vec4Buffer<T>& rhs) -> T {
    auto ymm_lhs = _mm256_loadu_pd(lhs.data());
    auto ymm_rhs = _mm256_loadu_pd(rhs.data());
    auto ymm_prod = _mm256_mul_pd(ymm_lhs, ymm_rhs);
    auto ymm_hsum = _mm256_hadd_pd(ymm_prod, ymm_prod);
    auto xmm_lo_sum = _mm256_extractf128_pd(ymm_hsum, 0);
    auto xmm_hi_sum = _mm256_extractf128_pd(ymm_hsum, 1);
    auto xmm_result = _mm_add_pd(xmm_lo_sum, xmm_hi_sum);
    return _mm_cvtsd_f64(xmm_result);
}

}  // namespace avx
}  // namespace math

#endif  // MATH_AVX_ENABLED
