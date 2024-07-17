#pragma once

#include <math/pose3d_t_decl.hpp>

#include <math/vec3_t.hpp>
#include <math/mat3_t.hpp>
#include <math/euler_t.hpp>
#include <math/quat_t.hpp>
#include <math/mat4_t.hpp>

namespace math {

template <typename T>
Pose3d<T>::Pose3d(const Vec3& pos, const Quat& quat) {
    this->position = pos;
    this->orientation = quat.normalized();
}

template <typename T>
Pose3d<T>::Pose3d(const Vec3& pos, const Euler<T>& euler) {
    this->position = pos;
    this->orientation.setFromEuler(euler);
    this->orientation.normalize();
}

template <typename T>
Pose3d<T>::Pose3d(const Vec3& pos, const Mat3& rotmat) {
    this->position = pos;
    this->orientation.setFromRotationMatrix(rotmat);
    this->orientation.normalize();
}

template <typename T>
Pose3d<T>::Pose3d(const Mat4& transform) {
    this->position = Vec3(transform[3]);
    this->orientation.setFromRotationMatrix(Mat3(transform));
    this->orientation.normalize();
}

template <typename T>
auto Pose3d<T>::apply(const Vec3& rhs) const -> Vec3 {
    return this->position + this->orientation.rotate(rhs);
}

template <typename T>
auto Pose3d<T>::inverse() const -> Pose3d<T> {
    // Inverse transform in matrix form:
    //
    //        | R   p |        | R^-1   -R^-1 * p |
    // X_AB = |       | X_BA = |                  |
    //        | 0   1 |        |  0          1    |
    //
    // Using quaternions (q) instead of Rotations (R)
    // - p: position (vector)
    //   q: orientation (quaternion)
    //
    // q_inv = q^-1
    // p_inv = -q_inv * p

    auto q_inv = this->orientation.inverse();
    auto p_inv = -q_inv.rotate(this->position);
    return Pose3d<T>(p_inv, q_inv);
}

template <typename T>
auto Pose3d<T>::toMatrix() const -> Mat4 {
    return Mat4(this->position, this->orientation);
}

template <typename T>
auto Pose3d<T>::operator*(const Pose3d<T>& rhs) const -> Pose3d<T> {
    auto res_orientation = (this->orientation * rhs.orientation).normalized();
    auto res_position = this->position + this->orientation.rotate(rhs.position);
    return Pose3d<T>(res_position, res_orientation);
}

template <typename T>
auto Pose3d<T>::operator*(const Vec3& rhs) const -> Vec3 {
    return this->apply(rhs);
}

}  // namespace math
