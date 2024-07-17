#pragma once

#include <cmath>
#include <string>

#include <math/euler_t_decl.hpp>

#include <math/quat_t.hpp>
#include <math/mat3_t.hpp>
#include <math/mat4_t.hpp>

namespace math {

namespace euler {

auto ToString(const Order& p_order) -> std::string {
    switch (p_order) {
        case Order::XYZ:
            return "XYZ";
        case Order::YZX:
            return "YZX";
        case Order::ZXY:
            return "ZXY";
        case Order::XZY:
            return "XZY";
        case Order::YXZ:
            return "YXZ";
        case Order::ZYX:
            return "ZYX";
        default:
            return "Undefined";
    }
}

auto ToString(const Convention& p_convention) -> std::string {
    switch (p_convention) {
        case Convention::INTRINSIC:
            return "Intrinsic";
        case Convention::EXTRINSIC:
            return "Extrinsic";
        default:
            return "Undefined";
    }
}

}  // namespace euler

// ***************************************************************************//
//                       Factory functions implementation                     //
// ***************************************************************************//

template <typename T>
auto Euler<T>::setFromRotationMatrix(const Mat3& m) -> void {
    // Implementation based on ThreeJS Euler.js implementation [0]

    constexpr T ONE = static_cast<T>(1.0);
    constexpr T ZERO = static_cast<T>(0.0);
    constexpr T EPSILON = static_cast<T>(1e-6);
    constexpr T SIN_MIN = -ONE;
    constexpr T SIN_MAX = ONE;
    constexpr T ONE_MINUS_EPS = ONE - EPSILON;

    if (this->convention != euler::Convention::INTRINSIC) {
        // TODO(wilbert): handle general case using the implementation from [1]
        return;
    }

    // clang-format off
    auto m11 = m(0, 0); auto m12 = m(0, 1); auto m13 = m(0, 2);
    auto m21 = m(1, 0); auto m22 = m(1, 1); auto m23 = m(1, 2);
    auto m31 = m(2, 0); auto m32 = m(2, 1); auto m33 = m(2, 2);
    // clang-format on

    switch (this->order) {
        case euler::Order::XYZ: {
            this->y = std::asin(clamp(m13, SIN_MIN, SIN_MAX));
            if (std::abs(m13) < ONE_MINUS_EPS) {
                this->x = std::atan2(-m23, m33);
                this->z = std::atan2(-m12, m11);
            } else {
                this->x = std::atan2(m32, m22);
                this->z = ZERO;
            }
            break;
        }
        case euler::Order::YXZ: {
            this->x = std::asin(-clamp(m23, SIN_MIN, SIN_MAX));
            if (std::abs(m23) < ONE_MINUS_EPS) {
                this->y = std::atan2(m13, m33);
                this->z = std::atan2(m21, m22);
            } else {
                this->y = std::atan2(-m31, m11);
                this->z = ZERO;
            }
            break;
        }
        case euler::Order::ZXY: {
            this->x = std::asin(clamp(m32, SIN_MIN, SIN_MAX));
            if (std::abs(m32) < ONE_MINUS_EPS) {
                this->y = std::atan2(-m31, m33);
                this->z = std::atan2(-m12, m22);
            } else {
                this->y = ZERO;
                this->z = std::atan2(m21, m11);
            }
            break;
        }
        case euler::Order::ZYX: {
            this->y = std::asin(-clamp(m31, SIN_MIN, SIN_MAX));
            if (std::abs(m31) < ONE_MINUS_EPS) {
                this->x = std::atan2(m32, m33);
                this->z = std::atan2(m21, m11);
            } else {
                this->x = ZERO;
                this->z = std::atan2(-m12, m22);
            }
            break;
        }
        case euler::Order::YZX: {
            this->z = std::asin(clamp(m21, SIN_MIN, SIN_MAX));
            if (std::abs(m21) < ONE_MINUS_EPS) {
                this->x = std::atan2(-m23, m22);
                this->y = std::atan2(-m31, m11);
            } else {
                this->x = ZERO;
                this->y = std::atan2(m13, m33);
            }
            break;
        }
        case euler::Order::XZY: {
            this->z = std::asin(-clamp(m12, SIN_MIN, SIN_MAX));
            if (std::abs(m12) < ONE_MINUS_EPS) {
                this->x = std::atan2(m32, m22);
                this->y = std::atan2(m13, m11);
            } else {
                this->x = std::atan2(-m23, m33);
                this->y = ZERO;
            }
            break;
        }
    }
}

template <typename T>
auto Euler<T>::setFromTransform(const Mat4& m) -> void {
    // clang-format off
    Mat3 mat_3(m(0, 0), m(0, 1), m(0, 2),
               m(1, 0), m(1, 1), m(1, 2),
               m(2, 0), m(2, 1), m(2, 2));
    // clang-format on
    setFromRotationMatrix(mat_3);
}

template <typename T>
auto Euler<T>::setFromQuaternion(const Quat& quaternion) -> void {
    setFromRotationMatrix(Mat3(quaternion));
}

template <typename T>
auto Euler<T>::setFromAxisAngle(const Vec3& axis, T angle) -> void {
    setFromQuaternion(Quat(axis, angle));
}

// ***************************************************************************//
//                    Euler Angles operations and functions                   //
// ***************************************************************************//

template <typename T>
using SFINAE_EULER_GUARD = typename std::enable_if<IsScalar<T>::value>::type*;

template <typename T, SFINAE_EULER_GUARD<T> = nullptr>
auto operator<<(std::ostream& output_stream, const Euler<T>& src)
    -> std::ostream& {
    output_stream << src.toString();
    return output_stream;
}

}  // namespace math
