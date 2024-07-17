#pragma once

#include <cmath>

#include <math/vec3_t_decl.hpp>

namespace math {
namespace scalar {

template <typename T>
using Vec3Buffer = typename Vector3<T>::BufferType;

template <typename T>
using SFINAE_VEC3_SCALAR_GUARD =
    typename std::enable_if<IsScalar<T>::value>::type*;

template <typename T, SFINAE_VEC3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_add_vec3(Vec3Buffer<T>& dst, const Vec3Buffer<T>& lhs,
                               const Vec3Buffer<T>& rhs) -> void {
    for (uint32_t i = 0; i < Vector3<T>::VECTOR_SIZE; ++i) {
        dst[i] = lhs[i] + rhs[i];
    }
}

template <typename T, SFINAE_VEC3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_sub_vec3(Vec3Buffer<T>& dst, const Vec3Buffer<T>& lhs,
                               const Vec3Buffer<T>& rhs) -> void {
    for (uint32_t i = 0; i < Vector3<T>::VECTOR_SIZE; ++i) {
        dst[i] = lhs[i] - rhs[i];
    }
}

template <typename T, SFINAE_VEC3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_scale_vec3(Vec3Buffer<T>& dst, T scale,
                                 const Vec3Buffer<T>& vec) -> void {
    for (uint32_t i = 0; i < Vector3<T>::VECTOR_SIZE; ++i) {
        dst[i] = scale * vec[i];
    }
}

template <typename T, SFINAE_VEC3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_hadamard_vec3(Vec3Buffer<T>& dst,
                                    const Vec3Buffer<T>& lhs,
                                    const Vec3Buffer<T>& rhs) -> void {
    for (uint32_t i = 0; i < Vector3<T>::VECTOR_SIZE; ++i) {
        dst[i] = lhs[i] * rhs[i];
    }
}

template <typename T, SFINAE_VEC3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_length_square_vec3(const Vec3Buffer<T>& vec) -> T {
    T accum = static_cast<T>(0.0);
    for (uint32_t i = 0; i < Vector3<T>::VECTOR_SIZE; ++i) {
        accum += vec[i] * vec[i];
    }
    return accum;
}

template <typename T, SFINAE_VEC3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_normalize_in_place_vec3(Vec3Buffer<T>& vec) -> void {
    auto length = std::sqrt(kernel_length_square_vec3<T>(vec));
    for (uint32_t i = 0; i < Vector3<T>::VECTOR_SIZE; ++i) {
        vec[i] /= length;
    }
}

template <typename T, SFINAE_VEC3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_dot_vec3(const Vec3Buffer<T>& lhs,
                               const Vec3Buffer<T>& rhs) -> T {
    T accum = static_cast<T>(0.0);
    for (uint32_t i = 0; i < Vector3<T>::VECTOR_SIZE; ++i) {
        accum += lhs[i] * rhs[i];
    }
    return accum;
}

template <typename T, SFINAE_VEC3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_compare_eq_vec3(const Vec3Buffer<T>& lhs,
                                      const Vec3Buffer<T>& rhs) -> bool {
    for (uint32_t i = 0; i < Vector3<T>::VECTOR_SIZE; ++i) {
        if (std::abs(lhs[i] - rhs[i]) >= static_cast<T>(math::EPS)) {
            return false;
        }
    }
    return true;
}

template <typename T, SFINAE_VEC3_SCALAR_GUARD<T> = nullptr>
LM_INLINE auto kernel_cross_vec3(Vec3Buffer<T>& dst, const Vec3Buffer<T>& lhs,
                                 const Vec3Buffer<T>& rhs) -> void {
    // v.x =  v1.y  *  v2.z  -  v1.z  *  v2.y
    dst[0] = lhs[1] * rhs[2] - lhs[2] * rhs[1];
    // v.y =  v1.z  *  v2.x  -  v1.x  *  v2.z
    dst[1] = lhs[2] * rhs[0] - lhs[0] * rhs[2];
    // v.z =  v1.x  *  v2.y  -  v1.y  *  v2.x
    dst[2] = lhs[0] * rhs[1] - lhs[1] * rhs[0];
}

}  // namespace scalar
}  // namespace math
