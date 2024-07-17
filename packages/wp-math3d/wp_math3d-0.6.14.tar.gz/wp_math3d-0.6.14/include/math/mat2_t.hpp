#pragma once

#include <cmath>
#include <iomanip>

#include <math/mat2_t_decl.hpp>

#include <math/impl/mat2_t_scalar_impl.hpp>
#include <math/impl/mat2_t_sse_impl.hpp>
#include <math/impl/mat2_t_avx_impl.hpp>

namespace math {

// ***************************************************************************//
//                       Factory functions implementation                     //
// ***************************************************************************//

template <typename T>
auto Matrix2<T>::Rotation(T angle) -> Matrix2<T> {
    auto cos_t = std::cos(angle);
    auto sin_t = std::sin(angle);
    // clang-format off
    return Matrix2<T>(
        cos_t, -sin_t,
        sin_t,  cos_t);
    // clang-format on
}

template <typename T>
auto Matrix2<T>::Scale(T scale_x, T scale_y) -> Matrix2<T> {
    // clang-format off
    return Matrix2<T>(
        scale_x, 0.0,
        0.0, scale_y);
    // clang-format on
}

template <typename T>
auto Matrix2<T>::Scale(const Vector2<T>& scale) -> Matrix2<T> {
    // clang-format off
    return Matrix2<T>(
        scale.x(), 0.0,
        0.0, scale.y());
    // clang-format on
}

template <typename T>
auto Matrix2<T>::Identity() -> Matrix2<T> {
    // clang-format off
    return Matrix2<T>(
        1.0, 0.0,
        0.0, 1.0);
    // clang-format on
}

template <typename T>
auto Matrix2<T>::Zeros() -> Matrix2<T> {
    return Matrix2<T>();
}

// ***************************************************************************//
//                       Matrix Methods implementation                        //
// ***************************************************************************//

template <typename T>
using SFINAE_MAT2_GUARD = typename std::enable_if<IsScalar<T>::value>::type*;

/// Returns the tranpose of the given matrix
template <typename T, SFINAE_MAT2_GUARD<T> = nullptr>
LM_INLINE auto transpose(const Matrix2<T>& mat) -> Matrix2<T> {
    Matrix2<T> dst = mat;
    scalar::kernel_transpose_inplace_mat2<T>(dst.elements());
    return dst;
}

/// Transposes the given matrix in place
template <typename T, SFINAE_MAT2_GUARD<T> = nullptr>
LM_INLINE auto transposeInPlace(Matrix2<T>& mat) -> void {  // NOLINT
    scalar::kernel_transpose_inplace_mat2<T>(mat.elements());
}

/// Returns the trace (sum of diagonal elements) of the matrix
template <typename T, SFINAE_MAT2_GUARD<T> = nullptr>
LM_INLINE auto trace(const Matrix2<T>& mat) -> T {
    return scalar::kernel_trace_mat2<T>(mat.elements());
}

/// Returns the determinant of the matrix
template <typename T, SFINAE_MAT2_GUARD<T> = nullptr>
LM_INLINE auto determinant(const Matrix2<T>& mat) -> T {
    return scalar::kernel_determinant_mat2<T>(mat.elements());
}

/// Returns the inverse of the matrix
template <typename T, SFINAE_MAT2_GUARD<T> = nullptr>
LM_INLINE auto inverse(const Matrix2<T>& mat) -> Matrix2<T> {
    Matrix2<T> dst;
    scalar::kernel_inverse_mat2<T>(dst.elements(), mat.elements());
    return dst;
}

// ***************************************************************************//
//                     Matrix Operators implementation                        //
// ***************************************************************************//

/// Returns the matrix sum of the two given matrices
template <typename T, SFINAE_MAT2_GUARD<T> = nullptr>
LM_INLINE auto operator+(const Matrix2<T>& lhs, const Matrix2<T>& rhs)
    -> Matrix2<T> {
    Matrix2<T> dst;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_add_mat2<T>(dst.elements(), lhs.elements(), rhs.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_add_mat2<T>(dst.elements(), lhs.elements(), rhs.elements());
#else
    scalar::kernel_add_mat2<T>(dst.elements(), lhs.elements(), rhs.elements());
#endif
    return dst;
}

template <typename T, SFINAE_MAT2_GUARD<T> = nullptr>
LM_INLINE auto operator-(const Matrix2<T>& lhs, const Matrix2<T>& rhs)
    -> Matrix2<T> {
    Matrix2<T> dst;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_sub_mat2<T>(dst.elements(), lhs.elements(), rhs.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_sub_mat2<T>(dst.elements(), lhs.elements(), rhs.elements());
#else
    scalar::kernel_sub_mat2<T>(dst.elements(), lhs.elements(), rhs.elements());
#endif
    return dst;
}

template <typename T, SFINAE_MAT2_GUARD<T> = nullptr>
LM_INLINE auto operator*(double scale, const Matrix2<T>& mat) -> Matrix2<T> {
    Matrix2<T> dst;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_scale_mat2<T>(dst.elements(), static_cast<T>(scale),
                              mat.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_scale_mat2<T>(dst.elements(), static_cast<T>(scale),
                              mat.elements());
#else
    scalar::kernel_scale_mat2<T>(dst.elements(), static_cast<T>(scale),
                                 mat.elements());
#endif
    return dst;
}

template <typename T, SFINAE_MAT2_GUARD<T> = nullptr>
LM_INLINE auto operator*(const Matrix2<T>& mat, double scale) -> Matrix2<T> {
    Matrix2<T> dst;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_scale_mat2<T>(dst.elements(), static_cast<T>(scale),
                              mat.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_scale_mat2<T>(dst.elements(), static_cast<T>(scale),
                              mat.elements());
#else
    scalar::kernel_scale_mat2<T>(dst.elements(), static_cast<T>(scale),
                                 mat.elements());
#endif
    return dst;
}

template <typename T, SFINAE_MAT2_GUARD<T> = nullptr>
LM_INLINE auto operator*(const Matrix2<T>& lhs, const Matrix2<T>& rhs)
    -> Matrix2<T> {
    Matrix2<T> dst;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_matmul_mat2<T>(dst.elements(), lhs.elements(), rhs.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_matmul_mat2<T>(dst.elements(), lhs.elements(), rhs.elements());
#else
    scalar::kernel_matmul_mat2<T>(dst.elements(), lhs.elements(),
                                  rhs.elements());
#endif
    return dst;
}

template <typename T, SFINAE_MAT2_GUARD<T> = nullptr>
LM_INLINE auto operator*(const Matrix2<T>& lhs_mat, const Vector2<T>& rhs_vec)
    -> Vector2<T> {
    Vector2<T> dst;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_matmul_vec_mat2<T>(dst.elements(), lhs_mat.elements(),
                                   rhs_vec.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_matmul_vec_mat2<T>(dst.elements(), lhs_mat.elements(),
                                   rhs_vec.elements());
#else
    scalar::kernel_matmul_vec_mat2<T>(dst.elements(), lhs_mat.elements(),
                                      rhs_vec.elements());
#endif
    return dst;
}

template <typename T, SFINAE_MAT2_GUARD<T> = nullptr>
LM_INLINE auto hadamard(const Matrix2<T>& lhs, const Matrix2<T>& rhs)
    -> Matrix2<T> {
    Matrix2<T> dst;
#if defined(MATH_AVX_ENABLED)
    avx::kernel_hadamard_mat2<T>(dst.elements(), lhs.elements(),
                                 rhs.elements());
#elif defined(MATH_SSE_ENABLED)
    sse::kernel_hadamard_mat2<T>(dst.elements(), lhs.elements(),
                                 rhs.elements());
#else
    scalar::kernel_hadamard_mat2<T>(dst.elements(), lhs.elements(),
                                    rhs.elements());
#endif
    return dst;
}

template <typename T, SFINAE_MAT2_GUARD<T> = nullptr>
LM_INLINE auto operator==(const Matrix2<T>& lhs, const Matrix2<T>& rhs)
    -> bool {
    return scalar::kernel_compare_eq_mat2<T>(lhs.elements(), rhs.elements());
}

template <typename T, SFINAE_MAT2_GUARD<T> = nullptr>
LM_INLINE auto operator!=(const Matrix2<T>& lhs, const Matrix2<T>& rhs)
    -> bool {
    return !scalar::kernel_compare_eq_mat2<T>(lhs.elements(), rhs.elements());
}

template <typename T, SFINAE_MAT2_GUARD<T> = nullptr>
auto operator<<(std::ostream& output_stream, const Matrix2<T>& src)
    -> std::ostream& {
    constexpr int PRECISION_DIGITS = 10;
    output_stream << std::setprecision(PRECISION_DIGITS);
    output_stream << "( " << src[0][0] << ", " << src[1][0] << '\n';
    output_stream << "  " << src[0][1] << ", " << src[1][1] << " )";
    return output_stream;
}

template <typename T, SFINAE_MAT2_GUARD<T> = nullptr>
auto operator>>(std::istream& input_stream, Matrix2<T>& dst) -> std::istream& {
    // Based on ignition-math implementation https://bit.ly/3MPgPcW
    input_stream.setf(std::ios_base::skipws);
    // Temporary place to store the inputs given by the user
    std::array<T, Matrix2<T>::BUFFER_SIZE> mat;
    // Get these many items/elements from the input stream
    input_stream >> mat[0] >> mat[1] >> mat[2] >> mat[3];
    if (!input_stream.fail()) {
        dst(0, 0) = mat[0];
        dst(0, 1) = mat[1];
        dst(1, 0) = mat[2];
        dst(1, 1) = mat[3];
    }
    return input_stream;
}

}  // namespace math
