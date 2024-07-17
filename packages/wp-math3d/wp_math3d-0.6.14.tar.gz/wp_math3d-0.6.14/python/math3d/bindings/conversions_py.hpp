#pragma once

#include <string>
#include <stdexcept>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/pytypes.h>

#include <math/vec2_t.hpp>
#include <math/vec3_t.hpp>
#include <math/vec4_t.hpp>
#include <math/mat2_t.hpp>
#include <math/mat3_t.hpp>
#include <math/mat4_t.hpp>
#include <math/quat_t.hpp>

/**
 * NOTES:
 *
 * - For numpy to matrix conversions: We're assumming that the matrix given as a
 * numpy array is stored in the most common format (row-major). Our internal
 * ordering for matrices is column-major, so we have to grab the elements.
 */

namespace py = pybind11;

#if defined(_MSC_VER)
#pragma warning(push)
#pragma warning(disable : 4127)
#endif

// clang-format off

// -------------------------------------------------------------------------- //
//                Macros for conversions between and from Vectors             //
// -------------------------------------------------------------------------- //

// NOLINTNEXTLINE
#define QUAT_TO_NPARRAY(QuatCls, xquat)                             \
    auto array_np = py::array_t<T>(QuatCls::QUAT_SIZE);             \
    memcpy(array_np.request().ptr, xquat.data(), sizeof(QuatCls));  \
    return array_np

// NOLINTNEXTLINE
#define NPARRAY_TO_QUAT(QuatCls, xquat_np)                              \
    auto info = xquat_np.request();                                     \
    if (info.size != QuatCls::QUAT_SIZE) {                              \
        throw std::runtime_error("Incompatible array_size, expected " + \
                                 std::to_string(QuatCls::QUAT_SIZE) +   \
                                 " elements");                          \
    }                                                                   \
    QuatCls quat;                                                       \
    memcpy(quat.data(), info.ptr, sizeof(QuatCls));                     \
    return quat

// NOLINTNEXTLINE
#define VECTOR_TO_NPARRAY(VecCls, xvec)                             \
    auto array_np = py::array_t<T>(VecCls::VECTOR_SIZE);            \
    memcpy(array_np.request().ptr, xvec.data(), sizeof(VecCls));    \
    return array_np

// NOLINTNEXTLINE
#define NPARRAY_TO_VECTOR(VecCls, xarray_np)                                \
    auto info = xarray_np.request();                                        \
    if (info.size != VecCls::VECTOR_SIZE) {                                 \
        throw std::runtime_error("Incompatible array size, expected " +     \
                                 std::to_string(VecCls::VECTOR_SIZE) +      \
                                 " elements");                              \
    }                                                                       \
    VecCls vec;                                                             \
    memcpy(vec.data(), info.ptr, sizeof(VecCls));                           \
    return vec

// NOLINTNEXTLINE
#define BUFFER_TO_VECTOR(VecCls, xbuff)                                     \
    constexpr size_t SIZE_N = VecCls::VECTOR_SIZE;                          \
    using Type = typename VecCls::ElementType;                              \
    auto info = xbuff.request();                                            \
    if (IsFloat32<Type>::value &&                                           \
        (info.format != py::format_descriptor<Type>::format())) {           \
        throw std::runtime_error(                                           \
            "Incompatible format: expected float (float32) array");         \
    }                                                                       \
    if (IsFloat64<Type>::value &&                                           \
        (info.format != py::format_descriptor<Type>::format())) {           \
        throw std::runtime_error(                                           \
            "Incompatible format: expected double (float64) array");        \
    }                                                                       \
    bool is_valid_shape;                                                    \
    if (info.ndim == 1) {                                                   \
        is_valid_shape = (info.shape[0] == SIZE_N);                         \
    } else if (info.ndim == 2) {                                            \
        is_valid_shape = (info.shape[0] == SIZE_N ||                        \
                          info.shape[1] == SIZE_N);                         \
    } else {                                                                \
        is_valid_shape = false;                                             \
    }                                                                       \
    if (!is_valid_shape) {                                                  \
        throw std::runtime_error(                                           \
            "Incompatible shape: expected (,n), (1,n), (n,1)");             \
    }                                                                       \
    VecCls vec;                                                             \
    memcpy(vec.data(), info.ptr, sizeof(Type) * SIZE_N);                    \
    return vec

// -------------------------------------------------------------------------- //
//               Macros for conversions between and from Matrices             //
// -------------------------------------------------------------------------- //

// NOLINTNEXTLINE
#define MATRIX_TO_NPARRAY(MatCls, xmat)                                 \
    constexpr size_t SIZE_N = MatCls::MATRIX_SIZE;                      \
    using Type = typename MatCls::ElementType;                          \
    return py::array(py::buffer_info(                                   \
                        const_cast<Type*>(xmat.data()), /* NOLINT */    \
                        sizeof(Type),                                   \
                        py::format_descriptor<Type>::format(),          \
                        2,                                              \
                        {SIZE_N, SIZE_N},                               \
                        {sizeof(Type), sizeof(Type) * SIZE_N}))


// NOLINTNEXTLINE
#define NPARRAY_TO_MATRIX(MatCls, xarray_np)                                \
    constexpr uint32_t SIZE_N = MatCls::MATRIX_SIZE;                        \
    using Type = typename MatCls::ElementType;                              \
    auto info = xarray_np.request();                                        \
    if (info.ndim != 2) {                                                   \
        throw std::runtime_error(                                           \
            "nparray_to_matrix: incompatible array dimensions. It requires "\
            "an (n, n) array, so two dimensions are required");             \
    }                                                                       \
    if (info.shape[0] != SIZE_N || info.shape[1] != SIZE_N) {               \
        throw std::runtime_error(                                           \
            "nparray_to_matrix: incompatible array size. It expects a (n, " \
            "n) matrix of size 'n'");                                       \
    }                                                                       \
    auto data = static_cast<const Type*>(info.ptr);                         \
    MatCls matrix;                                                          \
    for (uint32_t i = 0; i < SIZE_N; ++i) {                                 \
        for (uint32_t j = 0; j < SIZE_N; ++j) {                             \
            if (xarray_np.flags() & py::array::f_style) {                   \
                matrix(i, j) = data[i + SIZE_N * j];                        \
            } else if (xarray_np.flags() & py::array::c_style) {            \
                matrix(i, j) = data[j + SIZE_N * i];                        \
            }                                                               \
        }                                                                   \
    }                                                                       \
    return matrix

// clang-format on

namespace math {

template <typename T>
using SFINAE_CONVERSIONS_BINDINGS =
    typename std::enable_if<IsScalar<T>::value>::type*;

// -------------------------------------------------------------------------- //
//                    Conversions from Math3d to NumPy                        //
// -------------------------------------------------------------------------- //

template <typename T, SFINAE_CONVERSIONS_BINDINGS<T> = nullptr>
inline auto quat_to_nparray(const Quaternion<T>& quat) -> py::array_t<T> {
    QUAT_TO_NPARRAY(Quaternion<T>, quat);
}

template <typename T, SFINAE_CONVERSIONS_BINDINGS<T> = nullptr>
inline auto vec2_to_nparray(const Vector2<T>& vec) -> py::array_t<T> {
    VECTOR_TO_NPARRAY(Vector2<T>, vec);
}

template <typename T, SFINAE_CONVERSIONS_BINDINGS<T> = nullptr>
inline auto vec3_to_nparray(const Vector3<T>& vec) -> py::array_t<T> {
    VECTOR_TO_NPARRAY(Vector3<T>, vec);
}

template <typename T, SFINAE_CONVERSIONS_BINDINGS<T> = nullptr>
inline auto vec4_to_nparray(const Vector4<T>& vec) -> py::array_t<T> {
    VECTOR_TO_NPARRAY(Vector4<T>, vec);
}

template <typename T, SFINAE_CONVERSIONS_BINDINGS<T> = nullptr>
inline auto mat2_to_nparray(const Matrix2<T>& mat) -> py::array_t<T> {
    MATRIX_TO_NPARRAY(Matrix2<T>, mat);
}

template <typename T, SFINAE_CONVERSIONS_BINDINGS<T> = nullptr>
inline auto mat3_to_nparray(const Matrix3<T>& mat) -> py::array_t<T> {
    MATRIX_TO_NPARRAY(Matrix3<T>, mat);
}

template <typename T, SFINAE_CONVERSIONS_BINDINGS<T> = nullptr>
inline auto mat4_to_nparray(const Matrix4<T>& mat) -> py::array_t<T> {
    MATRIX_TO_NPARRAY(Matrix4<T>, mat);
}

// -------------------------------------------------------------------------- //
//                    Conversions from NumPy to Math3d                        //
// -------------------------------------------------------------------------- //

template <typename T, SFINAE_CONVERSIONS_BINDINGS<T> = nullptr>
inline auto nparray_to_quat(const py::array_t<T>& array_np) -> Quaternion<T> {
    NPARRAY_TO_QUAT(Quaternion<T>, array_np);
}

template <typename T, SFINAE_CONVERSIONS_BINDINGS<T> = nullptr>
inline auto nparray_to_vec2(const py::array_t<T>& array_np) -> Vector2<T> {
    NPARRAY_TO_VECTOR(Vector2<T>, array_np);
}

template <typename T, SFINAE_CONVERSIONS_BINDINGS<T> = nullptr>
inline auto nparray_to_vec3(const py::array_t<T>& array_np) -> Vector3<T> {
    NPARRAY_TO_VECTOR(Vector3<T>, array_np);
}

template <typename T, SFINAE_CONVERSIONS_BINDINGS<T> = nullptr>
inline auto nparray_to_vec4(const py::array_t<T>& array_np) -> Vector4<T> {
    NPARRAY_TO_VECTOR(Vector4<T>, array_np);
}

template <typename T, SFINAE_CONVERSIONS_BINDINGS<T> = nullptr>
inline auto nparray_to_mat2(const py::array_t<T>& array_np) -> Matrix2<T> {
    NPARRAY_TO_MATRIX(Matrix2<T>, array_np);
}

template <typename T, SFINAE_CONVERSIONS_BINDINGS<T> = nullptr>
inline auto nparray_to_mat3(const py::array_t<T>& array_np) -> Matrix3<T> {
    NPARRAY_TO_MATRIX(Matrix3<T>, array_np);
}

template <typename T, SFINAE_CONVERSIONS_BINDINGS<T> = nullptr>
inline auto nparray_to_mat4(const py::array_t<T>& array_np) -> Matrix4<T> {
    NPARRAY_TO_MATRIX(Matrix4<T>, array_np);
}

// -------------------------------------------------------------------------- //
//                 Conversions from Buffer Protocol to Math3d                 //
// -------------------------------------------------------------------------- //

template <typename T, SFINAE_CONVERSIONS_BINDINGS<T> = nullptr>
inline auto buffer_to_vec4(const py::buffer& buff) -> Vector4<T> {
    BUFFER_TO_VECTOR(Vector4<T>, buff);
}

template <typename T, SFINAE_CONVERSIONS_BINDINGS<T> = nullptr>
inline auto buffer_to_vec3(const py::buffer& buff) -> Vector3<T> {
    BUFFER_TO_VECTOR(Vector3<T>, buff);
}

template <typename T, SFINAE_CONVERSIONS_BINDINGS<T> = nullptr>
inline auto buffer_to_vec2(const py::buffer& buff) -> Vector2<T> {
    BUFFER_TO_VECTOR(Vector2<T>, buff);
}

}  // namespace math

#if defined(_MSC_VER)
#pragma warning(pop)
#endif
