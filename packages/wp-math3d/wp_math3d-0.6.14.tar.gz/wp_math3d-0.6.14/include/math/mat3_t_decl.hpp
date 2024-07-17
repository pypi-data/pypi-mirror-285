#pragma once

#include <array>
#include <cstdint>
#include <sstream>
#include <string>

#include <math/vec3_t_decl.hpp>
#include <math/mat4_t_decl.hpp>
#include <math/quat_t_decl.hpp>
#include <math/euler_t_decl.hpp>

namespace math {

template <typename T>
class Matrix4;

template <typename T>
class Quaternion;

template <typename T>
class Euler;

}  // namespace math

namespace math {

/// \class Matrix3
///
/// \brief Class representation of a 3 by 3 matrix of real-valued entries
///
/// \tparam T Type of scalar value used for the entries of the matrix
///
/// This is a class that represents 3x3 matrices with real-valued entries. The
/// internal data is stored as the columns of the matrix using 3d vectors of the
/// same scalar type, thus using a column major order.
template <typename T>
class Matrix3 {
 public:
    /// Number of scalars used for the storage of this matrix
    static constexpr uint32_t BUFFER_SIZE = 9;
    /// Number of dimensions of the matrix (square 3x3 matrix)
    static constexpr uint32_t MATRIX_SIZE = 3;
    /// Number of dimensions of this matrix (as in numpy.ndarray.ndim)
    static constexpr uint32_t MATRIX_NDIM = 2;

    /// Typename of the matrix
    using Type = Matrix3<T>;
    /// Typename of the scalar used for the matrix entries (float, double, etc.)
    using ElementType = T;
    /// Typename of the internal storage used by the matrix
    using BufferType = std::array<Vector3<T>, MATRIX_SIZE>;
    /// Typename of the columns of the matrix
    using ColumnType = Vector3<T>;

    // Some related types
    using Vec3 = Vector3<T>;
    using Mat4 = Matrix4<T>;
    using Quat = Quaternion<T>;

    /// Creates a zero-initialized matrix
    Matrix3() = default;

    // clang-format off
    /// Creates a matrix using the given scalars for its entries
    explicit Matrix3(T x00, T x01, T x02,
                     T x10, T x11, T x12,
                     T x20, T x21, T x22) {
        // First row
        m_Elements[0][0] = x00;
        m_Elements[1][0] = x01;
        m_Elements[2][0] = x02;

        // Second row
        m_Elements[0][1] = x10;
        m_Elements[1][1] = x11;
        m_Elements[2][1] = x12;

        // Third row
        m_Elements[0][2] = x20;
        m_Elements[1][2] = x21;
        m_Elements[2][2] = x22;
    }
    // clang-format on

    /// \brief Creates a diagonal matrix from some given diagonal entries
    explicit Matrix3(T x00, T x11, T x22) {
        m_Elements[0][0] = x00;
        m_Elements[1][1] = x11;
        m_Elements[2][2] = x22;
    }

    /// \brief Creates a 3x3 matrix from its columns in order
    explicit Matrix3(const ColumnType& col0, const ColumnType& col1,
                     const ColumnType& col2) {
        m_Elements[0] = col0;
        m_Elements[1] = col1;
        m_Elements[2] = col2;
    }

    /// \brief Creates a 3x3 rotation matrix from a given quaternion
    explicit Matrix3(const Quat& quaternion) { setFromQuaternion(quaternion); }

    /// \brief Creates a 3x3 rotation matrix from a given set of Euler angles
    explicit Matrix3(const Euler<T>& euler) { setFromEuler(euler); }

    /// \brief Creates a 3x3 rotation matrix from a given 4x4 transform matrix
    explicit Matrix3(const Mat4& transform) { setFromTransform(transform); }

    /// \brief Udpates this rotation matrix from a given quaternion
    auto setFromQuaternion(const Quat& quaternion) -> void;

    /// \brief Updates this rotation matrix from a given set of Euler angles
    auto setFromEuler(const Euler<T>& euler) -> void;

    /// \brief Updates this rotation matrix from a given 4x4 transform matrix
    auto setFromTransform(const Mat4& transform) -> void;

    /// Returns a mutable reference to the underlying storage of the matrix
    auto elements() -> BufferType& { return m_Elements; }

    /// Returns an unmutable reference to the underlying storage of the matrix
    auto elements() const -> const BufferType& { return m_Elements; }

    /// Returns a pointer to the data of the underlying storage in use
    auto data() -> T* { return m_Elements[0].data(); }

    /// Reeturns a const-pointer to the data of the underlying storage in use
    auto data() const -> const T* { return m_Elements[0].data(); }

    /// Gets a mutable reference to the column requested by the given index
    auto operator[](uint32_t col_index) -> ColumnType& {
        return m_Elements[col_index];
    }

    /// Gets an unmutable reference to the column requested by the given index
    auto operator[](uint32_t col_index) const -> const ColumnType& {
        return m_Elements[col_index];
    }

    /// Gets a mutable reference to the requested matrix entry
    auto operator()(uint32_t row_index, uint32_t col_index) -> T& {
        return m_Elements[col_index][row_index];
    }

    /// Gets an unmutable reference to the requested matrix entry
    auto operator()(uint32_t row_index, uint32_t col_index) const -> const T& {
        return m_Elements[col_index][row_index];
    }

    /// Multiplies this matrix by the given matrix
    /// \param[in] rhs The matrix to multiply this matrix by
    /// \returns The resulting matrix that combines both matrix operands
    LM_INLINE auto operator*(const Type& rhs) -> Type;

    /// Multiplies this matrix by the given vector
    /// \param[in] rhs The second operand of the matrix-vector multiplication
    /// \returns The resulting vector of the matrix multiplication
    LM_INLINE auto operator*(const Vec3& rhs) -> Vec3;

    /// Returns a comma-initializer to construct the matrix via its coefficients
    auto operator<<(T coeff) -> MatCommaInitializer<Type> {
        return MatCommaInitializer<Type>(*this, coeff);
    }

    /// Returns a printable string-representation of the matrix
    [[nodiscard]] auto toString() const -> std::string {
        const auto& data_elms = m_Elements;
        std::stringstream sstr_result;

        sstr_result << "( " << data_elms[0][0] << ", " << data_elms[1][0]
                    << ", " << data_elms[2][0] << ",\n";
        sstr_result << "  " << data_elms[0][1] << ", " << data_elms[1][1]
                    << ", " << data_elms[2][1] << ",\n";
        sstr_result << "  " << data_elms[0][2] << ", " << data_elms[1][2]
                    << ", " << data_elms[2][2] << ')';

        return sstr_result.str();
    }

    /// Creates a rotation matrix for the given angle around the X-axis
    static auto RotationX(T angle) -> Matrix3<T>;

    /// Creates a rotation matrix for the given angle around the Y-axis
    static auto RotationY(T angle) -> Matrix3<T>;

    /// Creates a rotation matrix for the given angle around the Z-axis
    static auto RotationZ(T angle) -> Matrix3<T>;

    /// Creates a scale matrix for the given separate scale arguments
    static auto Scale(T scale_x, T scale_y, T scale_z) -> Matrix3<T>;

    /// Creates a scale matrix for the given scale arguments given as a vec-3
    static auto Scale(const Vector3<T>& scale) -> Matrix3<T>;

    /// Creates an Identity matrix
    static auto Identity() -> Matrix3<T>;

    /// Creates a Zero matrix
    static auto Zeros() -> Matrix3<T>;

    /// Returns the number of rows
    static constexpr auto rows() -> uint32_t { return MATRIX_SIZE; }

    /// Returns the number of columns
    static constexpr auto cols() -> uint32_t { return MATRIX_SIZE; }

    /// Returns the number of elements in the matrix
    static constexpr auto size() -> uint32_t {
        return MATRIX_SIZE * MATRIX_SIZE;
    }

 private:
    /// The buffer where all data is stored
    BufferType m_Elements;
};

}  // namespace math
