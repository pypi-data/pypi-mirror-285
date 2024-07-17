#pragma once

#include <math/vec3_t_decl.hpp>

#include <math/impl/vec3_t_scalar_impl.hpp>
#include <math/impl/vec3_t_sse_impl.hpp>
#include <math/impl/vec3_t_avx_impl.hpp>

namespace math {

// ***************************************************************************//
//                   Vector3 helper functions and operators                   //
// ***************************************************************************//

template <typename T>
using SFINAE_VEC3_GUARD = typename std::enable_if<IsScalar<T>::value>::type*;

/// \brief Returns the square of the norm-2 of the vector
template <typename T, SFINAE_VEC3_GUARD<T> = nullptr>
LM_INLINE auto squareNorm(const Vector3<T>& vec) -> T {
    return scalar::kernel_length_square_vec3<T>(vec.elements());
}

/// \brief Returns the norm-2 of the vector
template <typename T, SFINAE_VEC3_GUARD<T> = nullptr>
LM_INLINE auto norm(const Vector3<T>& vec) -> T {
    return std::sqrt(scalar::kernel_length_square_vec3<T>(vec.elements()));
}

/// \brief Returns a normalized version of this vector
template <typename T, SFINAE_VEC3_GUARD<T> = nullptr>
LM_INLINE auto normalize(const Vector3<T>& vec) -> Vector3<T> {
    Vector3<T> vec_normalized = vec;
    scalar::kernel_normalize_in_place_vec3<T>(vec_normalized.elements());
    return vec_normalized;
}

/// \brief Normalizes in-place the given vector
template <typename T, SFINAE_VEC3_GUARD<T> = nullptr>
LM_INLINE auto normalize_in_place(Vector3<T>& vec) -> void {  // NOLINT
    scalar::kernel_normalize_in_place_vec3<T>(vec.elements());
}

/// \brief Returns the dot-product of the given two vectors
template <typename T, SFINAE_VEC3_GUARD<T> = nullptr>
LM_INLINE auto dot(const Vector3<T>& lhs, const Vector3<T>& rhs) -> T {
    return scalar::kernel_dot_vec3<T>(lhs.elements(), rhs.elements());
}

/// \brief Returns the cross-product of the given two vectors
template <typename T, SFINAE_VEC3_GUARD<T> = nullptr>
LM_INLINE auto cross(const Vector3<T>& lhs, const Vector3<T>& rhs)
    -> Vector3<T> {
    Vector3<T> vec_cross;
    scalar::kernel_cross_vec3<T>(vec_cross.elements(), lhs.elements(),
                                 rhs.elements());
    return vec_cross;
}

/// \brief Returns the vector-sum of two 3d vector operands
///
/// \tparam T Type of scalar used by both scalar and vector operands
///
/// \param[in] lhs Left-hand-side operand of the vector-sum
/// \param[in] rhs Right-hand-side operand of the vector-sum
template <typename T, SFINAE_VEC3_GUARD<T> = nullptr>
LM_INLINE auto operator+(const Vector3<T>& lhs, const Vector3<T>& rhs)
    -> Vector3<T> {
    Vector3<T> dst;
    scalar::kernel_add_vec3<T>(dst.elements(), lhs.elements(), rhs.elements());
    return dst;
}

/// \brief Returns the vector-difference of two 3d vector operands
///
/// \tparam T Type of scalar used by both scalar and vector operands
///
/// \param[in] lhs Left-hand-side operand of the vector-sum
/// \param[in] rhs Right-hand-side operand of the vector-sum
template <typename T, SFINAE_VEC3_GUARD<T> = nullptr>
LM_INLINE auto operator-(const Vector3<T>& lhs, const Vector3<T>& rhs)
    -> Vector3<T> {
    Vector3<T> dst;
    scalar::kernel_sub_vec3<T>(dst.elements(), lhs.elements(), rhs.elements());
    return dst;
}

/// \brief Returns the scalar-vector product of a scalar and 3d vector operands
///
/// \tparam T Type of scalar used by both scalar and vector operands
///
/// \param[in] scale Scalar value by which to scale the second operand
/// \param[in] vec Vector in 3d-space which we want to scale
template <typename T, SFINAE_VEC3_GUARD<T> = nullptr>
LM_INLINE auto operator*(double scale, const Vector3<T>& vec) -> Vector3<T> {
    Vector3<T> dst;
    scalar::kernel_scale_vec3<T>(dst.elements(), static_cast<T>(scale),
                                 vec.elements());
    return dst;
}

/// \brief Returns the vector-scalar product of a 3d vector and scalar operands
///
/// \tparam T Type of scalar used by both vector and scalar operands
///
/// \param[in] vec Vector in 3d-space which we want to scale
/// \param[in] scale Scalar value by which to scale the first operand
template <typename T, SFINAE_VEC3_GUARD<T> = nullptr>
LM_INLINE auto operator*(const Vector3<T>& vec, double scale) -> Vector3<T> {
    Vector3<T> dst;
    scalar::kernel_scale_vec3(dst.elements(), static_cast<T>(scale),
                              vec.elements());
    return dst;
}

/// \brief Returns the element-wise product of two 3d vector operands
///
/// \tparam T Type of scalar value used by the 3d-vector operands
///
/// \param[in] lhs Left-hand-side operand of the element-wise product
/// \param[in] rhs Right-hand-side operand of the element-wise product
template <typename T, SFINAE_VEC3_GUARD<T> = nullptr>
LM_INLINE auto operator*(const Vector3<T>& lhs, const Vector3<T>& rhs)
    -> Vector3<T> {
    Vector3<T> dst;
    scalar::kernel_hadamard_vec3<T>(dst.elements(), lhs.elements(),
                                    rhs.elements());
    return dst;
}

/// \brief Returns the additive inverse of the given vector
///
/// \tparam T Type of scalar value used by the 3d-vector operand
///
/// \param[in] vec The vector whose inverse we want
/// \returns The additive inverse of the given vector
template <typename T, SFINAE_VEC3_GUARD<T> = nullptr>
LM_INLINE auto operator-(const Vector3<T>& vec) -> Vector3<T> {
    return Vector3<T>(-vec.x(), -vec.y(), -vec.z());
}

/// \brief Checks if two given vectors are "equal" (within epsilon margin)
///
/// \tparam T Type of scalar value used by the 3d-vector operands
///
/// \param[in] lhs Left-hand-side operand of the comparison
/// \param[in] rhs Right-hand-side operand of the comparison
/// \returns true if the given vectors are within a pre-defined epsilon margin
template <typename T, SFINAE_VEC3_GUARD<T> = nullptr>
LM_INLINE auto operator==(const Vector3<T>& lhs, const Vector3<T>& rhs)
    -> bool {
    return scalar::kernel_compare_eq_vec3<T>(lhs.elements(), rhs.elements());
}

/// \brief Checks if two given vectors are not "equal" (within epsilon margin)
///
/// \tparam T Type of scalar value used by the 3d-vector operands
///
/// \param[in] lhs Left-hand-side operand of the comparison
/// \param[in] rhs Right-hand-side operand of the comparison
/// \returns true if the given vectors are not within a pre-defined margin
template <typename T, SFINAE_VEC3_GUARD<T> = nullptr>
LM_INLINE auto operator!=(const Vector3<T>& lhs, const Vector3<T>& rhs)
    -> bool {
    return !scalar::kernel_compare_eq_vec3<T>(lhs.elements(), rhs.elements());
}

/// \brief Prints the given 3d vector to the given output stream
///
/// \tparam T Type of scalar used by the 3d vector operand
///
/// \param[in,out] output_stream The output stream to write the vector to
/// \param[in] src The vector we want to print to the output stream
/// \returns A reference to the modified output stream (to concatenate calls)
template <typename T, SFINAE_VEC3_GUARD<T> = nullptr>
auto operator<<(std::ostream& output_stream, const Vector3<T>& src)
    -> std::ostream& {
    output_stream << "(" << src.x() << ", " << src.y() << ", " << src.z()
                  << ")";
    return output_stream;
}

/// \brief Reads a 3d vector from the given input stream
///
/// \tparam T Type of scalar used by the 3d vector operand
///
/// \param[in,out] input_stream The input stream from which to read the vector
/// \param[out] dst The vector in which to place the read values
/// \returns A reference to the modified input stream (to concatenate calls)
template <typename T, SFINAE_VEC3_GUARD<T> = nullptr>
auto operator>>(std::istream& input_stream, Vector3<T>& dst) -> std::istream& {
    // Based on ignition-math implementation https://bit.ly/3iqAVgS
    T x_val{};
    T y_val{};
    T z_val{};

    input_stream.setf(std::ios_base::skipws);
    input_stream >> x_val >> y_val >> z_val;
    if (!input_stream.fail()) {
        dst.x() = x_val;
        dst.y() = y_val;
        dst.z() = z_val;
    }

    return input_stream;
}

// ***************************************************************************//
//                           Vector3-type methods                             //
// ***************************************************************************//

template <typename T>
auto Vector3<T>::lengthSquare() const -> T {
    return ::math::squareNorm<T>(*this);
}

template <typename T>
auto Vector3<T>::length() const -> T {
    return ::math::norm<T>(*this);
}

template <typename T>
auto Vector3<T>::normalize() -> void {
    ::math::normalize_in_place<T>(*this);
}

template <typename T>
auto Vector3<T>::normalized() const -> Vector3<T> {
    return ::math::normalize<T>(*this);
}

template <typename T>
auto Vector3<T>::dot(const Vector3<T>& rhs) const -> T {
    return ::math::dot<T>(*this, rhs);
}

template <typename T>
auto Vector3<T>::cross(const Vector3<T>& rhs) const -> Vector3<T> {
    return ::math::cross<T>(*this, rhs);
}

}  // namespace math
