#include <catch2/catch.hpp>
#include <math/vec2_t.hpp>
#include <math/vec3_t.hpp>
#include <math/vec4_t.hpp>
#include <math/mat2_t.hpp>
#include <math/mat3_t.hpp>
#include <math/mat4_t.hpp>
#include <math/quat_t.hpp>
#include <math/euler_t.hpp>
#include "math/euler_t_decl.hpp"

// NOLINTNEXTLINE
#define gen_random_value(T, range_min, range_max, Nsamples)   \
    GENERATE(take(Nsamples, random(static_cast<T>(range_min), \
                                   static_cast<T>(range_max))))

namespace math {

template <typename T>
constexpr auto func_value_close(T a, T b, T eps) -> bool {
    return ((a - b) < eps) && ((a - b) > -eps);
}

template <typename T>
constexpr auto func_all_close(const ::math::Vector2<T>& vec, T x, T y, T eps)
    -> bool {
    return func_value_close(vec.x(), x, eps) &&
           func_value_close(vec.y(), y, eps);
}

template <typename T>
constexpr auto func_all_close(const ::math::Vector3<T>& vec, T x, T y, T z,
                              T eps) -> bool {
    return func_value_close(vec.x(), x, eps) &&
           func_value_close(vec.y(), y, eps) &&
           func_value_close(vec.z(), z, eps);
}

template <typename T>
constexpr auto func_all_close(const ::math::Vector4<T>& vec, T x, T y, T z, T w,
                              T eps) -> bool {
    return func_value_close(vec.x(), x, eps) &&
           func_value_close(vec.y(), y, eps) &&
           func_value_close(vec.z(), z, eps) &&
           func_value_close(vec.w(), w, eps);
}

// clang-format off
template <typename T>
constexpr auto func_all_close(const ::math::Matrix2<T>& mat,
                              T x00, T x01,
                              T x10, T x11, T eps) -> bool {
    return func_value_close<T>(mat(0, 0), x00, eps) &&
           func_value_close<T>(mat(0, 1), x01, eps) &&
           func_value_close<T>(mat(1, 0), x10, eps) &&
           func_value_close<T>(mat(1, 1), x11, eps);
}

template <typename T>
constexpr auto func_all_close(const ::math::Matrix3<T>& mat,
                              T x00, T x01, T x02,
                              T x10, T x11, T x12,
                              T x20, T x21, T x22, T eps) -> bool {
    return func_value_close<T>(mat(0, 0), x00, eps) &&
           func_value_close<T>(mat(0, 1), x01, eps) &&
           func_value_close<T>(mat(0, 2), x02, eps) &&

           func_value_close<T>(mat(1, 0), x10, eps) &&
           func_value_close<T>(mat(1, 1), x11, eps) &&
           func_value_close<T>(mat(1, 2), x12, eps) &&

           func_value_close<T>(mat(2, 0), x20, eps) &&
           func_value_close<T>(mat(2, 1), x21, eps) &&
           func_value_close<T>(mat(2, 2), x22, eps);
}

template <typename T>
constexpr auto func_all_close(const ::math::Matrix4<T>& mat,
                              T x00, T x01, T x02, T x03,
                              T x10, T x11, T x12, T x13,
                              T x20, T x21, T x22, T x23,
                              T x30, T x31, T x32, T x33, T eps) -> bool {
    return func_value_close<T>(mat(0, 0), x00, eps) &&
           func_value_close<T>(mat(0, 1), x01, eps) &&
           func_value_close<T>(mat(0, 2), x02, eps) &&
           func_value_close<T>(mat(0, 3), x03, eps) &&

           func_value_close<T>(mat(1, 0), x10, eps) &&
           func_value_close<T>(mat(1, 1), x11, eps) &&
           func_value_close<T>(mat(1, 2), x12, eps) &&
           func_value_close<T>(mat(1, 3), x13, eps) &&

           func_value_close<T>(mat(2, 0), x20, eps) &&
           func_value_close<T>(mat(2, 1), x21, eps) &&
           func_value_close<T>(mat(2, 2), x22, eps) &&
           func_value_close<T>(mat(2, 3), x23, eps) &&

           func_value_close<T>(mat(3, 0), x30, eps) &&
           func_value_close<T>(mat(3, 1), x31, eps) &&
           func_value_close<T>(mat(3, 2), x32, eps) &&
           func_value_close<T>(mat(3, 3), x33, eps);
}
// clang-format on

template <typename T>
constexpr auto func_all_close(const ::math::Quaternion<T>& quat, T w, T x, T y,
                              T z, T eps) -> bool {
    return func_value_close<T>(quat.w(), w, eps) &&
           func_value_close<T>(quat.x(), x, eps) &&
           func_value_close<T>(quat.y(), y, eps) &&
           func_value_close<T>(quat.z(), z, eps);
}

template <typename T>
constexpr auto func_all_close(const ::math::Euler<T>& euler, T ex, T ey, T ez,
                              T eps) -> bool {
    return func_value_close<T>(euler.x, ex, eps) &&
           func_value_close<T>(euler.y, ey, eps) &&
           func_value_close<T>(euler.z, ez, eps);
}

}  // namespace math
