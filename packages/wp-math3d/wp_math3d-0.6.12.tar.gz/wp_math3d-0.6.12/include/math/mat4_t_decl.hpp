#pragma once

#include <array>
#include <cstdint>
#include <sstream>
#include <string>

#include <math/vec3_t_decl.hpp>
#include <math/vec4_t_decl.hpp>
#include <math/mat3_t_decl.hpp>
#include <math/euler_t_decl.hpp>
#include <math/quat_t_decl.hpp>

namespace math {

template <typename T>
class Matrix3;

template <typename T>
class Euler;

template <typename T>
class Quaternion;

}  // namespace math

namespace math {

/// \class Matrix4
///
/// \brief Class representation of a 4 by 4 matrix of real-valued entries
///
/// \tparam T Type of scalar value used for the entries of the matrix
///
/// This is a class that represents 4x4 matrices with real-valued entries. The
/// internal data is stored as the columns of the matrix using 4d vectors of the
/// same scalar type. The resulting storage is column major and aligned in a way
/// that allows the use of aligned versions of some SIMD instructions (when
/// using either SSE or AVX instrinsics).
template <typename T>
class Matrix4 {
 public:
    /// Number of scalars used in the storage of the matrix
    constexpr static uint32_t BUFFER_SIZE = 16;
    /// Number of dimensions of the matrix (square 4x4 matrix)
    constexpr static uint32_t MATRIX_SIZE = 4;
    /// Number of dimensions of this matrix (as in numpy.ndarray.ndim)
    static constexpr uint32_t MATRIX_NDIM = 2;

    /// Typename of the matrix
    using Type = Matrix4<T>;
    /// Typename of the scalar used for the matrix entries (float, double, etc.)
    using ElementType = T;
    /// Typename of the internal storage used by the matrix
    using BufferType = std::array<Vector4<T>, MATRIX_SIZE>;
    /// Typename of the columns of the matrix
    using ColumnType = Vector4<T>;

    // Some related types
    using Vec3 = Vector3<T>;
    using Vec4 = Vector4<T>;
    using Mat3 = Matrix3<T>;
    using Quat = Quaternion<T>;

    /// Creates a zero-initialized matrix
    Matrix4() = default;

    /// Creates a matrix using the given scalars for its entries
    explicit Matrix4(T x00, T x01, T x02, T x03, T x10, T x11, T x12, T x13,
                     T x20, T x21, T x22, T x23, T x30, T x31, T x32, T x33) {
        // Row-0
        m_Elements[0][0] = x00;
        m_Elements[1][0] = x01;
        m_Elements[2][0] = x02;
        m_Elements[3][0] = x03;

        // Row-1
        m_Elements[0][1] = x10;
        m_Elements[1][1] = x11;
        m_Elements[2][1] = x12;
        m_Elements[3][1] = x13;

        // Row-2
        m_Elements[0][2] = x20;
        m_Elements[1][2] = x21;
        m_Elements[2][2] = x22;
        m_Elements[3][2] = x23;

        // Row-3
        m_Elements[0][3] = x30;
        m_Elements[1][3] = x31;
        m_Elements[2][3] = x32;
        m_Elements[3][3] = x33;
    }

    /// Creates a diagonal matrix using the given diagonal elements
    explicit Matrix4(T x00, T x11, T x22, T x33) {
        m_Elements[0][0] = x00;
        m_Elements[1][1] = x11;
        m_Elements[2][2] = x22;
        m_Elements[3][3] = x33;
    }

    /// Creates a matrix using the given columns
    explicit Matrix4(const ColumnType& col0, const ColumnType& col1,
                     const ColumnType& col2, const ColumnType& col3) {
        m_Elements[0] = col0;
        m_Elements[1] = col1;
        m_Elements[2] = col2;
        m_Elements[3] = col3;
    }

    /// Constructs a transform matrix given its world position and orientation
    /// \param[in] position The position part of the transform in world space
    /// \param[in] rotmat A 3x3 rotation matrix representing orientation
    explicit Matrix4(const Vec3& position, const Mat3& rotmat) {
        setPosition(position);
        setRotation(rotmat);
    }

    /// Constructs a transform matrix given its world position and orientation
    /// \param[in] position The position part of the transform in world space
    /// \param[in] quat A quaternion representing the orientation in world space
    explicit Matrix4(const Vec3& position, const Quat& quat) {
        setPosition(position);
        setRotation(quat);
    }

    /// Constructs a transform matrix given its world position and orientation
    /// \param[in] position The position part of the transform in world space
    /// \param[in] euler A set of euler angles representing orientation
    explicit Matrix4(const Vec3& position, const Euler<T>& euler) {
        setPosition(position);
        setRotation(euler);
    }

    /// Sets the position part of this transform
    auto setPosition(const Vec3& position) -> void;

    /// Sets the rotation part of this transform from a given quaternion
    auto setRotation(const Quat& quat) -> void;

    /// Sets the rotation part of this transform from given euler angles
    auto setRotation(const Euler<T>& euler) -> void;

    /// Sets the rotation part of this transform from a 3x3 rotation matrix
    auto setRotation(const Mat3& mat) -> void;

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

    /// Returns a comma-initializer to construct the matrix via its coefficients
    auto operator<<(T coeff) -> MatCommaInitializer<Type> {
        return MatCommaInitializer<Type>(*this, coeff);
    }

    /// Returns a printable string-representation of the matrix
    [[nodiscard]] auto toString() const -> std::string {
        const auto& data_elms = m_Elements;
        std::stringstream sstr_result;

        sstr_result << "( " << data_elms[0][0] << ", " << data_elms[1][0]
                    << ", " << data_elms[2][0] << ", " << data_elms[3][0]
                    << "\n";
        sstr_result << "  " << data_elms[0][1] << ", " << data_elms[1][1]
                    << ", " << data_elms[2][1] << ", " << data_elms[3][1]
                    << "\n";
        sstr_result << "  " << data_elms[0][2] << ", " << data_elms[1][2]
                    << ", " << data_elms[2][2] << ", " << data_elms[3][2]
                    << "\n";
        sstr_result << "  " << data_elms[0][3] << ", " << data_elms[1][3]
                    << ", " << data_elms[2][3] << ", " << data_elms[3][3]
                    << " )";

        return sstr_result.str();
    }

    /// Creates a rotation matrix for the given angle around the X-axis
    static auto RotationX(T angle) -> Matrix4<T>;

    /// Creates a rotation matrix for the given angle around the Y-axis
    static auto RotationY(T angle) -> Matrix4<T>;

    /// Creates a rotation matrix for the given angle around the Z-axis
    static auto RotationZ(T angle) -> Matrix4<T>;

    /// Creates a scale matrix for the given separate scale arguments
    static auto Scale(T scale_x, T scale_y, T scale_z) -> Matrix4<T>;

    /// Creates a scale matrix for the given scale arguments given as a vec3
    static auto Scale(const Vector3<T>& scale) -> Matrix4<T>;

    /// Creates a translation matrix from the given translation given as a vec3
    static auto Translation(const Vector3<T>& position) -> Matrix4<T>;

    /// Creates a perspective projection matrix from the given configuration
    static auto Perspective(T fov, T aspect, T near, T far) -> Matrix4<T>;

    /// Creates a perspective projection matrix from the frustum sizes
    static auto Perspective(T left, T right, T top, T bottom, T near, T far)
        -> Matrix4<T>;

    /// Creates a orthographic projection matrix from the given configuration
    static auto Ortho(T width, T height, T near, T far) -> Matrix4<T>;

    /// Returns a 4x4 identity matrix of the current scalar type
    static auto Identity() -> Matrix4<T>;

    /// Returns a 4x4 zero matrix of the current scalar type
    static auto Zeros() -> Matrix4<T>;

    /// Returns the number of rows
    static constexpr auto rows() -> uint32_t { return MATRIX_SIZE; }

    /// Returns the number of columns
    static constexpr auto cols() -> uint32_t { return MATRIX_SIZE; }

    /// Returns the number of elements in the matrix
    static constexpr auto size() -> uint32_t {
        return MATRIX_SIZE * MATRIX_SIZE;
    }

 private:
    /// The buffer where all data lies (as an array of 4 column vectors)
    BufferType m_Elements;
};

}  // namespace math
