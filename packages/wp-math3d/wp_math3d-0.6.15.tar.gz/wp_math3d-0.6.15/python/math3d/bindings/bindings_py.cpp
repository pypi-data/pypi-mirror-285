#include <pybind11/pybind11.h>

#include <vec2_py.hpp>
#include <vec3_py.hpp>
#include <vec4_py.hpp>
#include <mat2_py.hpp>
#include <mat3_py.hpp>
#include <mat4_py.hpp>
#include <quat_py.hpp>
#include <euler_py.hpp>
#include <pose3d_py.hpp>
#include <utils/geometry_helpers_py.hpp>

namespace py = pybind11;

namespace math {

extern auto bindings_conversions_functions(py::module m) -> void;

}  // namespace math

// NOLINTNEXTLINE
PYBIND11_MODULE(math3d_bindings, m) {
    ::math::bindings_vector2<::math::float32_t>(m, "Vector2f");
    ::math::bindings_vector2<::math::float64_t>(m, "Vector2d");
    ::math::bindings_vector3<::math::float32_t>(m, "Vector3f");
    ::math::bindings_vector3<::math::float64_t>(m, "Vector3d");
    ::math::bindings_vector4<::math::float32_t>(m, "Vector4f");
    ::math::bindings_vector4<::math::float64_t>(m, "Vector4d");
    ::math::bindings_matrix2<::math::float32_t>(m, "Matrix2f");
    ::math::bindings_matrix2<::math::float64_t>(m, "Matrix2d");
    ::math::bindings_matrix3<::math::float32_t>(m, "Matrix3f");
    ::math::bindings_matrix3<::math::float64_t>(m, "Matrix3d");
    ::math::bindings_matrix4<::math::float32_t>(m, "Matrix4f");
    ::math::bindings_matrix4<::math::float64_t>(m, "Matrix4d");
    ::math::bindings_quaternion<::math::float32_t>(m, "Quaternionf");
    ::math::bindings_quaternion<::math::float64_t>(m, "Quaterniond");
    ::math::bindings_euler_enums(m);
    ::math::bindings_euler<::math::float32_t>(m, "Euler_f");
    ::math::bindings_euler<::math::float64_t>(m, "Euler_d");
    ::math::bindings_pose3d<::math::float32_t>(m, "Pose3d_f");
    ::math::bindings_pose3d<::math::float64_t>(m, "Pose3d_d");

    ::math::bindings_utils_line<::math::float32_t>(m, "Line_f");
    ::math::bindings_utils_line<::math::float64_t>(m, "Line_d");
    ::math::bindings_utils_plane<::math::float32_t>(m, "Plane_f");
    ::math::bindings_utils_plane<::math::float64_t>(m, "Plane_d");
    ::math::bindings_utils_aabb<::math::float32_t>(m, "AABB_f");
    ::math::bindings_utils_aabb<::math::float64_t>(m, "AABB_d");

    ::math::bindings_conversions_functions(m);
}
