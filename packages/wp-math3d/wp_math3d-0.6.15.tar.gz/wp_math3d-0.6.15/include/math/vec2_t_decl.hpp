#pragma once

#include <array>
#include <cassert>
#include <cstdint>
#include <initializer_list>
#include <sstream>
#include <string>
#include <algorithm>
#include <type_traits>

#include <math/common.hpp>

namespace math {

/// \class Vector2
///
/// \brief Class representation of a vector in 2d-space
///
/// \tparam T Type of scalar value used for this 2d-vector (float|double)
///
/// This is a class that represents a 2d-vector with entries x, y of some
/// scalar floating-point type. Its storage is a buffer of the given scalar
/// type; however, it's not aligned for SIMD load/store instructions (tradeoff
/// between adding padding/size and usage of aligned load/store). So, SIMD
/// kernels are build using unaligned load/store operations (unlike friends like
/// vec3 and vec4 types)
template <typename T>
struct Vector2 {
    /// Number of scalars used in the storage of the vector
    static constexpr uint32_t BUFFER_SIZE = 2;
    /// Number of scalars contained by the vector
    static constexpr uint32_t VECTOR_SIZE = 2;
    /// Number of dimensions of this vector (as in numpy.ndarray.ndim)
    static constexpr uint32_t VECTOR_NDIM = 1;

    // Some handy type aliases used throught the codebase
    using Type = Vector2<T>;
    using ElementType = T;
    using BufferType = std::array<T, BUFFER_SIZE>;

    /// Constructs a zero-initialized vector
    Vector2() = default;

    /// Constructs a vector of the form (x, x)
    explicit Vector2(T x_coord) {
        m_Elements[0] = x_coord;
        m_Elements[1] = x_coord;
    }

    /// Constructs a vector of the form (x, y)
    explicit Vector2(T x_coord, T y_coord) {
        m_Elements[0] = x_coord;
        m_Elements[1] = y_coord;
    }

    /// Constructs a vector from an initializer list of the form {x, y}
    Vector2(const std::initializer_list<T>& values) {
        assert(values.size() == Vector2<T>::VECTOR_SIZE);
        std::copy(values.begin(), values.end(), m_Elements.data());
    }

    /// Returns the square of the length of this vector
    auto lengthSquare() const -> T;

    /// Returns the length of this vector
    auto length() const -> T;

    /// Normalizes this vector in place
    auto normalize() -> void;

    /// Returns the normalized version of this vector
    auto normalized() const -> Vector2<T>;

    /// Returns the dot product of this vector with the given vector
    auto dot(const Vector2<T>& rhs) const -> T;

    /// Returns a mutable reference to the x-component of the vector
    auto x() -> T& { return m_Elements[0]; }

    /// Returns a mutable reference to the y-component of the vector
    auto y() -> T& { return m_Elements[1]; }

    /// Returns an unmutable reference to the x-component of the vector
    auto x() const -> const T& { return m_Elements[0]; }

    /// Returns an unmutable reference to the y-component of the vector
    auto y() const -> const T& { return m_Elements[1]; }

    /// Returns a mutable reference to the underlying storage of the vector
    auto elements() -> BufferType& { return m_Elements; }

    /// Returns an unmutable reference to the underlying storage of the vector
    auto elements() const -> const BufferType& { return m_Elements; }

    /// Returns a pointer to the data of the underlying storage in use
    auto data() -> T* { return m_Elements.data(); }

    /// Reeturns a const-pointer to the data of the underlying storage in use
    auto data() const -> const T* { return m_Elements.data(); }

    /// Returns a mutable reference to the requested entry of the vector
    auto operator[](uint32_t index) -> T& { return m_Elements[index]; }

    /// Returns an unmutable reference to the requested entry of the vector
    auto operator[](uint32_t index) const -> const T& {
        return m_Elements[index];
    }

    /// Returns a comma-initializer to construct the vector via its coefficients
    auto operator<<(T coeff) -> VecCommaInitializer<Type> {
        return VecCommaInitializer<Type>(*this, coeff);
    }

    /// Returns a printable string-representation of the vector
    [[nodiscard]] auto toString() const -> std::string {
        std::stringstream str_result;
        if constexpr (std::is_same<ElementType, float>::value) {
            str_result << "Vector2f(" << x() << ", " << y() << ")";
        } else if constexpr (std::is_same<ElementType, double>::value) {
            str_result << "Vector2d(" << x() << ", " << y() << ")";
        } else {
            str_result << "Vector2X(" << x() << ", " << y() << ")";
        }
        return str_result.str();
    }

 private:
    /// Storage of the vector's scalars
    BufferType m_Elements = {0, 0};
};

}  // namespace math
