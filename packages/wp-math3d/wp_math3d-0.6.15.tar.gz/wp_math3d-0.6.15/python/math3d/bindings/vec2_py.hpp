#pragma once

#include <cstring>
#include <stdexcept>
#include <utility>

#include <pybind11/buffer_info.h>
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/pytypes.h>
#include <pybind11/numpy.h>
#include <pybind11/attr.h>
#include <pybind11/detail/common.h>

#include <math/vec2_t.hpp>

#include <common_py.hpp>
#include <conversions_py.hpp>

namespace py = pybind11;

#if defined(__clang__)
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wunused-parameter"
#endif

#if defined(_MSC_VER)
#pragma warning(push)
#pragma warning(disable : 4127)
#endif

namespace math {

template <typename T>
using SFINAE_VEC2_BINDINGS = typename std::enable_if<IsScalar<T>::value>::type*;

template <typename T, SFINAE_VEC2_BINDINGS<T> = nullptr>
// NOLINTNEXTLINE
auto bindings_vector2(py::module& m, const char* class_name) -> void {
    {
        using Class = Vector2<T>;
        py::class_<Class>(m, class_name, py::buffer_protocol())
            .def(py::init<>())
            .def(py::init<T>())
            .def(py::init<T, T>())
            // clang-format off
            VECTOR_BUFFER_PROTOCOL(T)
            VECTOR_PROPERTY(x)
            VECTOR_PROPERTY(y)
            VECTOR_OPERATORS(T)
            VECTOR_GETSET_ITEM(2, T)
            // clang-format on
            .def("dot",
                 [](const Class& self, const Class& other) -> T {
                     return self.dot(other);
                 })
            .def("norm", [](const Class& self) -> T { return self.length(); })
            .def("squareNorm",
                 [](const Class& self) -> T { return self.lengthSquare(); })
            .def("normalize",
                 [](const Class& self) -> Class { return self.normalized(); })
            .def("normalize_", [](Class& self) -> void { self.normalize(); })
            .def("numpy",
                 [](const Class& self) -> py::array_t<T> {
                     return py::array_t<T>(Class::VECTOR_SIZE, self.data(),
                                           py::cast(self));
                 })
            // NOLINTNEXTLINE
            .def_property_readonly(
                "ndim", [](const Class&) { return Class::VECTOR_NDIM; })
            // NOLINTNEXTLINE
            .def_property_readonly("shape",
                                   [](const Class&) {
                                       return std::pair<uint32_t, uint32_t>(1,
                                                                            2);
                                   })
            .def("__repr__", [](const Class& self) -> py::str {
                return py::str("Vector2{}(x={}, y={})")
                    .format((IsFloat32<T>::value ? "f" : "d"), self.x(),
                            self.y());
            });
    }
}

#if defined(__clang__)
#pragma clang diagnostic pop
#endif

#if defined(_MSC_VER)
#pragma warning(pop)
#endif

}  // namespace math
