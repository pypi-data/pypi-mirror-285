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
#include <math/vec3_t_decl.hpp>

namespace math {

template <typename T>
class Vector3;

}  // namespace math

namespace math {

/// \class Vector4
///
/// \brief Class representation of a vector in 4d-space
///
/// \tparam T Type of scalar value used for this 4d-vector (float|double)
///
/// This is a class that represents a 4d-vector with entries x, y, z, w of some
/// scalar floating-point type. Its storage is a buffer of the given scalar
/// type, and it's aligned accordingly in order to use the aligned versions of
/// some SIMD instructions (when using either SSE or AVX intrinsics).
template <typename T>
class Vector4 {
 public:
    /// Number of scalars used in the storage of the vector
    static constexpr uint32_t BUFFER_SIZE = 4;
    /// Number of scalar dimensions of the vector
    static constexpr uint32_t VECTOR_SIZE = 4;
    /// Number of dimensions of this vector (as in np.array.ndim)
    static constexpr uint32_t VECTOR_NDIM = 1;

    // Some handy type aliases used throught the codebase
    using Type = Vector4<T>;
    using ElementType = T;
    using BufferType = std::array<T, BUFFER_SIZE>;
    using Vec3 = Vector3<T>;

    /// Constructs a zero-initialized vector
    Vector4() = default;

    /// Constructs a vector of the form (x, x, x, x)
    explicit Vector4(T x_coord) {
        m_Elements[0] = x_coord;
        m_Elements[1] = x_coord;
        m_Elements[2] = x_coord;
        m_Elements[3] = x_coord;
    }

    /// Constructs a vector of the form (x, y, y, y)
    explicit Vector4(T x_coord, T y_coord) {
        m_Elements[0] = x_coord;
        m_Elements[1] = y_coord;
        m_Elements[2] = y_coord;
        m_Elements[3] = y_coord;
    }

    /// Constructs a vector of the form (x, y, z, z)
    explicit Vector4(T x_coord, T y_coord, T z_coord) {
        m_Elements[0] = x_coord;
        m_Elements[1] = y_coord;
        m_Elements[2] = z_coord;
        m_Elements[3] = z_coord;
    }

    /// Constructs a vector of the form (x, y, z, w)
    explicit Vector4(T x_coord, T y_coord, T z_coord, T w_coord) {
        m_Elements[0] = x_coord;
        m_Elements[1] = y_coord;
        m_Elements[2] = z_coord;
        m_Elements[3] = w_coord;
    }

    /// Constructs a vector of the form (x, y, z, 1.0)
    explicit Vector4(const Vec3& vec) {
        m_Elements[0] = vec.x();
        m_Elements[1] = vec.y();
        m_Elements[2] = vec.z();
        m_Elements[3] = 1.0F;
    }

    /// Constructs a vector from an initializer list of the form {x, y, z, w}
    Vector4(const std::initializer_list<T>& values) {
        // Complain in case we don't receive exactly 4 values
        assert(values.size() == Vector4<T>::VECTOR_SIZE);
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
    auto normalized() const -> Vector4<T>;

    /// Returns the dot product of this vector with the given vector
    auto dot(const Vector4<T>& rhs) const -> T;

    /// Returns a mutable reference to the x-component of the vector
    auto x() -> T& { return m_Elements[0]; }

    /// Returns a mutable reference to the y-component of the vector
    auto y() -> T& { return m_Elements[1]; }

    /// Returns a mutable reference to the z-component of the vector
    auto z() -> T& { return m_Elements[2]; }

    /// Returns a mutable reference to the w-component of the vector
    auto w() -> T& { return m_Elements[3]; }

    /// Returns an unmutable reference to the x-component of the vector
    auto x() const -> const T& { return m_Elements[0]; }

    /// Returns an unmutable reference to the y-component of the vector
    auto y() const -> const T& { return m_Elements[1]; }

    /// Returns an unmutable reference to the z-component of the vector
    auto z() const -> const T& { return m_Elements[2]; }

    /// Returns an unmutable reference to the w-component of the vector
    auto w() const -> const T& { return m_Elements[3]; }

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
            str_result << "Vector4f(" << x() << ", " << y() << ", " << z()
                       << ", " << w() << ")";
        } else if constexpr (std::is_same<ElementType, double>::value) {
            str_result << "Vector4d(" << x() << ", " << y() << ", " << z()
                       << ", " << w() << ")";
        } else {
            str_result << "Vector4X(" << x() << ", " << y() << ", " << z()
                       << ", " << w() << ")";
        }
        return str_result.str();
    }

 private:
    /// Storage of the vector's scalars
    BufferType m_Elements = {0, 0, 0, 0};
};

}  // namespace math
