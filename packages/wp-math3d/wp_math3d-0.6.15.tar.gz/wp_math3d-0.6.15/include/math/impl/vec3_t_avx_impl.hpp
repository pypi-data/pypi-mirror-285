#pragma once

#if defined(MATH_AVX_ENABLED)

#include <immintrin.h>

#include <math/vec3_t_decl.hpp>

/**
 * AVX instruction sets required for each kernel:
 *
 * - kernel_add_vec3                : AVX|SSE|SSE2
 * - kernel_sub_vec3                : AVX|SSE|SSE2
 * - kernel_scale_vec3              : AVX|SSE|SSE2
 * - kernel_hadamard_vec3           : AVX|SSE|SSE2
 * - kernel_length_square_vec3      : AVX|SSE|SSE2|SSE4.1
 * - kernel_length_vec3             : AVX|SSE|SSE2|SSE4.1
 * - kernel_normalize_in_place_vec3 : AVX|SSE|SSE2|SSE4.1
 * - kernel_dot_vec3                : AVX|SSE|SSE2|SSE4.1
 * - kernel_cross_vec3              : AVX|SSE
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
using Vec3Buffer = typename Vector3<T>::BufferType;

template <typename T>
using SFINAE_VEC3_F32_AVX_GUARD =
    typename std::enable_if<CpuHasAVX<T>::value && IsFloat32<T>::value>::type*;

template <typename T>
using SFINAE_VEC3_F64_AVX_GUARD =
    typename std::enable_if<CpuHasAVX<T>::value && IsFloat64<T>::value>::type*;

template <typename T, SFINAE_VEC3_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_vec3(Vec3Buffer<T>& dst, const Vec3Buffer<T>& lhs,
                               const Vec3Buffer<T>& rhs) -> void {
    auto xmm_lhs = _mm_loadu_ps(lhs.data());
    auto xmm_rhs = _mm_loadu_ps(rhs.data());
    auto xmm_result = _mm_add_ps(xmm_lhs, xmm_rhs);
    _mm_storeu_ps(dst.data(), xmm_result);
}

template <typename T, SFINAE_VEC3_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_vec3(Vec3Buffer<T>& dst, const Vec3Buffer<T>& lhs,
                               const Vec3Buffer<T>& rhs) -> void {
    auto ymm_lhs = _mm256_loadu_pd(lhs.data());
    auto ymm_rhs = _mm256_loadu_pd(rhs.data());
    auto ymm_result = _mm256_add_pd(ymm_lhs, ymm_rhs);
    _mm256_storeu_pd(dst.data(), ymm_result);
}

template <typename T, SFINAE_VEC3_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_vec3(Vec3Buffer<T>& dst, const Vec3Buffer<T>& lhs,
                               const Vec3Buffer<T>& rhs) -> void {
    auto xmm_lhs = _mm_loadu_ps(lhs.data());
    auto xmm_rhs = _mm_loadu_ps(rhs.data());
    auto xmm_result = _mm_sub_ps(xmm_lhs, xmm_rhs);
    _mm_storeu_ps(dst.data(), xmm_result);
}

template <typename T, SFINAE_VEC3_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_vec3(Vec3Buffer<T>& dst, const Vec3Buffer<T>& lhs,
                               const Vec3Buffer<T>& rhs) -> void {
    auto ymm_lhs = _mm256_loadu_pd(lhs.data());
    auto ymm_rhs = _mm256_loadu_pd(rhs.data());
    auto ymm_result = _mm256_sub_pd(ymm_lhs, ymm_rhs);
    _mm256_storeu_pd(dst.data(), ymm_result);
}

template <typename T, SFINAE_VEC3_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_vec3(Vec3Buffer<T>& dst, T scale,
                                 const Vec3Buffer<T>& vec) -> void {
    auto xmm_scale = _mm_set1_ps(scale);
    auto xmm_vector = _mm_loadu_ps(vec.data());
    auto xmm_result = _mm_mul_ps(xmm_scale, xmm_vector);
    _mm_storeu_ps(dst.data(), xmm_result);
}

template <typename T, SFINAE_VEC3_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_vec3(Vec3Buffer<T>& dst, T scale,
                                 const Vec3Buffer<T>& vec) -> void {
    auto ymm_scale = _mm256_set1_pd(scale);
    auto ymm_vector = _mm256_loadu_pd(vec.data());
    auto ymm_result = _mm256_mul_pd(ymm_scale, ymm_vector);
    _mm256_storeu_pd(dst.data(), ymm_result);
}

template <typename T, SFINAE_VEC3_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_hadamard_vec3(Vec3Buffer<T>& dst,
                                    const Vec3Buffer<T>& lhs,
                                    const Vec3Buffer<T>& rhs) -> void {
    auto xmm_lhs = _mm_loadu_ps(lhs.data());
    auto xmm_rhs = _mm_loadu_ps(rhs.data());
    _mm_storeu_ps(dst.data(), _mm_mul_ps(xmm_lhs, xmm_rhs));
}

template <typename T, SFINAE_VEC3_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_hadamard_vec3(Vec3Buffer<T>& dst,
                                    const Vec3Buffer<T>& lhs,
                                    const Vec3Buffer<T>& rhs) -> void {
    auto ymm_lhs = _mm256_loadu_pd(lhs.data());
    auto ymm_rhs = _mm256_loadu_pd(rhs.data());
    _mm256_storeu_pd(dst.data(), _mm256_mul_pd(ymm_lhs, ymm_rhs));
}

template <typename T, SFINAE_VEC3_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_square_vec3(const Vec3Buffer<T>& vec) -> T {
    // Implementation based on this post: https://bit.ly/3FyZF0n
    auto xmm_v = _mm_loadu_ps(vec.data());
    return _mm_cvtss_f32(_mm_dp_ps(xmm_v, xmm_v, 0x71));
}

template <typename T, SFINAE_VEC3_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_square_vec3(const Vec3Buffer<T>& vec) -> T {
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

template <typename T, SFINAE_VEC3_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_vec3(const Vec3Buffer<T>& vec) -> T {
    // Implementation based on this post: https://bit.ly/3FyZF0n
    auto xmm_v = _mm_loadu_ps(vec.data());
    return _mm_cvtss_f32(_mm_sqrt_ss(_mm_dp_ps(xmm_v, xmm_v, 0x71)));
}

template <typename T, SFINAE_VEC3_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_vec3(const Vec3Buffer<T>& vec) -> T {
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

template <typename T, SFINAE_VEC3_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_normalize_in_place_vec3(Vec3Buffer<T>& vec) -> void {
    // Implementation based on this post: https://bit.ly/3FyZF0n
    auto xmm_v = _mm_loadu_ps(vec.data());
    auto xmm_sums = _mm_dp_ps(xmm_v, xmm_v, 0x7f);
    auto xmm_r_sqrt_sums = _mm_sqrt_ps(xmm_sums);
    auto xmm_v_norm = _mm_div_ps(xmm_v, xmm_r_sqrt_sums);
    _mm_storeu_ps(vec.data(), xmm_v_norm);
}

template <typename T, SFINAE_VEC3_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_normalize_in_place_vec3(Vec3Buffer<T>& vec) -> void {
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

template <typename T, SFINAE_VEC3_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_dot_vec3(const Vec3Buffer<T>& lhs,
                               const Vec3Buffer<T>& rhs) -> T {
    auto xmm_lhs = _mm_loadu_ps(lhs.data());
    auto xmm_rhs = _mm_loadu_ps(rhs.data());
    auto xmm_cond_prod = _mm_dp_ps(xmm_lhs, xmm_rhs, 0x71);
    return _mm_cvtss_f32(xmm_cond_prod);
}

template <typename T, SFINAE_VEC3_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_dot_vec3(const Vec3Buffer<T>& lhs,
                               const Vec3Buffer<T>& rhs) -> T {
    auto ymm_lhs = _mm256_loadu_pd(lhs.data());
    auto ymm_rhs = _mm256_loadu_pd(rhs.data());
    auto ymm_prod = _mm256_mul_pd(ymm_lhs, ymm_rhs);
    auto ymm_hsum = _mm256_hadd_pd(ymm_prod, ymm_prod);
    auto xmm_lo_sum = _mm256_extractf128_pd(ymm_hsum, 0);
    auto xmm_hi_sum = _mm256_extractf128_pd(ymm_hsum, 1);
    auto xmm_result = _mm_add_pd(xmm_lo_sum, xmm_hi_sum);
    return _mm_cvtsd_f64(xmm_result);
}

template <typename T, SFINAE_VEC3_F32_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_cross_vec3(Vec3Buffer<T>& dst, const Vec3Buffer<T>& lhs,
                                 const Vec3Buffer<T>& rhs) -> void {
    // Implementation adapted from @ian_mallett (https://bit.ly/3lu6pVe)
    // Recall that the dot product of two 3d-vectors a and b given by:
    // a = {a[0], a[1], a[2], a[3]=0}, b = {b[0], b[1], b[2], b[3]=0}
    // has as resulting expression:
    // a (x) b = [a[1] * b[2] - a[2] * b[1],
    //            a[2] * b[0] - a[0] * b[2],
    //            a[0] * b[1] - a[1] * b[0],
    //                        0            ]
    auto vec_a = _mm_loadu_ps(lhs.data());  // a = {a[0], a[1], a[2], a[3]=0}
    auto vec_b = _mm_loadu_ps(rhs.data());  // b = {b[0], b[1], b[2], b[3]=0}
    // tmp_0 = {a[1], a[2], a[0], 0}
    auto tmp_0 = _mm_shuffle_ps(
        vec_a, vec_a, static_cast<int>(math::ShuffleMask<3, 0, 2, 1>::value));
    // tmp_1 = {b[2], b[0], b[1], 0}
    auto tmp_1 = _mm_shuffle_ps(
        vec_b, vec_b, static_cast<int>(math::ShuffleMask<3, 1, 0, 2>::value));
    // tmp_2 = {a[2], a[0], a[1], 0}
    auto tmp_2 = _mm_shuffle_ps(
        vec_a, vec_a, static_cast<int>(math::ShuffleMask<3, 1, 0, 2>::value));
    // tmp_3 = {b[1], b[2], b[0], 0}
    auto tmp_3 = _mm_shuffle_ps(
        vec_b, vec_b, static_cast<int>(math::ShuffleMask<3, 0, 2, 1>::value));
    _mm_storeu_ps(dst.data(), _mm_sub_ps(_mm_mul_ps(tmp_0, tmp_1),
                                         _mm_mul_ps(tmp_2, tmp_3)));
}

template <typename T, SFINAE_VEC3_F64_AVX_GUARD<T> = nullptr>
LM_INLINE auto kernel_cross_vec3(Vec3Buffer<T>& dst, const Vec3Buffer<T>& lhs,
                                 const Vec3Buffer<T>& rhs) -> void {
    // Implementation adapted from @ian_mallett (https://bit.ly/3lu6pVe)
    auto vec_a = _mm256_loadu_pd(lhs.data());
    auto vec_b = _mm256_loadu_pd(rhs.data());

    // Construct both {a[1], a[2], a[0], 0} and {a[2], a[0], a[1], 0} **********
    auto tmp_0a = _mm256_permute2f128_pd(vec_a, vec_a, 0x21);
    auto tmp_1a = _mm256_permute_pd(vec_a, 0x09);
    auto tmp_2a = _mm256_permute_pd(tmp_0a, 0x05);
    // Constructing {a[2], a[0], a[1], 0}
    auto tmp_3a = _mm256_blend_pd(tmp_0a, tmp_1a, 0x0e);
    auto tmp_4a = _mm256_blend_pd(tmp_2a, tmp_3a, 0x0b);  // {a[2],a[0],a[1],0}
    // Constructing {a[1], a[2], a[0], 0}
    auto tmp_5a = _mm256_blend_pd(tmp_1a, tmp_2a, 0x02);
    auto tmp_6a = _mm256_blend_pd(tmp_0a, tmp_5a, 0x0b);  // {a[1],a[2],a[0],0}
    // *************************************************************************

    // Construct both {b[1], b[2], b[0], 0} and {b[2], b[0], b[1], 0} **********
    auto tmp_0b = _mm256_permute2f128_pd(vec_b, vec_b, 0x21);
    auto tmp_1b = _mm256_permute_pd(vec_b, 0x09);
    auto tmp_2b = _mm256_permute_pd(tmp_0b, 0x05);
    // Constructing {a[2], a[0], a[1], 0}
    auto tmp_3b = _mm256_blend_pd(tmp_0b, tmp_1b, 0x0e);
    auto tmp_4b = _mm256_blend_pd(tmp_2b, tmp_3b, 0x0b);  // {b[2],b[0],b[1],0}
    // Constructing {a[1], a[2], a[0], 0}
    auto tmp_5b = _mm256_blend_pd(tmp_1b, tmp_2b, 0x02);
    auto tmp_6b = _mm256_blend_pd(tmp_0b, tmp_5b, 0x0b);  // {b[1],b[2],b[0],0}
    // *************************************************************************
    _mm256_storeu_pd(dst.data(), _mm256_sub_pd(_mm256_mul_pd(tmp_6a, tmp_4b),
                                               _mm256_mul_pd(tmp_4a, tmp_6b)));
    // @todo(wilbert): replace permutation madness with "permute4x64_pd" (AVX2)
}

}  // namespace avx
}  // namespace math

#endif  // MATH_AVX_ENABLED
