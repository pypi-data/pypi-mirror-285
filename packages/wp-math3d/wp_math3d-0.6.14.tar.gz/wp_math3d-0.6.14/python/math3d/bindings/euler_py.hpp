#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

#include <common_py.hpp>
#include <conversions_py.hpp>

namespace py = pybind11;

namespace math {

// NOLINTNEXTLINE
auto bindings_euler_enums(py::module& m) -> void {
    py::enum_<::math::euler::Order>(m, "eOrder")
        .value("XYZ", ::math::euler::Order::XYZ)
        .value("YZX", ::math::euler::Order::YZX)
        .value("ZXY", ::math::euler::Order::ZXY)
        .value("XZY", ::math::euler::Order::XZY)
        .value("YXZ", ::math::euler::Order::YXZ)
        .value("ZYX", ::math::euler::Order::ZYX);

    py::enum_<::math::euler::Convention>(m, "eConvention")
        .value("INTRINSIC", ::math::euler::Convention::INTRINSIC)
        .value("EXTRINSIC", ::math::euler::Convention::EXTRINSIC);
}

template <typename T>
using SFINAE_EULER_BINDINGS =
    typename std::enable_if<IsScalar<T>::value>::type*;

template <typename T, SFINAE_EULER_BINDINGS<T> = nullptr>
// NOLINTNEXTLINE
auto bindings_euler(py::module& m, const char* class_name) -> void {
    using Vec3 = ::math::Vector3<T>;
    using Mat3 = ::math::Matrix3<T>;
    using Mat4 = ::math::Matrix4<T>;
    using Quat = ::math::Quaternion<T>;

    using Class = ::math::Euler<T>;
    py::class_<Class>(m, class_name)
        .def(py::init<>())
        .def(py::init<T, T, T>())
        .def(py::init<Mat3>())
        .def(py::init<Mat4>())
        .def(py::init<Quat>())
        .def(py::init<Vec3, T>())
        .def_readwrite("order", &Class::order)
        .def_readwrite("convention", &Class::convention)
        .def_readwrite("x", &Class::x)
        .def_readwrite("y", &Class::y)
        .def_readwrite("z", &Class::z)
        .def("setFromRotationMatrix",
             [](Class& self, const Mat3& rotmat) -> void {
                 self.setFromRotationMatrix(rotmat);
             })
        .def("setFromTransform",
             [](Class& self, const Mat4& tf) -> void {
                 self.setFromTransform(tf);
             })
        .def("setFromQuaternion",
             [](Class& self, const Quat& quat) -> void {
                 self.setFromQuaternion(quat);
             })
        .def("setFromAxisAngle",
             [](Class& self, const Vec3& axis, T angle) -> void {
                 self.setFromAxisAngle(axis, angle);
             })
        .def("__repr__", [](const Class& self) -> py::str {
            return py::str(
                       "<Euler\n"
                       "  x: {:.8f}\n"
                       "  y: {:.8f}\n"
                       "  z: {:.8f}\n"
                       "  dtype: {}\n"
                       "  order: {}\n"
                       "  convention: {}\n"
                       ">")
                .format(self.x, self.y, self.z,
                        (IsFloat32<T>::value ? "float32" : "float64"),
                        ::math::euler::ToString(self.order),
                        ::math::euler::ToString(self.convention));
        });
}

}  // namespace math
