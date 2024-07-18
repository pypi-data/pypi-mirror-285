#pragma once

#if defined(MATH_SSE_ENABLED) || defined(MATH_AVX_ENABLED)

#include <emmintrin.h>
#include <smmintrin.h>
#include <xmmintrin.h>

#include <math/vec2_t_decl.hpp>

/**
 * SSE instruction sets required for each kernel:
 *
 * - kernel_add_vec3                : SSE|SSE2
 * - kernel_sub_vec3                : SSE|SSE2
 * - kernel_scale_vec3              : SSE|SSE2
 * - kernel_hadamard_vec3           : SSE|SSE2
 * - kernel_length_square_vec3      : SSE|SSE2|SSE4.1
 * - kernel_length_vec3             : SSE|SSE2|SSE4.1
 * - kernel_normalize_in_place_vec3 : SSE|SSE2|SSE4.1
 * - kernel_dot_vec3                : SSE|SSE2|SSE4.1
 * - kernel_cross_vec3              : SSE
 *
 * Notes:
 * 1. For SSE-float32:
 *  - @note(wilbert): data is not aligned to the width of an xmm-register, so
 *      we use the unaligned version of the load/store intrinsic functions
 *  - @note(wilbert): data buffer is smaller than the width of an xmm register,
 *      which might load 8 bytes not related to the vector. This might be ok;
 *      however, for stores we need to only touch 2 floats, or else we'll
 *      corrupt 2 bytes from any object that might be allocated right next to it
 *
 * 2. For SSE-float64:
 *  - @note(wilbert): All elements of the buffer (2xf64) fit into a single xmm
 *      register (128-bits <=> 2xfloat64)
 *
 * 3. Note that we're using the same SSE kernels for the AVX versions
 */

namespace math {
namespace sse {

template <typename T>
using Vec2Buffer = typename Vector2<T>::BufferType;

template <typename T>
using SFINAE_VEC2_F32_SSE_GUARD =
    typename std::enable_if<(CpuHasSSE<T>::value || CpuHasAVX<T>::value) &&
                            IsFloat32<T>::value>::type*;

template <typename T>
using SFINAE_VEC2_F64_SSE_GUARD =
    typename std::enable_if<(CpuHasSSE<T>::value || CpuHasAVX<T>::value) &&
                            IsFloat64<T>::value>::type*;

template <typename T, SFINAE_VEC2_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_vec2(Vec2Buffer<T>& dst, const Vec2Buffer<T>& lhs,
                               const Vec2Buffer<T>& rhs) -> void {
    auto xmm_lhs = _mm_loadu_ps(lhs.data());
    auto xmm_rhs = _mm_loadu_ps(rhs.data());
    auto xmm_result = _mm_add_ps(xmm_lhs, xmm_rhs);
    _mm_storel_pi(reinterpret_cast<__m64*>(dst.data()), xmm_result);  // NOLINT
}

template <typename T, SFINAE_VEC2_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_vec2(Vec2Buffer<T>& dst, const Vec2Buffer<T>& lhs,
                               const Vec2Buffer<T>& rhs) -> void {
    auto xmm_lhs = _mm_loadu_pd(lhs.data());
    auto xmm_rhs = _mm_loadu_pd(rhs.data());
    auto xmm_result = _mm_add_pd(xmm_lhs, xmm_rhs);
    _mm_storeu_pd(dst.data(), xmm_result);
}

template <typename T, SFINAE_VEC2_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_vec2(Vec2Buffer<T>& dst, const Vec2Buffer<T>& lhs,
                               const Vec2Buffer<T>& rhs) -> void {
    auto xmm_lhs = _mm_loadu_ps(lhs.data());
    auto xmm_rhs = _mm_loadu_ps(rhs.data());
    auto xmm_result = _mm_sub_ps(xmm_lhs, xmm_rhs);
    _mm_storel_pi(reinterpret_cast<__m64*>(dst.data()), xmm_result);  // NOLINT
}

template <typename T, SFINAE_VEC2_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_vec2(Vec2Buffer<T>& dst, const Vec2Buffer<T>& lhs,
                               const Vec2Buffer<T>& rhs) -> void {
    auto xmm_lhs = _mm_loadu_pd(lhs.data());
    auto xmm_rhs = _mm_loadu_pd(rhs.data());
    auto xmm_result = _mm_sub_pd(xmm_lhs, xmm_rhs);
    _mm_storeu_pd(dst.data(), xmm_result);
}

template <typename T, SFINAE_VEC2_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_vec2(Vec2Buffer<T>& dst, T scale,
                                 const Vec2Buffer<T>& vec) -> void {
    auto xmm_scale = _mm_set1_ps(scale);
    auto xmm_vector = _mm_loadu_ps(vec.data());
    auto xmm_result = _mm_mul_ps(xmm_scale, xmm_vector);
    _mm_storel_pi(reinterpret_cast<__m64*>(dst.data()), xmm_result);  // NOLINT
}

template <typename T, SFINAE_VEC2_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_vec2(Vec2Buffer<T>& dst, T scale,
                                 const Vec2Buffer<T>& vec) -> void {
    auto xmm_scale = _mm_set1_pd(scale);
    auto xmm_vector = _mm_loadu_pd(vec.data());
    auto xmm_result = _mm_mul_pd(xmm_scale, xmm_vector);
    _mm_storeu_pd(dst.data(), xmm_result);
}

template <typename T, SFINAE_VEC2_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_hadamard_vec2(Vec2Buffer<T>& dst,
                                    const Vec2Buffer<T>& lhs,
                                    const Vec2Buffer<T>& rhs) -> void {
    auto xmm_lhs = _mm_loadu_ps(lhs.data());
    auto xmm_rhs = _mm_loadu_ps(rhs.data());
    auto xmm_result = _mm_mul_ps(xmm_lhs, xmm_rhs);
    _mm_storel_pi(reinterpret_cast<__m64*>(dst.data()), xmm_result);  // NOLINT
}

template <typename T, SFINAE_VEC2_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_hadamard_vec2(Vec2Buffer<T>& dst,
                                    const Vec2Buffer<T>& lhs,
                                    const Vec2Buffer<T>& rhs) -> void {
    auto xmm_lhs = _mm_loadu_pd(lhs.data());
    auto xmm_rhs = _mm_loadu_pd(rhs.data());
    auto xmm_result = _mm_mul_pd(xmm_lhs, xmm_rhs);
    _mm_storeu_pd(dst.data(), xmm_result);
}

template <typename T, SFINAE_VEC2_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_square_vec2(const Vec2Buffer<T>& vec) -> T {
    // Implementation based on this post: https://bit.ly/3FyZF0n
    auto xmm_v = _mm_loadu_ps(vec.data());
    auto xmm_square_sum = _mm_dp_ps(xmm_v, xmm_v, 0x31);
    return _mm_cvtss_f32(xmm_square_sum);
}

template <typename T, SFINAE_VEC2_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_square_vec2(const Vec2Buffer<T>& vec) -> T {
    // Implementation based on this post: https://bit.ly/3FyZF0n
    auto xmm_v = _mm_loadu_pd(vec.data());
    auto xmm_square_sum = _mm_dp_pd(xmm_v, xmm_v, 0x31);
    return _mm_cvtsd_f64(xmm_square_sum);
}

template <typename T, SFINAE_VEC2_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_vec2(const Vec2Buffer<T>& vec) -> T {
    // Implementation based on this post: https://bit.ly/3FyZF0n
    auto xmm_v = _mm_loadu_ps(vec.data());
    auto xmm_square_sum = _mm_dp_ps(xmm_v, xmm_v, 0x31);
    return _mm_cvtss_f32(_mm_sqrt_ss(xmm_square_sum));
}

template <typename T, SFINAE_VEC2_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_vec2(const Vec2Buffer<T>& vec) -> T {
    // Implementation based on this post: https://bit.ly/3FyZF0n
    auto xmm_v = _mm_loadu_pd(vec.data());
    auto xmm_square_sum = _mm_dp_pd(xmm_v, xmm_v, 0x31);
    return _mm_cvtsd_f64(_mm_sqrt_sd(xmm_square_sum, xmm_square_sum));
}

template <typename T, SFINAE_VEC2_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_normalize_in_place_vec2(Vec2Buffer<T>& vec) -> void {
    // Implementation based on this post: https://bit.ly/3FyZF0n
    auto xmm_v = _mm_loadu_ps(vec.data());
    auto xmm_sums = _mm_dp_ps(xmm_v, xmm_v, 0x3f);
    auto xmm_r_sqrt_sums = _mm_sqrt_ps(xmm_sums);
    auto xmm_v_norm = _mm_div_ps(xmm_v, xmm_r_sqrt_sums);
    _mm_storel_pi(reinterpret_cast<__m64*>(vec.data()), xmm_v_norm);  // NOLINT
}

template <typename T, SFINAE_VEC2_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_normalize_in_place_vec2(Vec2Buffer<T>& vec) -> void {
    // Implementation based on this post: https://bit.ly/3FyZF0n
    auto xmm_v = _mm_loadu_pd(vec.data());
    auto xmm_sums = _mm_dp_pd(xmm_v, xmm_v, 0x33);
    auto xmm_r_sqrt_sums = _mm_sqrt_pd(xmm_sums);
    auto xmm_v_norm = _mm_div_pd(xmm_v, xmm_r_sqrt_sums);
    _mm_storeu_pd(vec.data(), xmm_v_norm);
}

template <typename T, SFINAE_VEC2_F32_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_dot_vec2(const Vec2Buffer<T>& lhs,
                               const Vec2Buffer<T>& rhs) -> T {
    auto xmm_lhs = _mm_loadu_ps(lhs.data());
    auto xmm_rhs = _mm_loadu_ps(rhs.data());
    auto xmm_cond_prod = _mm_dp_ps(xmm_lhs, xmm_rhs, 0x31);
    return _mm_cvtss_f32(xmm_cond_prod);
}

template <typename T, SFINAE_VEC2_F64_SSE_GUARD<T> = nullptr>
LM_INLINE auto kernel_dot_vec2(const Vec2Buffer<T>& lhs,
                               const Vec2Buffer<T>& rhs) -> T {
    auto xmm_lhs = _mm_loadu_pd(lhs.data());
    auto xmm_rhs = _mm_loadu_pd(rhs.data());
    auto xmm_dot = _mm_dp_pd(xmm_lhs, xmm_rhs, 0x31);
    return _mm_cvtsd_f64(xmm_dot);
}

}  // namespace sse
}  // namespace math

#endif  // MATH_SSE_ENABLED || MATH_AVX_ENABLED
