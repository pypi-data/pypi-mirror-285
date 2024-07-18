#pragma once

#include <cmath>
#include <iomanip>

#include <math/mat4_t_decl.hpp>

#include <math/impl/mat4_t_scalar_impl.hpp>
#include <math/impl/mat4_t_sse_impl.hpp>
#include <math/impl/mat4_t_avx_impl.hpp>

#include <math/quat_t.hpp>
#include <math/euler_t.hpp>
#include <math/mat3_t.hpp>

namespace math {

template <typename T>
auto Matrix4<T>::setPosition(const Vec3& position) -> void {
    m_Elements[3][0] = position.x();
    m_Elements[3][1] = position.y();
    m_Elements[3][2] = position.z();
    m_Elements[3][3] = static_cast<T>(1.0);
}

template <typename T>
auto Matrix4<T>::setRotation(const Mat3& rotmat) -> void {
    m_Elements[0][0] = rotmat(0, 0);
    m_Elements[0][1] = rotmat(1, 0);
    m_Elements[0][2] = rotmat(2, 0);

    m_Elements[1][0] = rotmat(0, 1);
    m_Elements[1][1] = rotmat(1, 1);
    m_Elements[1][2] = rotmat(2, 1);

    m_Elements[2][0] = rotmat(0, 2);
    m_Elements[2][1] = rotmat(1, 2);
    m_Elements[2][2] = rotmat(2, 2);
}

template <typename T>
auto Matrix4<T>::setRotation(const Quat& quat) -> void {
    setRotation(Mat3(quat));
}

template <typename T>
auto Matrix4<T>::setRotation(const Euler<T>& euler) -> void {
    setRotation(Mat3(euler));
}

// ***************************************************************************//
//                       Factory functions implementation                     //
// ***************************************************************************//

template <typename T>
auto Matrix4<T>::RotationX(T angle) -> Matrix4<T> {
    auto cos_t = std::cos(angle);
    auto sin_t = std::sin(angle);
    // clang-format off
    return Matrix4<T>(
        1.0,   0.0,    0.0, 0.0,
        0.0, cos_t, -sin_t, 0.0,
        0.0, sin_t,  cos_t, 0.0,
        0.0,   0.0,    0.0, 1.0);
    // clang-format on
}

template <typename T>
auto Matrix4<T>::RotationY(T angle) -> Matrix4<T> {
    auto cos_t = std::cos(angle);
    auto sin_t = std::sin(angle);
    // clang-format off
    return Matrix4<T>(
        cos_t, 0.0, sin_t, 0.0,
          0.0, 1.0,   0.0, 0.0,
       -sin_t, 0.0, cos_t, 0.0,
          0.0, 0.0,   0.0, 1.0);
    // clang-format on
}

template <typename T>
auto Matrix4<T>::RotationZ(T angle) -> Matrix4<T> {
    auto cos_t = std::cos(angle);
    auto sin_t = std::sin(angle);
    // clang-format off
    return Matrix4<T>(
        cos_t, -sin_t, 0.0, 0.0,
        sin_t,  cos_t, 0.0, 0.0,
          0.0,    0.0, 1.0, 0.0,
          0.0,    0.0, 0.0, 1.0);
    // clang-format on
}

template <typename T>
auto Matrix4<T>::Scale(T scale_x, T scale_y, T scale_z) -> Matrix4<T> {
    // clang-format off
    return Matrix4<T>(
        scale_x,     0.0,     0.0, 0.0,
            0.0, scale_y,     0.0, 0.0,
            0.0,     0.0, scale_z, 0.0,
            0.0,     0.0,     0.0, 1.0);
    // clang-format on
}

template <typename T>
auto Matrix4<T>::Scale(const Vector3<T>& scale) -> Matrix4<T> {
    // clang-format off
    return Matrix4<T>(
        scale.x(),       0.0,       0.0, 0.0,
              0.0, scale.y(),       0.0, 0.0,
              0.0,       0.0, scale.z(), 0.0,
              0.0,       0.0,       0.0, 1.0);
    // clang-format on
}

template <typename T>
auto Matrix4<T>::Translation(const Vector3<T>& position) -> Matrix4<T> {
    // clang-format off
    return Matrix4<T>(
        1.0, 0.0, 0.0, position.x(),
        0.0, 1.0, 0.0, position.y(),
        0.0, 0.0, 1.0, position.z(),
        0.0, 0.0, 0.0,          1.0);
    // clang-format on
}

template <typename T>
auto Matrix4<T>::Perspective(T fov, T aspect, T near, T far) -> Matrix4<T> {
    auto tmp_0 = static_cast<T>(1.0) /
                 std::tan((fov / static_cast<T>(2.0)) *
                          (static_cast<T>(PI) / static_cast<T>(180.0)));
    auto tmp_1 = tmp_0 / aspect;
    auto tmp_2 = near - far;
    auto tmp_3 = (far + near) / tmp_2;
    auto tmp_4 = static_cast<T>(2.0) * (far * near) / tmp_2;

    // clang-format off
    return Matrix4<T>(
            tmp_1,  0.0 ,  0.0 ,  0.0 ,
             0.0 , tmp_0,  0.0 ,  0.0 ,
             0.0 ,  0.0 , tmp_3, tmp_4,
             0.0 ,  0.0 , -1.0 ,  0.0);
    // clang-format on
}

template <typename T>
auto Matrix4<T>::Perspective(T left, T right, T top, T bottom, T near, T far)
    -> Matrix4<T> {
    auto x = static_cast<T>(2.0) * near / (right - left);
    auto y = static_cast<T>(2.0) * near / (top - bottom);

    auto a = (right + left) / (right - left);
    auto b = (top + bottom) / (top - bottom);
    auto c = -(far + near) / (far - near);
    auto d = -static_cast<T>(2.0) * far * near / (far - near);

    // clang-format off
    return Matrix4<T>(
              x  ,  0.0 ,   a  ,  0.0 ,
             0.0 ,   y  ,   b  ,  0.0 ,
             0.0 ,  0.0 ,   c  ,   d  ,
             0.0 ,  0.0 , -1.0 ,  0.0);
    // clang-format on
}

template <typename T>
auto Matrix4<T>::Ortho(T width, T height, T near, T far) -> Matrix4<T> {
    auto tmp_0 = static_cast<T>(2.0) / width;
    auto tmp_1 = static_cast<T>(2.0) / height;
    auto tmp_2 = near - far;
    auto tmp_3 = static_cast<T>(2.0) / tmp_2;
    auto tmp_4 = (far + near) / tmp_2;

    // clang-format off
    return Matrix4<T>(
        tmp_0,  0.0  ,  0.0  ,  0.0  ,
         0.0 , tmp_1 ,  0.0  ,  0.0  ,
         0.0 ,  0.0  , tmp_3 , tmp_4 ,
         0.0 ,  0.0  ,  0.0  ,  1.0);
    // clang-format on
}

template <typename T>
auto Matrix4<T>::Identity() -> Matrix4<T> {
    // clang-format off
    return Matrix4<T>(1.0, 0.0, 0.0, 0.0,
                      0.0, 1.0, 0.0, 0.0,
                      0.0, 0.0, 1.0, 0.0,
                      0.0, 0.0, 0.0, 1.0);
    // clang-format on
}

template <typename T>
auto Matrix4<T>::Zeros() -> Matrix4<T> {
    return Matrix4<T>();
}

// ***************************************************************************//
//                       Matrix Methods implementation                        //
// ***************************************************************************//

template <typename T>
using SFINAE_MAT4_GUARD = typename std::enable_if<IsScalar<T>::value>::type*;

/// \brief Returns the transpose of the given matrix
template <typename T, SFINAE_MAT4_GUARD<T> = nullptr>
LM_INLINE auto transpose(const Matrix4<T>& mat) -> Matrix4<T> {
    Matrix4<T> dst = mat;
    scalar::kernel_transpose_inplace_mat4<T>(dst.elements());
    return dst;
}

/// \brief Transposes the given matrix in-place
template <typename T, SFINAE_MAT4_GUARD<T> = nullptr>
LM_INLINE auto transposeInPlace(Matrix4<T>& mat) -> void {  // NOLINT
    scalar::kernel_transpose_inplace_mat4<T>(mat.elements());
}

/// Returns the trace (sum of diagonal elements) of the matrix
template <typename T, SFINAE_MAT4_GUARD<T> = nullptr>
LM_INLINE auto trace(const Matrix4<T>& mat) -> T {
    return scalar::kernel_trace_mat4<T>(mat.elements());
}

/// Returns the determinant of the matrix
template <typename T, SFINAE_MAT4_GUARD<T> = nullptr>
LM_INLINE auto determinant(const Matrix4<T>& mat) -> T {
    return scalar::kernel_determinant_mat4<T>(mat.elements());
}

/// Returns the inverse of the matrix
template <typename T, SFINAE_MAT4_GUARD<T> = nullptr>
LM_INLINE auto inverse(const Matrix4<T>& mat) -> Matrix4<T> {
    Matrix4<T> dst;
    scalar::kernel_inverse_mat4<T>(dst.elements(), mat.elements());
    return dst;
}

/// \brief Returns the matrix-sum of the two given matrices
template <typename T, SFINAE_MAT4_GUARD<T> = nullptr>
LM_INLINE auto operator+(const Matrix4<T>& lhs, const Matrix4<T>& rhs)
    -> Matrix4<T> {
    Matrix4<T> dst;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_add_mat4<T>(dst.elements(), lhs.elements(), rhs.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_add_mat4<T>(dst.elements(), lhs.elements(), rhs.elements());
#else
    scalar::kernel_add_mat4<T>(dst.elements(), lhs.elements(), rhs.elements());
#endif
    return dst;
}

/// \brief Returns the matrix-difference of the two given matrices
template <typename T, SFINAE_MAT4_GUARD<T> = nullptr>
LM_INLINE auto operator-(const Matrix4<T>& lhs, const Matrix4<T>& rhs)
    -> Matrix4<T> {
    Matrix4<T> dst;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_sub_mat4<T>(dst.elements(), lhs.elements(), rhs.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_sub_mat4<T>(dst.elements(), lhs.elements(), rhs.elements());
#else
    scalar::kernel_sub_mat4<T>(dst.elements(), lhs.elements(), rhs.elements());
#endif
    return dst;
}

/// \brief Returns the scaled version of the given matrix by the given factor
template <typename T, SFINAE_MAT4_GUARD<T> = nullptr>
LM_INLINE auto operator*(double scale, const Matrix4<T>& mat) -> Matrix4<T> {
    Matrix4<T> dst;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_scale_mat4<T>(dst.elements(), static_cast<T>(scale),
                              mat.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_scale_mat4<T>(dst.elements(), static_cast<T>(scale),
                              mat.elements());
#else
    scalar::kernel_scale_mat4<T>(dst.elements(), static_cast<T>(scale),
                                 mat.elements());
#endif
    return dst;
}

/// \brief Returns the scaled version of the given matrix by the given factor
template <typename T, SFINAE_MAT4_GUARD<T> = nullptr>
LM_INLINE auto operator*(const Matrix4<T>& mat, double scale) -> Matrix4<T> {
    Matrix4<T> dst;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_scale_mat4<T>(dst.elements(), static_cast<T>(scale),
                              mat.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_scale_mat4<T>(dst.elements(), static_cast<T>(scale),
                              mat.elements());
#else
    scalar::kernel_scale_mat4<T>(dst.elements(), static_cast<T>(scale),
                                 mat.elements());
#endif
    return dst;
}

/// \brief Returns the matrix product of the two given matrices
template <typename T, SFINAE_MAT4_GUARD<T> = nullptr>
LM_INLINE auto operator*(const Matrix4<T>& lhs, const Matrix4<T>& rhs)
    -> Matrix4<T> {
    Matrix4<T> dst;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_matmul_mat4<T>(dst.elements(), lhs.elements(), rhs.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_matmul_mat4<T>(dst.elements(), lhs.elements(), rhs.elements());
#else
    scalar::kernel_matmul_mat4<T>(dst.elements(), lhs.elements(),
                                  rhs.elements());
#endif
    return dst;
}

/// \brief Returns the matrix-vector product of the given operands
template <typename T, SFINAE_MAT4_GUARD<T> = nullptr>
LM_INLINE auto operator*(const Matrix4<T>& lhs_mat, const Vector4<T>& rhs_vec)
    -> Vector4<T> {
    Vector4<T> dst;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_matmul_vec_mat4<T>(dst.elements(), lhs_mat.elements(),
                                   rhs_vec.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_matmul_vec_mat4<T>(dst.elements(), lhs_mat.elements(),
                                   rhs_vec.elements());
#else
    scalar::kernel_matmul_vec_mat4<T>(dst.elements(), lhs_mat.elements(),
                                      rhs_vec.elements());
#endif
    return dst;
}

/// \brief Returns the element-wise product of the two given matrices
template <typename T, SFINAE_MAT4_GUARD<T> = nullptr>
LM_INLINE auto hadamard(const Matrix4<T>& lhs, const Matrix4<T>& rhs)
    -> Matrix4<T> {
    Matrix4<T> dst;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_hadamard_mat4<T>(dst.elements(), lhs.elements(),
                                 rhs.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_hadamard_mat4<T>(dst.elements(), lhs.elements(),
                                 rhs.elements());
#else
    scalar::kernel_hadamard_mat4<T>(dst.elements(), lhs.elements(),
                                    rhs.elements());
#endif
    return dst;
}

/// \brief Checks if two given matrices are "equal" (within epsilon margin)
template <typename T, SFINAE_MAT4_GUARD<T> = nullptr>
LM_INLINE auto operator==(const Matrix4<T>& lhs, const Matrix4<T>& rhs)
    -> bool {
    return scalar::kernel_compare_eq_mat4<T>(lhs.elements(), rhs.elements());
}

/// \brief Checks if two given matrices are "not equal" (within epsilon margin)
template <typename T, SFINAE_MAT4_GUARD<T> = nullptr>
LM_INLINE auto operator!=(const Matrix4<T>& lhs, const Matrix4<T>& rhs)
    -> bool {
    return !scalar::kernel_compare_eq_mat4<T>(lhs.elements(), rhs.elements());
}

template <typename T, SFINAE_MAT4_GUARD<T> = nullptr>
auto operator<<(std::ostream& output_stream, const Matrix4<T>& src)
    -> std::ostream& {
    constexpr int PRECISION_DIGITS = 10;
    output_stream << std::setprecision(PRECISION_DIGITS);
    output_stream << "( " << src[0][0] << ", " << src[1][0] << ", " << src[2][0]
                  << ", " << src[3][0] << "\n";
    output_stream << "  " << src[0][1] << ", " << src[1][1] << ", " << src[2][1]
                  << ", " << src[3][1] << "\n";
    output_stream << "  " << src[0][2] << ", " << src[1][2] << ", " << src[2][2]
                  << ", " << src[3][2] << "\n";
    output_stream << "  " << src[0][3] << ", " << src[1][3] << ", " << src[2][3]
                  << ", " << src[3][3] << " )";
    return output_stream;
}

template <typename T, SFINAE_MAT4_GUARD<T> = nullptr>
auto operator>>(std::istream& input_stream, Matrix4<T>& dst) -> std::istream& {
    // Based on ignition-math implementation https://bit.ly/3MPgPcW
    input_stream.setf(std::ios_base::skipws);
    // Temporary place to store the inputs given by the user
    std::array<T, Matrix4<T>::BUFFER_SIZE> mat;
    // clang-format off
    // Get these many items/elements from the input stream
    input_stream >> mat[0]  >> mat[1]  >> mat[2]  >> mat[3]   // NOLINT
                 >> mat[4]  >> mat[5]  >> mat[6]  >> mat[7]   // NOLINT
                 >> mat[8]  >> mat[9]  >> mat[10] >> mat[11]  // NOLINT
                 >> mat[12] >> mat[13] >> mat[14] >> mat[15]; // NOLINT
    // clang-format on
    if (!input_stream.fail()) {
        // NOLINTNEXTLINE
        dst(0, 0) = mat[0];  // NOLINT
        dst(0, 1) = mat[1];  // NOLINT
        dst(0, 2) = mat[2];  // NOLINT
        dst(0, 3) = mat[3];  // NOLINT

        dst(1, 0) = mat[4];  // NOLINT
        dst(1, 1) = mat[5];  // NOLINT
        dst(1, 2) = mat[6];  // NOLINT
        dst(1, 3) = mat[7];  // NOLINT

        dst(2, 0) = mat[8];   // NOLINT
        dst(2, 1) = mat[9];   // NOLINT
        dst(2, 2) = mat[10];  // NOLINT
        dst(2, 3) = mat[11];  // NOLINT

        dst(3, 0) = mat[12];  // NOLINT
        dst(3, 1) = mat[13];  // NOLINT
        dst(3, 2) = mat[14];  // NOLINT
        dst(3, 3) = mat[15];  // NOLINT
    }
    return input_stream;
}

}  // namespace math
