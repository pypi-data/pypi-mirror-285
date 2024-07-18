#pragma once

#include <array>
#include <cstdint>
#include <sstream>
#include <string>

#include <math/vec2_t_decl.hpp>

namespace math {

/// \class Matrix2
///
/// \brief Class representation of a 2 by 2 matrix of real-valued entries
///
/// \tparam T Type of scalar value used for the entries of the matrix
///
/// This is a class that represents 2x2 matrices with real-valued entries. The
/// internal data is stored as the columns of the matrix using 2d vectors of the
/// same scalar type. The resulting storage is column major and aligned in a way
/// that allows the use of aligned versions of some SIMD instructions (when
/// using either SSE or AVX instrinsics).
template <typename T>
class Matrix2 {
 public:
    /// Number of scalars used for the storage of this matrix
    static constexpr uint32_t BUFFER_SIZE = 4;
    /// Number of dimensions of the matrix (square 2x2 matrix)
    static constexpr uint32_t MATRIX_SIZE = 2;
    /// Number of dimensions of this matrix (as in numpy.ndarray.ndim)
    static constexpr uint32_t MATRIX_NDIM = 2;

    /// Typename of the matrix
    using Type = Matrix2<T>;
    /// Typename of the scalar used for the matrix entries (float, double, etc.)
    using ElementType = T;
    /// Typename of the internal storage used by the matrix
    using BufferType = std::array<Vector2<T>, MATRIX_SIZE>;
    /// Typename of the columns of the matrix
    using ColumnType = Vector2<T>;

    /// Creates a zero-initialized matrix
    Matrix2() = default;

    /// Creates a matrix using the given scalars for its entries
    explicit Matrix2(T x00, T x01, T x10, T x11) {
        m_Elements[0][0] = x00;
        m_Elements[1][0] = x01;

        m_Elements[0][1] = x10;
        m_Elements[1][1] = x11;
    }

    explicit Matrix2(T x00, T x11) {
        m_Elements[0][0] = x00;
        m_Elements[1][1] = x11;
    }

    explicit Matrix2(const ColumnType& col0, const ColumnType& col1) {
        m_Elements[0] = col0;
        m_Elements[1] = col1;
    }

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
                    << '\n';
        sstr_result << "  " << data_elms[0][1] << ", " << data_elms[1][1]
                    << ')';

        return sstr_result.str();
    }

    /// Creates a rotation matrix for the given angle
    static auto Rotation(T angle) -> Matrix2<T>;

    /// Creates a scale matrix with the two given scale parameters
    /// \param[in] scale_x The value for the scale in the x component
    /// \param[in] scale_y The value for the scale in the y component
    static auto Scale(T scale_x, T scale_y) -> Matrix2<T>;

    /// Creates a scale matrix given scale parameters as a vec-2
    /// \param[in] scale A vec2 with both values for the scales
    static auto Scale(const Vector2<T>& scale) -> Matrix2<T>;

    /// Returns a 4x4 identity matrix of the current scalar type
    static auto Identity() -> Matrix2<T>;

    /// Returns a 4x4 zero matrix of the current scalar type
    static auto Zeros() -> Matrix2<T>;

    /// Returns the number of rows
    static constexpr auto rows() -> uint32_t { return MATRIX_SIZE; }

    /// Returns the number of columns
    static constexpr auto cols() -> uint32_t { return MATRIX_SIZE; }

    /// Returns the number of elements in the matrix
    static constexpr auto size() -> uint32_t {
        return MATRIX_SIZE * MATRIX_SIZE;
    }

 private:
    /// The buffer where all data is stored (as an array of 2 column
    /// vectors)
    BufferType m_Elements;
};

}  // namespace math
