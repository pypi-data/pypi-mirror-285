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
#include <math/vec4_t_decl.hpp>

namespace math {

template <typename T>
class Vector4;

}  // namespace math

namespace math {

/// \class Vector3
///
/// \brief Class representation of a vector in 3d-space
///
/// \tparam T Type of scalar value used for this 3d-vector (float|double)
///
/// This is a class that represents a 3d-vector with entries x, y, z of some
/// scalar floating-point type. Its storage is a buffer of the given scalar
/// type, and contains only the required storage for 3 elements.
template <typename T>
class Vector3 {
 public:
    /// Number of scalars used in the storage of the vector
    static constexpr uint32_t BUFFER_SIZE = 3;
    /// Number of scalar dimensions of the vector
    static constexpr uint32_t VECTOR_SIZE = 3;
    /// Number of dimensions of this vector (as in np.array.ndim)
    static constexpr uint32_t VECTOR_NDIM = 1;

    // Some handy type aliases used throught the codebase
    using Type = Vector3<T>;
    using ElementType = T;
    using BufferType = std::array<T, BUFFER_SIZE>;

    // Some related types
    using Vec4 = Vector4<T>;

    /// Constructs a zero-initialized vector
    Vector3() = default;

    /// Constructs a vector of the form (x, x, x)
    explicit Vector3(T x_coord) {
        m_Elements[0] = x_coord;
        m_Elements[1] = x_coord;
        m_Elements[2] = x_coord;
    }

    /// Constructs a vector of the form (x, y, y)
    explicit Vector3(T x_coord, T y_coord) {
        m_Elements[0] = x_coord;
        m_Elements[1] = y_coord;
        m_Elements[2] = y_coord;
    }

    /// Constructs a vector of the form (x, y, z)
    explicit Vector3(T x_coord, T y_coord, T z_coord) {
        m_Elements[0] = x_coord;
        m_Elements[1] = y_coord;
        m_Elements[2] = z_coord;
    }

    /// Constructs a vector from the vec3 part of a given vec4
    explicit Vector3(const Vec4& vec) {
        m_Elements[0] = vec.x();
        m_Elements[1] = vec.y();
        m_Elements[2] = vec.z();
    }

    /// COnstructs a vector from an initializer list of the form {x, y, z}
    Vector3(const std::initializer_list<T>& values) {
        // Complain in case we don't receive exactly 3 values
        assert(values.size() == Vector3<T>::VECTOR_SIZE);
        // Just copy the whole data from the initializer list
        std::copy(values.begin(), values.end(), m_Elements.data());
    }

    /// Returns the square of the length of this vector
    auto lengthSquare() const -> T;

    /// Returns the length of this vector
    auto length() const -> T;

    /// Normalizes this vector in place
    auto normalize() -> void;

    /// Returns the normalized version of this vector
    auto normalized() const -> Vector3<T>;

    /// Returns the dot product of this vector with the given vector
    auto dot(const Vector3<T>& rhs) const -> T;

    /// Returns the cross product of this vector with the given vector
    auto cross(const Vector3<T>& rhs) const -> Vector3<T>;

    /// Returns a mutable reference to the x-component of the vector
    auto x() -> T& { return m_Elements[0]; }

    /// Returns a mutable reference to the y-component of the vector
    auto y() -> T& { return m_Elements[1]; }

    /// Returns a mutable reference to the z-component of the vector
    auto z() -> T& { return m_Elements[2]; }

    /// Returns an unmutable reference to the x-component of the vector
    auto x() const -> const T& { return m_Elements[0]; }

    /// Returns an unmutable reference to the y-component of the vector
    auto y() const -> const T& { return m_Elements[1]; }

    /// Returns an unmutable reference to the z-component of the vector
    auto z() const -> const T& { return m_Elements[2]; }

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
            str_result << "Vector3f(" << x() << ", " << y() << ", " << z()
                       << ")";
        } else if constexpr (std::is_same<ElementType, double>::value) {
            str_result << "Vector3d(" << x() << ", " << y() << ", " << z()
                       << ")";
        } else {
            str_result << "Vector3X(" << x() << ", " << y() << ", " << z()
                       << ")";
        }
        return str_result.str();
    }

 private:
    /// Storage of the vector's scalars
    BufferType m_Elements = {0, 0, 0};
};

}  // namespace math
