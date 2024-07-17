#pragma once

#include <string>
#include <cstring>
#include <stdexcept>

#include <pybind11/buffer_info.h>
#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/numpy.h>
#include <pybind11/pytypes.h>

#include <math/pose3d_t.hpp>

#include <common_py.hpp>
#include <conversions_py.hpp>

namespace py = pybind11;

namespace math {

template <typename T>
using SFINAE_POSE3D_BINDINGS =
    typename std::enable_if<IsScalar<T>::value>::type*;

template <typename T, SFINAE_POSE3D_BINDINGS<T> = nullptr>
// NOLINTNEXTLINE
auto bindings_pose3d(py::module& m, const char* class_name) -> void {
    using Vec3 = ::math::Vector3<T>;
    using Mat3 = ::math::Matrix3<T>;
    using Mat4 = ::math::Matrix4<T>;
    using Quat = ::math::Quaternion<T>;

    using Class = ::math::Pose3d<T>;
    py::class_<Class>(m, class_name)
        .def(py::init<>())
        .def(py::init<Vec3, Quat>())
        .def(py::init<Vec3, Mat3>())
        .def_readwrite("position", &Class::position)
        .def_readwrite("orientation", &Class::orientation)
        .def("apply",
             [](const Class& self, const Vec3& vec) -> Vec3 {
                 return self.apply(vec);
             })
        .def("apply",
             [](const Class& self,
                const py::array_t<T>& vec_np) -> py::array_t<T> {
                 return ::math::vec3_to_nparray<T>(
                     self.apply(::math::nparray_to_vec3<T>(vec_np)));
             })
        .def("inverse",
             [](const Class& self) -> Class { return self.inverse(); })
        .def("toMatrix",
             [](const Class& self) -> Mat4 { return self.toMatrix(); })
        .def("__mul__",
             [](const Class& self, const Vec3& vec) -> Vec3 {
                 return self * vec;
             })
        .def("__mul__",
             [](const Class& self,
                const py::array_t<T>& vec_np) -> py::array_t<T> {
                 return ::math::vec3_to_nparray<T>(
                     self * ::math::nparray_to_vec3<T>(vec_np));
             })
        .def("__mul__",
             [](const Class& self, const Class& rhs) -> Class {
                 return self * rhs;
             })
        .def("__repr__", [](const Class& self) -> py::str {
            return py::str(
                       "<Pose3d\n"
                       "  pos: {}\n"
                       "  quat: {}\n"
                       "  dtype: {}\n"
                       ">")
                .format(self.position.toString(), self.orientation.toString(),
                        (IsFloat32<T>::value ? "float32" : "float64"));
        });
}

}  // namespace math
