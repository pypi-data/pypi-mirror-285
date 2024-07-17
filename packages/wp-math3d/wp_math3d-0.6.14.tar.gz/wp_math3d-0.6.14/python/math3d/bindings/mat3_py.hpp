#pragma once

#include <cstring>
#include <stdexcept>
#include <utility>

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/pytypes.h>
#include <pybind11/numpy.h>

#include <math/mat3_t.hpp>

#include <common_py.hpp>
#include <conversions_py.hpp>

namespace py = pybind11;

#if defined(_MSC_VER)
#pragma warning(push)
#pragma warning(disable : 4127)
#endif

namespace math {

template <typename T>
using SFINAE_MAT3_BINDINGS = typename std::enable_if<IsScalar<T>::value>::type*;

template <typename T, SFINAE_MAT3_BINDINGS<T> = nullptr>
// NOLINTNEXTLINE
auto bindings_matrix3(py::module& m, const char* class_name) -> void {
    using Class = Matrix3<T>;
    using Column = typename Matrix3<T>::ColumnType;
    py::class_<Class>(m, class_name, py::buffer_protocol())
        .def(py::init<>())
        .def(py::init<T, T, T>())
        .def(py::init<T, T, T, T, T, T, T, T, T>())
        .def(py::init<Column, Column, Column>())
        // clang-format off
        MATRIX_BUFFER_PROTOCOL(3, T)
        MATRIX_OPERATORS(T)
        MATRIX_METHODS(T)
        // cppcheck-suppress constParameter
        MATRIX_GETSET_ITEM(3, T)
        // clang-format on
        .def("numpy",
             [](const Class& self) -> py::array_t<T> {
                 return py::array_t<T>(
                     {Class::MATRIX_SIZE, Class::MATRIX_SIZE},
                     {sizeof(T), sizeof(T) * Class::MATRIX_SIZE}, self.data(),
                     py::cast(self));
             })
        .def("flatten",
             [](const Class& self) -> py::array_t<T> {
                 return py::array_t<T>(Class::BUFFER_SIZE, self.data(),
                                       py::cast(self));
             })
        .def_property_readonly(
            "T",
            [](const Class& self) -> Class { return math::transpose<T>(self); })
        .def_static("RotationX", &Class::RotationX)
        .def_static("RotationY", &Class::RotationY)
        .def_static("RotationZ", &Class::RotationZ)
        .def_static("Scale",
                    [](T scale_x, T scale_y, T scale_z) -> Class {
                        return Class::Scale(scale_x, scale_y, scale_z);
                    })
        .def_static("Scale",
                    [](const Vector3<T>& scale) -> Class {
                        return Class::Scale(scale);
                    })
        .def_static("Identity", &Class::Identity)
        .def_static("Zeros", &Class::Zeros)
        .def("__repr__", [](const Class& self) -> py::str {
            // clang-format off
            return py::str("Matrix3{}([[{:.8f},{:.8f},{:.8f}],\n"
                           "          [{:.8f},{:.8f},{:.8f}],\n"
                           "          [{:.8f},{:.8f},{:.8f}]])")
                .format(IsFloat32<T>::value ? "f" : "d",
                    self(0, 0), self(0, 1), self(0, 2),
                    self(1, 0), self(1, 1), self(1, 2),
                    self(2, 0), self(2, 1), self(2, 2));

            // clang-format on
        });
}

#if defined(_MSC_VER)
#pragma warning(pop)
#endif

}  // namespace math
