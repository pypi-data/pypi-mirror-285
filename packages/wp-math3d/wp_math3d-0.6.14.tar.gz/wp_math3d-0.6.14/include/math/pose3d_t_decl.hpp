#pragma once

#include <sstream>
#include <string>

#include <math/common.hpp>

#include <math/vec3_t_decl.hpp>
#include <math/vec4_t_decl.hpp>
#include <math/mat3_t_decl.hpp>
#include <math/mat4_t_decl.hpp>
#include <math/euler_t_decl.hpp>

namespace math {
template <typename T>
class Matrix3;

template <typename T>
class Euler;

template <typename T>
class Quaternion;
}  // namespace math

namespace math {

template <typename T>
class Pose3d {
 public:
    using Vec3 = ::math::Vector3<T>;
    using Vec4 = ::math::Vector4<T>;
    using Quat = ::math::Quaternion<T>;
    using Mat3 = ::math::Matrix3<T>;
    using Mat4 = ::math::Matrix4<T>;

    /// The position component of this pose
    Vec3 position;
    /// The orientation component of this pose
    Quat orientation;

    Pose3d() = default;

    explicit Pose3d(const Vec3& pos, const Quat& quat);

    explicit Pose3d(const Vec3& pos, const Euler<T>& euler);

    explicit Pose3d(const Vec3& pos, const Mat3& mat);

    explicit Pose3d(const Mat4& transform);

    /// Transforms the given vector by using this pose
    LM_INLINE auto apply(const Vec3& rhs) const -> Vec3;

    /// Returns the inverse of this pose
    LM_INLINE auto inverse() const -> Pose3d<T>;

    /// Returns a 4x4 matrix equivalent to this pose
    LM_INLINE auto toMatrix() const -> Mat4;

    /// Composes the given pose with this pose
    LM_INLINE auto operator*(const Pose3d<T>& rhs) const -> Pose3d<T>;

    /// Applies this transform to the given vector
    LM_INLINE auto operator*(const Vec3& rhs) const -> Vec3;

    /// Returns a printable string representation of this pose
    [[nodiscard]] auto toString() const -> std::string {
        std::stringstream str_result;
        str_result << "Pose3d(pos=" << this->position.toString() << ", ";
        str_result << "rot=" << this->orientation.toString() << ")";
        return str_result.str();
    }
};

}  // namespace math
