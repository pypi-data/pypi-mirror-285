#pragma once

#include <cmath>
#include <iomanip>

#include <math/mat3_t_decl.hpp>

#include <math/impl/mat3_t_scalar_impl.hpp>
#include <math/impl/mat3_t_sse_impl.hpp>
#include <math/impl/mat3_t_avx_impl.hpp>

#include <math/quat_t.hpp>
#include <math/euler_t.hpp>

namespace math {

// ***************************************************************************//
//                           Factory functions                                //
// ***************************************************************************//

template <typename T>
auto Matrix3<T>::setFromQuaternion(const Quat& quat) -> void {
    // Just in case, make sure the quaternion is normalized
    auto quat_normalized = quat.normalized();

    auto x = quat_normalized.x();
    auto y = quat_normalized.y();
    auto z = quat_normalized.z();
    auto w = quat_normalized.w();

    auto xx = x * x;
    auto yy = y * y;
    auto zz = z * z;
    auto xy = x * y;
    auto wz = w * z;
    auto xz = x * z;
    auto wy = w * y;
    auto yz = y * z;
    auto wx = w * x;

    constexpr auto ONE = static_cast<T>(1.0);
    constexpr auto TWO = static_cast<T>(2.0);

    m_Elements[0][0] = ONE - TWO * (yy + zz);
    m_Elements[1][0] = TWO * (xy - wz);
    m_Elements[2][0] = TWO * (xz + wy);

    m_Elements[0][1] = TWO * (xy + wz);
    m_Elements[1][1] = ONE - TWO * (xx + zz);
    m_Elements[2][1] = TWO * (yz - wx);

    m_Elements[0][2] = TWO * (xz - wy);
    m_Elements[1][2] = TWO * (yz + wx);
    m_Elements[2][2] = ONE - TWO * (xx + yy);
}

template <typename T>
auto Matrix3<T>::setFromEuler(const Euler<T>& euler) -> void {
    setFromQuaternion(Quat(euler));
}

template <typename T>
auto Matrix3<T>::setFromTransform(const Mat4& m) -> void {
    m_Elements[0][0] = m(0, 0);
    m_Elements[1][0] = m(0, 1);
    m_Elements[2][0] = m(0, 2);

    m_Elements[0][1] = m(1, 0);
    m_Elements[1][1] = m(1, 1);
    m_Elements[2][1] = m(1, 2);

    m_Elements[0][2] = m(2, 0);
    m_Elements[1][2] = m(2, 1);
    m_Elements[2][2] = m(2, 2);
}

template <typename T>
auto Matrix3<T>::RotationX(T angle) -> Matrix3<T> {
    auto cos_t = std::cos(angle);
    auto sin_t = std::sin(angle);
    // clang-format off
    return Matrix3<T>(
        1.0, 0.0, 0.0,
        0.0, cos_t, -sin_t,
        0.0, sin_t, cos_t);
    // clang-format on
}

template <typename T>
auto Matrix3<T>::RotationY(T angle) -> Matrix3<T> {
    auto cos_t = std::cos(angle);
    auto sin_t = std::sin(angle);
    // clang-format off
    return Matrix3<T>(
        cos_t, 0.0, sin_t,
          0.0, 1.0,   0.0,
       -sin_t, 0.0, cos_t);
    // clang-format on
}

template <typename T>
auto Matrix3<T>::RotationZ(T angle) -> Matrix3<T> {
    auto cos_t = std::cos(angle);
    auto sin_t = std::sin(angle);
    // clang-format off
    return Matrix3<T>(
        cos_t, -sin_t, 0.0,
        sin_t,  cos_t, 0.0,
          0.0,    0.0, 1.0);
    // clang-format on
}

template <typename T>
auto Matrix3<T>::Scale(T scale_x, T scale_y, T scale_z) -> Matrix3<T> {
    // clang-format off
    return Matrix3<T>(
        scale_x,     0.0,     0.0,
            0.0, scale_y,     0.0,
            0.0,     0.0, scale_z);
    // clang-format on
}

template <typename T>
auto Matrix3<T>::Scale(const Vector3<T>& scale) -> Matrix3<T> {
    // clang-format off
    return Matrix3<T>(
        scale.x(),       0.0,       0.0,
              0.0, scale.y(),       0.0,
              0.0,       0.0, scale.z());
    // clang-format on
}

template <typename T>
auto Matrix3<T>::Identity() -> Matrix3<T> {
    // clang-format off
    return Matrix3<T>(
        1.0, 0.0, 0.0,
        0.0, 1.0, 0.0,
        0.0, 0.0, 1.0);
    // clang-format on
}

template <typename T>
auto Matrix3<T>::Zeros() -> Matrix3<T> {
    return Matrix3<T>();
}

// ***************************************************************************//
//                     Matrix Operations and Functions                        //
// ***************************************************************************//

template <typename T>
using SFINAE_MAT3_GUARD = typename std::enable_if<IsScalar<T>::value>::type*;

/// Returns the tranpose of the given matrix
template <typename T, SFINAE_MAT3_GUARD<T> = nullptr>
LM_INLINE auto transpose(const Matrix3<T>& mat) -> Matrix3<T> {
    Matrix3<T> dst = mat;
    scalar::kernel_transpose_inplace_mat3<T>(dst.elements());
    return dst;
}

template <typename T, SFINAE_MAT3_GUARD<T> = nullptr>
LM_INLINE auto tranposeInPlace(Matrix3<T>& mat) -> void {  // NOLINT
    scalar::kernel_transpose_inplace_mat3<T>(mat.elements());
}

/// Returns the trace (sum of diagonal elements) of the matrix
template <typename T, SFINAE_MAT3_GUARD<T> = nullptr>
LM_INLINE auto trace(const Matrix3<T>& mat) -> T {
    return scalar::kernel_trace_mat3<T>(mat.elements());
}

/// Returns the determinant of the matrix
template <typename T, SFINAE_MAT3_GUARD<T> = nullptr>
LM_INLINE auto determinant(const Matrix3<T>& mat) -> T {
    return scalar::kernel_determinant_mat3<T>(mat.elements());
}

/// Returns the inverse of the matrix
template <typename T, SFINAE_MAT3_GUARD<T> = nullptr>
LM_INLINE auto inverse(const Matrix3<T>& mat) -> Matrix3<T> {
    Matrix3<T> dst;
    scalar::kernel_inverse_mat3<T>(dst.elements(), mat.elements());
    return dst;
}

template <typename T, SFINAE_MAT3_GUARD<T> = nullptr>
LM_INLINE auto operator+(const Matrix3<T>& lhs, const Matrix3<T>& rhs)
    -> Matrix3<T> {
    Matrix3<T> dst;
    scalar::kernel_add_mat3<T>(dst.elements(), lhs.elements(), rhs.elements());
    return dst;
}

template <typename T, SFINAE_MAT3_GUARD<T> = nullptr>
LM_INLINE auto operator-(const Matrix3<T>& lhs, const Matrix3<T>& rhs)
    -> Matrix3<T> {
    Matrix3<T> dst;
    scalar::kernel_sub_mat3<T>(dst.elements(), lhs.elements(), rhs.elements());
    return dst;
}

template <typename T, SFINAE_MAT3_GUARD<T> = nullptr>
LM_INLINE auto operator*(double scale, const Matrix3<T>& mat) -> Matrix3<T> {
    Matrix3<T> dst;
    scalar::kernel_scale_mat3<T>(dst.elements(), static_cast<T>(scale),
                                 mat.elements());
    return dst;
}

template <typename T, SFINAE_MAT3_GUARD<T> = nullptr>
LM_INLINE auto operator*(const Matrix3<T>& mat, double scale) -> Matrix3<T> {
    Matrix3<T> dst;
    scalar::kernel_scale_mat3<T>(dst.elements(), static_cast<T>(scale),
                                 mat.elements());
    return dst;
}

template <typename T, SFINAE_MAT3_GUARD<T> = nullptr>
LM_INLINE auto operator*(const Matrix3<T>& lhs, const Matrix3<T>& rhs)
    -> Matrix3<T> {
    Matrix3<T> dst;
    scalar::kernel_matmul_mat3<T>(dst.elements(), lhs.elements(),
                                  rhs.elements());
    return dst;
}

template <typename T, SFINAE_MAT3_GUARD<T> = nullptr>
LM_INLINE auto operator*(const Matrix3<T>& lhs_mat, const Vector3<T>& rhs_vec)
    -> Vector3<T> {
    Vector3<T> dst;
    scalar::kernel_matmul_vec_mat3<T>(dst.elements(), lhs_mat.elements(),
                                      rhs_vec.elements());
    return dst;
}

template <typename T, SFINAE_MAT3_GUARD<T> = nullptr>
LM_INLINE auto hadamard(const Matrix3<T>& lhs, const Matrix3<T>& rhs)
    -> Matrix3<T> {
    Matrix3<T> dst;
    scalar::kernel_hadamard_mat3<T>(dst.elements(), lhs.elements(),
                                    rhs.elements());
    return dst;
}

template <typename T, SFINAE_MAT3_GUARD<T> = nullptr>
LM_INLINE auto operator==(const Matrix3<T>& lhs, const Matrix3<T>& rhs)
    -> bool {
    return scalar::kernel_compare_eq_mat3<T>(lhs.elements(), rhs.elements());
}

template <typename T, SFINAE_MAT3_GUARD<T> = nullptr>
LM_INLINE auto operator!=(const Matrix3<T>& lhs, const Matrix3<T>& rhs)
    -> bool {
    return !scalar::kernel_compare_eq_mat3<T>(lhs.elements(), rhs.elements());
}

template <typename T, SFINAE_MAT3_GUARD<T> = nullptr>
auto operator<<(std::ostream& output_stream, const Matrix3<T>& src)
    -> std::ostream& {
    constexpr int PRECISION_DIGITS = 10;
    output_stream << std::setprecision(PRECISION_DIGITS);
    output_stream << "(" << src(0, 0) << ", " << src(0, 1) << ", " << src(0, 2)
                  << ",\n";
    output_stream << " " << src(1, 0) << ", " << src(1, 1) << ", " << src(1, 2)
                  << ",\n";
    output_stream << " " << src(2, 0) << ", " << src(2, 1) << ", " << src(2, 2)
                  << ")";
    return output_stream;
}

template <typename T, SFINAE_MAT3_GUARD<T> = nullptr>
auto operator>>(std::istream& input_stream, Matrix3<T>& dst) -> std::istream& {
    // Based on ignition-math implementation https://bit.ly/3MPgPcW
    input_stream.setf(std::ios_base::skipws);
    // Temporary place to store the inputs given by the user
    std::array<T, Matrix3<T>::BUFFER_SIZE> mat;
    // Get these many items/elements from the input stream (row-major order)
    // NOLINTNEXTLINE
    input_stream >> mat[0] >> mat[1] >> mat[2] >> mat[3] >> mat[4] >> mat[5] >>
        mat[6] >> mat[7] >> mat[8];  // NOLINT
    if (!input_stream.fail()) {
        dst(0, 0) = mat[0];
        dst(0, 1) = mat[1];
        dst(0, 2) = mat[2];

        dst(1, 0) = mat[3];
        dst(1, 1) = mat[4];
        dst(1, 2) = mat[5];  // NOLINT

        dst(2, 0) = mat[6];  // NOLINT
        dst(2, 1) = mat[7];  // NOLINT
        dst(2, 2) = mat[8];  // NOLINT
    }
    return input_stream;
}

// ***************************************************************************//
//                       Matrix Methods implementation                        //
// ***************************************************************************//

template <typename T>
LM_INLINE auto Matrix3<T>::operator*(const Vector3<T>& rhs) -> Vector3<T> {
    return ::math::operator*(*this, rhs);
}

template <typename T>
LM_INLINE auto Matrix3<T>::operator*(const Matrix3<T>& rhs) -> Matrix3<T> {
    return ::math::operator*(*this, rhs);
}

}  // namespace math
