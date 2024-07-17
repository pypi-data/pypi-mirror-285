#pragma once

#include <utility>

#include <pybind11/pybind11.h>

#include <math/common.hpp>

// clang-format off
// NOLINTNEXTLINE
#define VECTOR_BUFFER_PROTOCOL(T)                                           \
    .def(py::init([](const py::buffer& buff) -> Class {                     \
        py::buffer_info info = buff.request();                              \
        if (IsFloat32<T>::value &&                                          \
            (info.format != py::format_descriptor<T>::format())) {          \
            throw std::runtime_error(                                       \
                "Incompatible format: expected float (float32) array");     \
        }                                                                   \
        if (IsFloat64<T>::value &&                                          \
            (info.format != py::format_descriptor<T>::format())) {          \
            throw std::runtime_error(                                       \
                "Incompatible format: expected double (float64) array");    \
        }                                                                   \
        bool is_valid_shape = true;                                         \
        if (info.ndim == 1) {                                               \
            is_valid_shape = (info.shape[0] == Class::VECTOR_SIZE);         \
        } else if (info.ndim == 2) {                                        \
            is_valid_shape = (info.shape[0] == Class::VECTOR_SIZE ||        \
                              info.shape[1] == Class::VECTOR_SIZE);         \
        } else {                                                            \
            is_valid_shape = false;                                         \
        }                                                                   \
        if (!is_valid_shape) {                                              \
            throw std::runtime_error(                                       \
                "Incompatible shape: expected (, n), (1, n), (n, 1)");      \
        }                                                                   \
        Class vec;                                                          \
        memcpy(vec.data(), info.ptr, sizeof(T) * Class::VECTOR_SIZE);       \
        return vec;                                                         \
    }))                                                                     \
    .def_buffer([](Class& self) -> py::buffer_info {                        \
        return py::buffer_info(self.data(), sizeof(T),                      \
                               py::format_descriptor<T>::format(),          \
                               Class::VECTOR_NDIM,                          \
                               {Class::VECTOR_SIZE}, {sizeof(T)});          \
    })

// NOLINTNEXTLINE
#define MATRIX_BUFFER_PROTOCOL(Size, T)                                     \
    .def(py::init([](const py::buffer& buff) -> Class {                     \
        py::buffer_info info = buff.request();                              \
        if (IsFloat32<T>::value &&                                          \
            (info.format != py::format_descriptor<T>::format())) {          \
            throw std::runtime_error(                                       \
                "Incompatible format: expected float (float32) array");     \
        }                                                                   \
        if (IsFloat64<T>::value &&                                          \
            (info.format != py::format_descriptor<T>::format())) {          \
            throw std::runtime_error(                                       \
                "Incompatible format: expected double (float64) array");    \
        }                                                                   \
        Class mat;                                                          \
        if (info.ndim == Class::MATRIX_NDIM) {                              \
            if (info.shape[0] == Class::MATRIX_SIZE &&                      \
                info.shape[1] == Class::MATRIX_SIZE) {                      \
                auto* src_data = static_cast<const T*>(info.ptr);           \
                for (uint32_t j = 0; j < Class::MATRIX_SIZE; ++j) {         \
                    for (uint32_t i = 0; i < Class::MATRIX_SIZE; ++i) {     \
                        auto src_index = j + i * Class::MATRIX_SIZE;        \
                        mat(i, j) = src_data[src_index];                    \
                    }                                                       \
                }                                                           \
            } else {                                                        \
                throw std::runtime_error(                                   \
                    "Incompatible size: expected (" #Size ", " #Size ")");  \
            }                                                               \
        } else {                                                            \
            throw std::runtime_error(                                       \
                "Incompatible shape: expected (" #Size ", " #Size ")");     \
        }                                                                   \
        return mat;                                                         \
    }))                                                                     \
    .def_buffer([](Class& self) -> py::buffer_info {                        \
        return py::buffer_info(self.data(), sizeof(T),                      \
                               py::format_descriptor<T>::format(),          \
                               Class::MATRIX_NDIM,                          \
                               {Class::MATRIX_SIZE, Class::MATRIX_SIZE},    \
                               {sizeof(T), sizeof(T) * Class::MATRIX_SIZE});\
    })

// NOLINTNEXTLINE
#define VECTOR_PROPERTY(var) .def_property(#var,    \
    [](const Class& self) -> T                      \
        {                                           \
            return self.var();                      \
        },                                          \
    [](Class& self, T value)                        \
        {                                           \
            self.var() = value;                     \
        })

// NOLINTNEXTLINE
#define VECTOR_GETSET_ITEM(Size, Type)                      \
    .def("__getitem__",                                     \
    [](const Class& self, int32_t index) -> Type            \
        {                                                   \
            if (index >= Size || index < 0) {               \
                throw py::index_error();                    \
            }                                               \
            return self[static_cast<uint32_t>(index)];      \
        })                                                  \
    .def("__setitem__",                                     \
    [](Class& self, int32_t index, Type value) -> void      \
        {                                                   \
            if (index >= Size || index < 0) {               \
                throw py::index_error();                    \
            }                                               \
            self[static_cast<uint32_t>(index)] = value;     \
        })

// NOLINTNEXTLINE
#define MATRIX_GETSET_ITEM(Size, Type)                                      \
    .def("__getitem__",                                                     \
    [](const Class& self, int32_t index) -> Column                          \
        {                                                                   \
            if (index >= Size || index < 0) {                               \
                throw py::index_error();                                    \
            }                                                               \
            return self[static_cast<uint32_t>(index)];                      \
        })                                                                  \
    .def("__getitem__",                                                     \
    [](const Class& self, std::pair<int32_t, int32_t> accessor) -> Type     \
        {                                                                   \
            if (accessor.first >= Size || accessor.first < 0 ||             \
                accessor.second >= Size || accessor.second < 0) {           \
                throw py::index_error();                                    \
            }                                                               \
            auto row_index = static_cast<uint32_t>(accessor.first);         \
            auto col_index = static_cast<uint32_t>(accessor.second);        \
            return self(row_index, col_index);                              \
        })                                                                  \
    .def("__setitem__",                                                     \
    [](Class& self, int32_t index, const py::buffer& buff) -> void          \
        {                                                                   \
            if (index >= Size || index < 0) {                               \
                throw py::index_error();                                    \
            }                                                               \
            auto col_index = static_cast<uint32_t>(index);                  \
            self[col_index] = buffer_to_vec##Size<Type>(buff);              \
        })                                                                  \
    .def("__setitem__",                                                     \
    [](Class& self, std::pair<int32_t, int32_t> accessor, Type value)       \
        {                                                                   \
            if (accessor.first >= Size || accessor.first < 0 ||             \
                accessor.second >= Size || accessor.second < 0) {           \
                throw py::index_error();                                    \
            }                                                               \
            auto row_index = static_cast<uint32_t>(accessor.first);         \
            auto col_index = static_cast<uint32_t>(accessor.second);        \
            self(row_index, col_index) = value;                             \
        })

// NOLINTNEXTLINE
#define VECTOR_OPERATORS(Type)                                          \
    .def(py::self + py::self)                                           \
    .def(py::self - py::self)                                           \
    .def(py::self * py::self)                                           \
    .def("__mul__", [](const Class& self, Type scale) -> Class {        \
        return self * static_cast<double>(scale);                       \
    })                                                                  \
    .def("__rmul__", [](const Class& self, Type scale) -> Class {       \
        return static_cast<double>(scale) * self;                       \
    })                                                                  \
    .def("__eq__", [](const Class& lhs, const Class& rhs) -> bool {     \
        return lhs == rhs;                                              \
    })                                                                  \
    .def("__neq__", [](const Class& lhs, const Class& rhs) -> bool {    \
        return lhs != rhs;                                              \
    })                                                                  \
    .def("__neg__", [](const Class& self) -> Class {                    \
        return -self;                                                   \
    })

// NOLINTNEXTLINE
#define MATRIX_OPERATORS(Type)                                              \
    .def(py::self + py::self)                                               \
    .def(py::self - py::self)                                               \
    .def(py::self * py::self)                                               \
    .def("__mul__", [](const Class& self, Type scale) -> Class {            \
        return self * static_cast<double>(scale);                           \
    })                                                                      \
    .def("__rmul__", [](const Class& self, Type scale) -> Class {           \
        return static_cast<double>(scale) * self;                           \
    })                                                                      \
    .def("__mul__", [](const Class& self, const Column& rhs) -> Column {    \
        return self * rhs;                                                  \
    })                                                                      \
    .def("__eq__", [](const Class& lhs, const Class& rhs) -> bool {         \
        return lhs == rhs;                                                  \
    })                                                                      \
    .def("__neq__", [](const Class& lhs, const Class& rhs) -> bool {        \
        return lhs != rhs;                                                  \
    })

// NOLINTNEXTLINE
#define VECTOR_METHODS(Type)                                            \
    .def("dot", [](const Class& self, const Class& other) -> Type {     \
        return ::math::dot<Type>(self, other);                          \
    })                                                                  \
    .def("norm", [](const Class& self) -> Type {                        \
        return ::math::norm<Type>(self);                                \
    })                                                                  \
    .def("squareNorm", [](const Class& self) -> Type {                  \
        return ::math::squareNorm<Type>(self);                          \
    })                                                                  \
    .def("normalize", [](const Class& self) -> Class {                  \
        return ::math::normalize<Type>(self);                           \
    })                                                                  \
    .def("normalize_", [](Class& self) -> void {                        \
        ::math::normalize_in_place<Type>(self);                         \
    })

// NOLINTNEXTLINE
#define MATRIX_METHODS(Type)                                            \
    .def("transpose", [](const Class& self) -> Class {                  \
        return ::math::transpose<Type>(self);                           \
    })                                                                  \
    .def("trace", [](const Class& self) -> Type {                       \
        return ::math::trace<Type>(self);                               \
    })                                                                  \
    .def("determinant", [](const Class& self) -> Type {                 \
        return ::math::determinant<Type>(self);                         \
    })                                                                  \
    .def("inverse", [](const Class& self) -> Class {                    \
        return ::math::inverse<Type>(self);                             \
    })

// clang-format on
