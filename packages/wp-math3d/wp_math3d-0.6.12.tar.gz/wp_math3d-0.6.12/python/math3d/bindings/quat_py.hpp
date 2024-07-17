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

#include <math/quat_t.hpp>

#include <common_py.hpp>
#include <conversions_py.hpp>

namespace py = pybind11;

namespace math {

template <typename T>
using SFINAE_QUAT_BINDINGS = typename std::enable_if<IsScalar<T>::value>::type*;

template <typename T, SFINAE_QUAT_BINDINGS<T> = nullptr>
// NOLINTNEXTLINE
auto bindings_quaternion(py::module& m, const char* class_name) -> void {
    // using Vec3 = Vector3<T>;
    using Mat3 = Matrix3<T>;

    using Class = Quaternion<T>;
    py::class_<Class>(m, class_name, py::buffer_protocol())
        .def(py::init<>())
        .def(py::init<T>())
        .def(py::init<T, T, T, T>())
        .def(py::init<Mat3>())
        .def(py::init([](const py::array_t<T>& array_np) -> Class {
            auto array_buffer_info = array_np.request();
            if (array_buffer_info.size != Quaternion<T>::QUAT_SIZE) {
                throw std::runtime_error(
                    "Quaternion> incompatible array size; expected " +
                    std::to_string(Quaternion<T>::QUAT_SIZE) + ", got " +
                    std::to_string(array_buffer_info.size));
            }

            Class quat;
            memcpy(quat.data(), array_buffer_info.ptr, sizeof(Class));
            return quat;
        }))
        .def(py::init([](const py::buffer& buff) -> Class {
            py::buffer_info info = buff.request();
            if (IsFloat32<T>::value &&
                (info.format != py::format_descriptor<T>::format())) {
                throw std::runtime_error(
                    "Incompatible format: expected float (float32) array");
            }
            if (IsFloat64<T>::value &&
                (info.format != py::format_descriptor<T>::format())) {
                throw std::runtime_error(
                    "Incompatible format: expected double (float64) array");
            }
            bool is_valid_shape = true;
            if (info.ndim == 1) {
                is_valid_shape = (info.shape[0] == Class::QUAT_SIZE);
            } else if (info.ndim == 2) {
                is_valid_shape =
                    (info.shape[0] == Class::QUAT_SIZE && info.shape[1] == 1) ||
                    (info.shape[1] == Class::QUAT_SIZE && info.shape[0] == 1);
            } else {
                is_valid_shape = false;
            }
            if (!is_valid_shape) {
                throw std::runtime_error(
                    "Incompatible shape: expected (,4), (1,4), (4,1)");
            }

            Class quat;
            memcpy(quat.data(), info.ptr, sizeof(Class));
            return quat;
        }))
        .def_buffer([](Class& self) -> py::buffer_info {
            return py::buffer_info(self.data(), sizeof(T),
                                   py::format_descriptor<T>::format(), 1,
                                   {Class::QUAT_SIZE}, {sizeof(T)});
        })
        .def_property(
            "w", [](const Class& self) -> T { return self.w(); },
            [](Class& self, T value) -> void { self.w() = value; })
        .def_property(
            "x", [](const Class& self) -> T { return self.x(); },
            [](Class& self, T value) -> void { self.x() = value; })
        .def_property(
            "y", [](const Class& self) -> T { return self.y(); },
            [](Class& self, T value) -> void { self.y() = value; })
        .def_property(
            "z", [](const Class& self) -> T { return self.z(); },
            [](Class& self, T value) -> void { self.z() = value; })
        .def("__getitem__",
             [](const Class& self, int32_t index) -> T {
                 if (index >= 4 || index < 0) {
                     throw py::index_error();
                 }
                 return self[static_cast<uint32_t>(index)];
             })
        .def("__setitem__",
             [](Class& self, int32_t index, T value) -> void {
                 if (index >= 4 || index < 0) {
                     throw py::index_error();
                 }
                 self[static_cast<uint32_t>(index)] = value;
             })
        .def(py::self + py::self)
        .def(py::self - py::self)
        .def(py::self * py::self)
        .def("__mul__",
             [](const Class& self, T scale) -> Class {
                 return self * static_cast<double>(scale);
             })
        .def("__rmul__",
             [](Class& self, T scale) -> Class {
                 return static_cast<double>(scale) * self;
             })
        .def("__eq__",
             [](const Class& lhs, const Class& rhs) -> bool {
                 return lhs == rhs;
             })
        .def("__neq__",
             [](const Class& lhs, const Class& rhs) -> bool {
                 return lhs != rhs;
             })
        .def_static("RotationX", &Class::RotationX)
        .def_static("RotationY", &Class::RotationY)
        .def_static("RotationZ", &Class::RotationZ)
        .def("length", [](const Class& self) -> T { return norm<T>(self); })
        .def("lengthSquare",
             [](const Class& self) -> T { return ::math::squareNorm<T>(self); })
        .def("normalize",
             [](const Class& self) -> Class { return normalize<T>(self); })
        .def("normalize_",
             [](Class& self) -> void { normalize_in_place<T>(self); })
        .def(
            "conjugate",
            [](const Class& self) -> Class { return math::conjugate<T>(self); })
        .def("inverse",
             [](const Class& self) -> Class { return math::inverse<T>(self); })
        .def(
            "rotate",
            [](const Class& self, const py::array_t<T>& arr_vec) -> Vector3<T> {
                return math::rotate<T>(self, nparray_to_vec3<T>(arr_vec));
            })
        .def("__repr__", [](const Class& self) -> py::str {
            return py::str(
                       "Quaternion{}(w={:.8f}, x={:.8f}, y={:.8f}, z={:.8f})")
                .format((IsFloat32<T>::value ? "f" : "d"), self[0], self[1],
                        self[2], self[3]);
        });
}

}  // namespace math
