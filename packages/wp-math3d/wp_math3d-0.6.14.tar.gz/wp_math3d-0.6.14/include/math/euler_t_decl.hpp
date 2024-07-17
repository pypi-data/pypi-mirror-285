#pragma once

#include <ios>
#include <array>
#include <cmath>
#include <cassert>
#include <cstdint>
#include <initializer_list>
#include <iostream>
#include <sstream>
#include <string>
#include <algorithm>
#include <type_traits>

#include <math/vec3_t_decl.hpp>
#include <math/mat3_t_decl.hpp>
#include <math/mat4_t_decl.hpp>
#include <math/quat_t_decl.hpp>

namespace math {

template <typename T>
class Matrix3;

template <typename T>
class Matrix4;

template <typename T>
class Quaternion;

namespace euler {

/// Possible ordering (Tait-Bryan angles)
enum class Order : uint8_t {
    XYZ,
    YZX,
    ZXY,
    XZY,
    YXZ,
    ZYX,
};

/// Returns the string representation of the given order
inline auto ToString(const Order& p_order) -> std::string;

/// Possible conventions, either INTRINSIC or EXTRINSIC
enum class Convention {
    INTRINSIC,
    EXTRINSIC,
};

/// Returns the string representation of the given convention
inline auto ToString(const Convention& p_convention) -> std::string;

}  // namespace euler

/// \class Euler
///
/// \brief Class representation of a set of Euler angles
///
/// \tparam T Type of scalar value used for this set of Euler angles
///
/// This is a class that represents a set of Euler angles, with some given
/// axis order and convention.
template <typename T>
class Euler {
 public:
    using Vec3 = Vector3<T>;
    using Mat3 = Matrix3<T>;
    using Mat4 = Matrix4<T>;
    using Quat = Quaternion<T>;

    /// \brief Angle of rotation around the X-axis
    T x = static_cast<T>(0.0);  // NOLINT
    /// \brief Angle of rotation around the Y-axis
    T y = static_cast<T>(0.0);  // NOLINT
    /// \brief Angle of rotation around the Z-axis
    T z = static_cast<T>(0.0);  // NOLINT

    /// \brief The internal order used for the elemental rotations
    ///
    /// The order property for this set of Euler angles is used to define in
    /// which order are the elemental rotations taken (rotations around the
    /// X, Y, and Z axes). The default used is XYZ, which states that the
    /// rotations taken to generate the total rotation is the X, Y, Z, i.e.
    /// first we rotate around the X axis by an angle given by the .x()
    /// component of the Euler angles, then around the Y axis by an angle given
    /// by the .y() component of the Euler angles, and finally a rotation around
    /// the Z-axis by an angle given by the .z() component of the Euler angles.
    euler::Order order = euler::Order::XYZ;  // NOLINT

    /// \brief Returns the convention used by this set of Euler angles
    ///
    /// The convention property is used to define what we use as reference for
    /// the elemental rotations. This could be either INTRINSIC (rotations are
    /// taken w.r.t the rotating body frame), or EXTRINSIC (rotations are taken
    /// w.r.t. the fixed world frame). The default used is INTRINSIC, which
    /// states that we take the rotations around the axes while they are being
    /// rotated. For example, if we used ordering XYZ, we would rotate first
    /// around the X axis. Then the next rotation taken around the Y-axis would
    /// be performed around the new Y-axis after the first rotation was taken;
    /// we then rotate around the Z-axis in a similar way, around the new Z-axis
    /// defined after we have rotated around the Y-axis previously.
    euler::Convention convention = euler::Convention::INTRINSIC;  // NOLINT

    /// Constructs a set of Euler angles with all zero entries
    Euler() = default;

    /// Constructs a set of Euler angles from the given configuration
    /// \param[in] e_x Euler angle associated with a rotation around the X axis
    /// \param[in] e_y Euler angle associated with a rotation around the Y axis
    /// \param[in] e_z Euler angle associated with a rotation around the Z axis
    /// \param[in] p_order Order used for the representation
    /// \param[in] p_convention Convention used for the representation
    explicit Euler(
        T e_x, T e_y, T e_z, euler::Order p_order = euler::Order::XYZ,
        euler::Convention p_convention = euler::Convention::INTRINSIC) {
        this->order = p_order;
        this->convention = p_convention;
        this->x = e_x;
        this->y = e_y;
        this->z = e_z;
    }

    /// Constructs a set of Euler angles from the given 3x3 rotation matrix
    /// \param[in] matrix A 3x3 rotation matrix given by the user
    /// \param[in] p_order Order used for the representation
    /// \param[in] p_convention Convention used for the representation
    explicit Euler(
        const Mat3& matrix, euler::Order p_order = euler::Order::XYZ,
        euler::Convention p_convention = euler::Convention::INTRINSIC) {
        this->order = p_order;
        this->convention = p_convention;
        setFromRotationMatrix(matrix);
    }

    /// Constructs a set of Euler angles from the given 4x4 transform matrix
    /// \param[in] matrix A 4x4 transform matrix given by the user
    /// \param[in] p_order Order used for the representation
    /// \param[in] p_convention Convention used for the representation
    explicit Euler(
        const Mat4& matrix, euler::Order p_order = euler::Order::XYZ,
        euler::Convention p_convention = euler::Convention::INTRINSIC) {
        this->order = p_order;
        this->convention = p_convention;
        setFromTransform(matrix);
    }

    /// Constructs a set of Euler angles from the given quaternion
    /// \param[in] quaternion A quaternion given by the user
    /// \param[in] p_order Order used for the representation
    /// \param[in] p_convention Convention used for the representation
    explicit Euler(
        const Quat& quaternion, euler::Order p_order = euler::Order::XYZ,
        euler::Convention p_convention = euler::Convention::INTRINSIC) {
        this->order = p_order;
        this->convention = p_convention;
        setFromQuaternion(quaternion);
    }

    /// Constructs a set of Euler angles from the given axis-angle pair
    /// \param[in] axis The axis of rotation given by the user
    /// \param[in] angle The angle of rotation around the given axis
    /// \param[in] p_order Order used for the representation
    /// \param[in] p_convention Convention used for the representation
    explicit Euler(
        const Vec3& axis, T angle, euler::Order p_order = euler::Order::XYZ,
        euler::Convention p_convention = euler::Convention::INTRINSIC) {
        this->order = p_order;
        this->convention = p_convention;
        setFromAxisAngle(axis, angle);
    }

    /// Updates this set of Euler angles with the given 3x3 rotation matrix
    auto setFromRotationMatrix(const Mat3& matrix) -> void;

    /// Updates this set of Euler angles with the given 4x4 transform matrix
    auto setFromTransform(const Mat4& transform) -> void;

    /// Updates this set of Euler angles with the given quaternion
    auto setFromQuaternion(const Quat& quaternion) -> void;

    /// Updates this set of Euler angles with the given axis-angle pair
    auto setFromAxisAngle(const Vec3& axis, T angle) -> void;

    /// Returns a printable string-representation of the set of Euler Angles
    [[nodiscard]] auto toString() const -> std::string {
        std::stringstream sstr_repr;
        if constexpr (std::is_same<T, float>::value) {
            sstr_repr << "Euler_f(\n";
        } else if constexpr (std::is_same<T, double>::value) {
            sstr_repr << "Euler_d(\n";
        } else {
            sstr_repr << "Euler(\n";
        }

        sstr_repr << "  x=" << this->x << ",\n";
        sstr_repr << "  y=" << this->y << ",\n";
        sstr_repr << "  z=" << this->z << ",\n";
        sstr_repr << "  order=" << ::math::euler::ToString(this->order)
                  << ",\n";
        sstr_repr << "  convention="
                  << ::math::euler::ToString(this->convention) << "\n)";

        return sstr_repr.str();
    }
};

}  // namespace math
