#pragma once

#include <math/vec4_t_decl.hpp>

#include <math/impl/vec4_t_scalar_impl.hpp>
#include <math/impl/vec4_t_sse_impl.hpp>
#include <math/impl/vec4_t_avx_impl.hpp>

namespace math {

// ***************************************************************************//
//                   Vector4 helper functions and operators                   //
// ***************************************************************************//

template <typename T>
using SFINAE_VEC4_GUARD = typename std::enable_if<IsScalar<T>::value>::type*;

template <typename T, SFINAE_VEC4_GUARD<T> = nullptr>
LM_INLINE auto squareNorm(const Vector4<T>& vec) -> T {
#if defined(MATH_AVX_ENABLED)
    return avx::kernel_length_square_vec4<T>(vec.elements());
#elif defined(MATH_SSE_ENABLED)
    return sse::kernel_length_square_vec4<T>(vec.elements());
#else
    return scalar::kernel_length_square_vec4<T>(vec.elements());
#endif
}

/// \brief Returns the norm-2 of the vector
template <typename T, SFINAE_VEC4_GUARD<T> = nullptr>
LM_INLINE auto norm(const Vector4<T>& vec) -> T {
#if defined(MATH_AVX_ENABLED)
    return avx::kernel_length_vec4<T>(vec.elements());
#elif defined(MATH_SSE_ENABLED)
    return sse::kernel_length_vec4<T>(vec.elements());
#else
    return std::sqrt(scalar::kernel_length_square_vec4<T>(vec.elements()));
#endif
}

/// \brief Returns a normalized version of this vector
template <typename T, SFINAE_VEC4_GUARD<T> = nullptr>
LM_INLINE auto normalize(const Vector4<T>& vec) -> Vector4<T> {
    Vector4<T> vec_normalized = vec;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_normalize_in_place_vec4<T>(vec_normalized.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_normalize_in_place_vec4<T>(vec_normalized.elements());
#else
    scalar::kernel_normalize_in_place_vec4<T>(vec_normalized.elements());
#endif
    return vec_normalized;
}

/// \brief Normalizes in-place the given vector
template <typename T, SFINAE_VEC4_GUARD<T> = nullptr>
LM_INLINE auto normalize_in_place(Vector4<T>& vec) -> void {  // NOLINT
#if defined(MATH_AVX_ENABLED)
    avx::kernel_normalize_in_place_vec4<T>(vec.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_normalize_in_place_vec4<T>(vec.elements());
#else
    scalar::kernel_normalize_in_place_vec4<T>(vec.elements());
#endif
}

/// \brief Returns the dot-product of the given two vectors
template <typename T, SFINAE_VEC4_GUARD<T> = nullptr>
LM_INLINE auto dot(const Vector4<T>& lhs, const Vector4<T>& rhs) -> T {
#if defined(MATH_AVX_ENABLED)
    return avx::kernel_dot_vec4<T>(lhs.elements(), rhs.elements());
#elif defined(MATH_SSE_ENABLED)
    return sse::kernel_dot_vec4<T>(lhs.elements(), rhs.elements());
#else
    return scalar::kernel_dot_vec4<T>(lhs.elements(), rhs.elements());
#endif
}

/// \brief Returns the vector-sum of two 4d vector operands
///
/// \tparam T Type of scalar value used for the 4d-vector operands
///
/// This operator implements an element-wise sum of two Vector4 operands given
/// as input arguments. The internal operator selects the appropriate "kernel"
/// (just a function) to which to call, depending on whether or not the library
/// was compiled using SIMD support (i.e. SSE and AVX function intrinsics will
/// be used to handle the operation).
///
/// \param[in] lhs Left-hand-side operand of the vector-sum
/// \param[in] rhs Right-hand-side operand of the vector-sum
template <typename T, SFINAE_VEC4_GUARD<T> = nullptr>
LM_INLINE auto operator+(const Vector4<T>& lhs, const Vector4<T>& rhs)
    -> Vector4<T> {
    Vector4<T> dst;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_add_vec4<T>(dst.elements(), rhs.elements(), lhs.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_add_vec4<T>(dst.elements(), lhs.elements(), rhs.elements());
#else
    scalar::kernel_add_vec4<T>(dst.elements(), lhs.elements(), rhs.elements());
#endif
    return dst;
}

/// \brief Returns the vector-difference of two 4d vector operands
///
/// \tparam T Type of scalar value used for the 4d-vector operands
///
/// This operator implements an element-wise difference of two Vector4 operands
/// given as input arguments. The internal operator selects the appropriate
/// "kernel" (just a function) to which to call, depending on whether or not the
/// library was compiled using SIMD support (i.e. SSE and AVX function
/// intrinsics will be used to handle the operation).
///
/// \param[in] lhs Left-hand-side operand of the vector-sum
/// \param[in] rhs Right-hand-side operand of the vector-sum
template <typename T, SFINAE_VEC4_GUARD<T> = nullptr>
LM_INLINE auto operator-(const Vector4<T>& lhs, const Vector4<T>& rhs)
    -> Vector4<T> {
    Vector4<T> dst;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_sub_vec4<T>(dst.elements(), lhs.elements(), rhs.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_sub_vec4<T>(dst.elements(), lhs.elements(), rhs.elements());
#else
    scalar::kernel_sub_vec4<T>(dst.elements(), lhs.elements(), rhs.elements());
#endif
    return dst;
}

/// \brief Returns the scalar-vector product of a scalar and 4d vector operands
///
/// \tparam T Type of scalar used by both scalar and vector operands
///
/// This operator implements the scalar-vector product of two operands (a scalar
/// and a vector in that order) given as input arguments. The internal operator
/// selects the appropriate "kernel" (just a function) to which to call,
/// depending on whether or not the library was compiled using SIMD support
/// (i.e. SSE and AVX function intrinsics will be used to handle the operation).
///
/// \param[in] scale Scalar value by which to scale the second operand
/// \param[in] vec Vector in 4d-space which we want to scale
template <typename T, SFINAE_VEC4_GUARD<T> = nullptr>
LM_INLINE auto operator*(double scale, const Vector4<T>& vec) -> Vector4<T> {
    Vector4<T> dst;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_scale_vec4<T>(dst.elements(), static_cast<T>(scale),
                              vec.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_scale_vec4<T>(dst.elements(), static_cast<T>(scale),
                              vec.elements());
#else
    scalar::kernel_scale_vec4<T>(dst.elements(), static_cast<T>(scale),
                                 vec.elements());
#endif
    return dst;
}

/// \brief Returns the vector-scalar product of a 4d vector and scalar operands
///
/// \tparam T Type of scalar used by both vector and scalar operands
///
/// This operator implements the vector-scalar product of two operands (a vector
/// and a scalar in that order) given as input arguments. The internal operator
/// selects the appropriate "kernel" (just a function) to which to call,
/// depending on whether or not the library was compiled using SIMD support
/// (i.e. SSE and AVX function intrinsics will be used to handle the operation).
///
/// \param[in] vec Vector in 4d-space which we want to scale
/// \param[in] scale Scalar value by which to scale the first operand
template <typename T, SFINAE_VEC4_GUARD<T> = nullptr>
LM_INLINE auto operator*(const Vector4<T>& vec, double scale) -> Vector4<T> {
    Vector4<T> dst;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_scale_vec4<T>(dst.elements(), static_cast<T>(scale),
                              vec.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_scale_vec4<T>(dst.elements(), static_cast<T>(scale),
                              vec.elements());
#else
    scalar::kernel_scale_vec4<T>(dst.elements(), static_cast<T>(scale),
                                 vec.elements());
#endif
    return dst;
}

/// \brief Returns the element-wise product of two 4d vector operands
///
/// \tparam T Type of scalar value used by the 4d-vector operands
///
/// This operator implements an element-wise product (Hadamard-Schur product) of
/// two Vector4 operands given as input arguments. The internal operator selects
/// the appropriate "kernel" (just a function) to which to call, depending on
/// whether or not the library was compiled using SIMD support (i.e. SSE and AVX
/// function intrinsics will be used to handle the operation).
///
/// \param[in] lhs Left-hand-side operand of the element-wise product
/// \param[in] rhs Right-hand-side operand of the element-wise product
template <typename T, SFINAE_VEC4_GUARD<T> = nullptr>
LM_INLINE auto operator*(const Vector4<T>& lhs, const Vector4<T>& rhs)
    -> Vector4<T> {
    Vector4<T> dst;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_hadamard_vec4<T>(dst.elements(), lhs.elements(),
                                 rhs.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_hadamard_vec4<T>(dst.elements(), lhs.elements(),
                                 rhs.elements());
#else
    scalar::kernel_hadamard_vec4<T>(dst.elements(), lhs.elements(),
                                    rhs.elements());
#endif
    return dst;
}

/// \brief Returns the additive inverse of the given vector
///
/// \tparam T Type of scalar value used by the 4d-vector operand
///
/// \param[in] vec The vector whose inverse we want
/// \returns The additive inverse of the given vector
template <typename T, SFINAE_VEC4_GUARD<T> = nullptr>
LM_INLINE auto operator-(const Vector4<T>& vec) -> Vector4<T> {
    return Vector4<T>(-vec.x(), -vec.y(), -vec.z(), -vec.w());
}

/// \brief Checks if two given vectors are "equal" (within epsilon margin)
///
/// \tparam Scalar_T Type of scalar value used by the 4d-vector operands
///
/// This operator implements an "np.allclose"-like operation (numpy's allclose
/// function), checking if the corresponding (x,y,z) entries of both operands
/// are within a certain margin "epsilon" (pre-defined constant). There was an
/// "equal"-like SIMD instruction that implements floating point comparisons,
/// however, we're not using it as single-precision floating point operations
/// and transformation functions within the library might result in compounding
/// errors that the user might want to test a small margin of error tuned
/// appropriately (specially for single-precision floating point types)
///
/// \param[in] lhs Left-hand-side operand of the comparison
/// \param[in] rhs Right-hand-side operand of the comparison
/// \returns true if the given vectors are within a pre-defined epsilon margin
template <typename T, SFINAE_VEC4_GUARD<T> = nullptr>
LM_INLINE auto operator==(const Vector4<T>& lhs, const Vector4<T>& rhs)
    -> bool {
    return scalar::kernel_compare_eq_vec4<T>(lhs.elements(), rhs.elements());
}

/// \brief Checks if two given vectors are not "equal" (within epsilon margin)
///
/// \tparam Scalar_T Type of scalar value used by the 4d-vector operands
///
/// \param[in] lhs Left-hand-side operand of the comparison
/// \param[in] rhs Right-hand-side operand of the comparison
/// \returns true if the given vectors are not within a pre-defined margin
template <typename T, SFINAE_VEC4_GUARD<T> = nullptr>
LM_INLINE auto operator!=(const Vector4<T>& lhs, const Vector4<T>& rhs)
    -> bool {
    return !scalar::kernel_compare_eq_vec4<T>(lhs.elements(), rhs.elements());
}

/// \brief Prints the given 4d vector to the given output stream
///
/// \tparam T Type of scalar used by the 4d vector operand
///
/// \param[in,out] output_stream The output stream to write the vector to
/// \param[in] src The vector we want to print to the output stream
/// \returns A reference to the modified output stream (to concatenate calls)
template <typename T, SFINAE_VEC4_GUARD<T> = nullptr>
auto operator<<(std::ostream& output_stream, const Vector4<T>& src)
    -> std::ostream& {
    output_stream << "(" << src.x() << ", " << src.y() << ", " << src.z()
                  << ", " << src.w() << ")";
    return output_stream;
}

/// \brief Reads a 4d vector from the given input stream
///
/// \tparam T Type of scalar used by the 4d vector operand
///
/// \param[in,out] input_stream The input stream from which to read the vector
/// \param[out] dst The vector in which to place the read values
/// \returns A reference to the modified input stream (to concatenate calls)
template <typename T, SFINAE_VEC4_GUARD<T> = nullptr>
auto operator>>(std::istream& input_stream, Vector4<T>& dst) -> std::istream& {
    // Based on ignition-math implementation https://bit.ly/3iqAVgS
    T x_val{};
    T y_val{};
    T z_val{};
    T w_val{};

    input_stream.setf(std::ios_base::skipws);
    input_stream >> x_val >> y_val >> z_val >> w_val;
    if (!input_stream.fail()) {
        dst.x() = x_val;
        dst.y() = y_val;
        dst.z() = z_val;
        dst.w() = w_val;
    }

    return input_stream;
}

// ***************************************************************************//
//                           Vector4-type methods                             //
// ***************************************************************************//

template <typename T>
auto Vector4<T>::lengthSquare() const -> T {
    return ::math::squareNorm<T>(*this);
}

template <typename T>
auto Vector4<T>::length() const -> T {
    return ::math::norm<T>(*this);
}

template <typename T>
auto Vector4<T>::normalize() -> void {
    ::math::normalize_in_place<T>(*this);
}

template <typename T>
auto Vector4<T>::normalized() const -> Vector4<T> {
    return ::math::normalize<T>(*this);
}

template <typename T>
auto Vector4<T>::dot(const Vector4<T>& rhs) const -> T {
    return ::math::dot<T>(*this, rhs);
}

}  // namespace math
