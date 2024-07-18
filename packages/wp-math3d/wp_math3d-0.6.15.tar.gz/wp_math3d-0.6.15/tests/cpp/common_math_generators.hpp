#include <catch2/catch.hpp>
#include <math/vec2_t.hpp>
#include <math/vec3_t.hpp>
#include <math/vec4_t.hpp>
#include <math/mat2_t.hpp>
#include <math/mat3_t.hpp>
#include <math/mat4_t.hpp>
#include <math/quat_t.hpp>

#include <random>

namespace math {

template <typename T>
using Vec2 = ::math::Vector2<T>;

template <typename T>
using Vec3 = ::math::Vector3<T>;

template <typename T>
using Vec4 = ::math::Vector4<T>;

template <typename T>
using Mat2 = ::math::Matrix2<T>;

template <typename T>
using Mat3 = ::math::Matrix3<T>;

template <typename T>
using Mat4 = ::math::Matrix4<T>;

template <typename T>
using Quat = ::math::Quaternion<T>;

template <typename T, typename V>
class RandomValueBase : public Catch::Generators::IGenerator<V> {
 public:
    RandomValueBase(T val_range_min, T val_range_max)
        : m_Dist(val_range_min, val_range_max),  // NOLINT
          m_Gen(std::random_device{}()) {}       // NOLINT

    auto get() const -> const V& override { return m_Value; }

 protected:
    /// Distribution from which to generate random real values
    std::uniform_real_distribution<T> m_Dist;
    /// The method used to generate random numbers
    std::minstd_rand m_Gen;
    /// The random value to be exposed
    V m_Value;
};

//****************************************************************************//
//                        Generators for Vector types                         //
//****************************************************************************//

//-------------------//
// Custom Generators //
//-------------------//

template <typename T>
class RandomVec2Generator : public Catch::Generators::IGenerator<Vec2<T>> {
 public:
    RandomVec2Generator(T range_min, T range_max)
        // NOLINTNEXTLINE
        : m_Gen(std::random_device{}()), m_Dist(range_min, range_max) {
        static_cast<void>(next());
    }

    auto get() const -> const Vec2<T>& override { return m_Value; }

    auto next() -> bool override {
        m_Value.x() = m_Dist(m_Gen);
        m_Value.y() = m_Dist(m_Gen);
        return true;
    }

 private:
    /// The method used to generate random numbers
    std::minstd_rand m_Gen;
    /// Distribution from which to generate random real values
    std::uniform_real_distribution<T> m_Dist;
    /// The random value to be exposed
    Vec2<T> m_Value;
};

template <typename T>
class RandomVec3Generator : public Catch::Generators::IGenerator<Vec3<T>> {
 public:
    RandomVec3Generator(T range_min, T range_max)
        // NOLINTNEXTLINE
        : m_Gen(std::random_device{}()), m_Dist(range_min, range_max) {
        static_cast<void>(next());
    }

    auto get() const -> const Vec3<T>& override { return m_Value; }

    auto next() -> bool override {
        m_Value.x() = m_Dist(m_Gen);
        m_Value.y() = m_Dist(m_Gen);
        m_Value.z() = m_Dist(m_Gen);
        return true;
    }

 private:
    /// The method used to generate random numbers
    std::minstd_rand m_Gen;
    /// Distribution from which to generate random real values
    std::uniform_real_distribution<T> m_Dist;
    /// The random value to be exposed
    Vec3<T> m_Value;
};

template <typename T>
class RandomVec4Generator : public Catch::Generators::IGenerator<Vec4<T>> {
 public:
    RandomVec4Generator(T range_min, T range_max)
        // NOLINTNEXTLINE
        : m_Gen(std::random_device{}()), m_Dist(range_min, range_max) {
        static_cast<void>(next());
    }

    auto get() const -> const Vec4<T>& override { return m_Value; }

    auto next() -> bool override {
        m_Value.x() = m_Dist(m_Gen);
        m_Value.y() = m_Dist(m_Gen);
        m_Value.z() = m_Dist(m_Gen);
        m_Value.w() = m_Dist(m_Gen);
        return true;
    }

 private:
    /// The method used to generate random numbers
    std::minstd_rand m_Gen;
    /// Distribution from which to generate random real values
    std::uniform_real_distribution<T> m_Dist;
    /// The random value to be exposed
    Vec4<T> m_Value;
};

//--------------------//
// Generator wrappers //
//--------------------//

template <typename T>
auto random_vec2(T val_range_min = static_cast<T>(-1.0),
                 T val_range_max = static_cast<T>(1.0))
    -> Catch::Generators::GeneratorWrapper<Vector2<T>> {
    return Catch::Generators::GeneratorWrapper<Vector2<T>>(
        Catch::Generators::pf::make_unique<RandomVec2Generator<T>>(
            val_range_min, val_range_max));
}

template <typename T>
auto random_vec3(T val_range_min = static_cast<T>(-1.0),
                 T val_range_max = static_cast<T>(1.0))
    -> Catch::Generators::GeneratorWrapper<Vector3<T>> {
    return Catch::Generators::GeneratorWrapper<Vector3<T>>(
        Catch::Generators::pf::make_unique<RandomVec3Generator<T>>(
            val_range_min, val_range_max));
}

template <typename T>
auto random_vec4(T val_range_min = static_cast<T>(-1.0),
                 T val_range_max = static_cast<T>(1.0))
    -> Catch::Generators::GeneratorWrapper<Vector4<T>> {
    return Catch::Generators::GeneratorWrapper<Vector4<T>>(
        Catch::Generators::pf::make_unique<RandomVec4Generator<T>>(
            val_range_min, val_range_max));
}

//****************************************************************************//
//                        Generators for Matrix types                         //
//****************************************************************************//

//-------------------//
// Custom Generators //
//-------------------//

template <typename T>
class RandomMatrix2Generator : public Catch::Generators::IGenerator<Mat2<T>> {
 public:
    RandomMatrix2Generator(T range_min, T range_max)
        // NOLINTNEXTLINE
        : m_Gen(std::random_device{}()), m_Dist(range_min, range_max) {
        static_cast<void>(next());
    }

    auto get() const -> const Mat2<T>& override { return m_Value; }

    auto next() -> bool override {
        // Generate first column
        m_Value(0, 0) = m_Dist(m_Gen);
        m_Value(1, 0) = m_Dist(m_Gen);
        // Generate second column
        m_Value(0, 1) = m_Dist(m_Gen);
        m_Value(1, 1) = m_Dist(m_Gen);
        return true;
    }

 private:
    /// The method used to generate random numbers
    std::minstd_rand m_Gen;
    /// Distribution from which to generate random real values
    std::uniform_real_distribution<T> m_Dist;
    /// The random value to be exposed
    Mat2<T> m_Value;
};

template <typename T>
class RandomMatrix3Generator : public Catch::Generators::IGenerator<Mat3<T>> {
 public:
    RandomMatrix3Generator(T range_min, T range_max)
        // NOLINTNEXTLINE
        : m_Gen(std::random_device{}()), m_Dist(range_min, range_max) {
        static_cast<void>(next());
    }

    auto get() const -> const Mat3<T>& override { return m_Value; }

    auto next() -> bool override {
        // Generate first column
        m_Value(0, 0) = m_Dist(m_Gen);
        m_Value(1, 0) = m_Dist(m_Gen);
        m_Value(2, 0) = m_Dist(m_Gen);
        // Generate second column
        m_Value(0, 1) = m_Dist(m_Gen);
        m_Value(1, 1) = m_Dist(m_Gen);
        m_Value(2, 1) = m_Dist(m_Gen);
        // Generate third column
        m_Value(0, 2) = m_Dist(m_Gen);
        m_Value(1, 2) = m_Dist(m_Gen);
        m_Value(2, 2) = m_Dist(m_Gen);
        return true;
    }

 private:
    /// The method used to generate random numbers
    std::minstd_rand m_Gen;
    /// Distribution from which to generate random real values
    std::uniform_real_distribution<T> m_Dist;
    /// The random value to be exposed
    Mat3<T> m_Value;
};

template <typename T>
class RandomMatrix4Generator : public Catch::Generators::IGenerator<Mat4<T>> {
 public:
    RandomMatrix4Generator(T range_min, T range_max)
        // NOLINTNEXTLINE
        : m_Gen(std::random_device{}()), m_Dist(range_min, range_max) {
        static_cast<void>(next());
    }

    auto get() const -> const Mat4<T>& override { return m_Value; }

    auto next() -> bool override {
        // Generate first column
        m_Value(0, 0) = m_Dist(m_Gen);
        m_Value(1, 0) = m_Dist(m_Gen);
        m_Value(2, 0) = m_Dist(m_Gen);
        m_Value(3, 0) = m_Dist(m_Gen);
        // Generate second column
        m_Value(0, 1) = m_Dist(m_Gen);
        m_Value(1, 1) = m_Dist(m_Gen);
        m_Value(2, 1) = m_Dist(m_Gen);
        m_Value(3, 1) = m_Dist(m_Gen);
        // Generate third column
        m_Value(0, 2) = m_Dist(m_Gen);
        m_Value(1, 2) = m_Dist(m_Gen);
        m_Value(2, 2) = m_Dist(m_Gen);
        m_Value(3, 2) = m_Dist(m_Gen);
        // Generate fourth column
        m_Value(0, 3) = m_Dist(m_Gen);
        m_Value(1, 3) = m_Dist(m_Gen);
        m_Value(2, 3) = m_Dist(m_Gen);
        m_Value(3, 3) = m_Dist(m_Gen);
        return true;
    }

 private:
    /// The method used to generate random numbers
    std::minstd_rand m_Gen;
    /// Distribution from which to generate random real values
    std::uniform_real_distribution<T> m_Dist;
    /// The random value to be exposed
    Mat4<T> m_Value;
};

//--------------------//
// Generator wrappers //
//--------------------//

template <typename T>
auto random_mat2(T val_range_min = static_cast<T>(-1.0),
                 T val_range_max = static_cast<T>(1.0))
    -> Catch::Generators::GeneratorWrapper<Mat2<T>> {
    return Catch::Generators::GeneratorWrapper<Mat2<T>>(
        Catch::Generators::pf::make_unique<RandomMatrix2Generator<T>>(
            val_range_min, val_range_max));
}

template <typename T>
auto random_mat3(T val_range_min = static_cast<T>(-1.0),
                 T val_range_max = static_cast<T>(1.0))
    -> Catch::Generators::GeneratorWrapper<Mat3<T>> {
    return Catch::Generators::GeneratorWrapper<Mat3<T>>(
        Catch::Generators::pf::make_unique<RandomMatrix3Generator<T>>(
            val_range_min, val_range_max));
}

template <typename T>
auto random_mat4(T val_range_min = static_cast<T>(-1.0),
                 T val_range_max = static_cast<T>(1.0))
    -> Catch::Generators::GeneratorWrapper<Mat4<T>> {
    return Catch::Generators::GeneratorWrapper<Mat4<T>>(
        Catch::Generators::pf::make_unique<RandomMatrix4Generator<T>>(
            val_range_min, val_range_max));
}

//****************************************************************************//
//                      Generators for Quaternion type                        //
//****************************************************************************//

//-------------------//
// Custom Generators //
//-------------------//

template <typename T>
class RandomQuaternion : public Catch::Generators::IGenerator<Quat<T>> {
 public:
    RandomQuaternion()
        // NOLINTNEXTLINE
        : m_Gen(std::random_device{}()), m_Dist(-1.0, 1.0) {
        static_cast<void>(next());
    }

    auto get() const -> const Quat<T>& override { return m_Value; }

    auto next() -> bool override {
        m_Value = {m_Dist(m_Gen), m_Dist(m_Gen), m_Dist(m_Gen), m_Dist(m_Gen)};
        return true;
    }

 private:
    /// The method used to generate random numbers
    std::minstd_rand m_Gen;
    /// Distribution from which to generate random real values
    std::uniform_real_distribution<T> m_Dist;
    /// The random value to be exposed
    Quat<T> m_Value;
};

template <typename T>
class RandomUnitQuaternion : public Catch::Generators::IGenerator<Quat<T>> {
 public:
    RandomUnitQuaternion()
        // NOLINTNEXTLINE
        : m_Gen(std::random_device{}()), m_Dist(-1.0, 1.0) {
        static_cast<void>(next());
    }

    auto get() const -> const Quat<T>& override { return m_Value; }

    auto next() -> bool override {
        m_Value = {m_Dist(m_Gen), m_Dist(m_Gen), m_Dist(m_Gen), m_Dist(m_Gen)};
        m_Value.normalize();
        return true;
    }

 private:
    /// The method used to generate random numbers
    std::minstd_rand m_Gen;
    /// Distribution from which to generate random real values
    std::uniform_real_distribution<T> m_Dist;
    /// The random value to be exposed
    Quat<T> m_Value;
};

//--------------------//
// Generator wrappers //
//--------------------//

template <typename T>
auto random_quaternion() -> Catch::Generators::GeneratorWrapper<Quat<T>> {
    return Catch::Generators::GeneratorWrapper<Quat<T>>(
        Catch::Generators::pf::make_unique<RandomQuaternion<T>>());
}

template <typename T>
auto random_unit_quaternion() -> Catch::Generators::GeneratorWrapper<Quat<T>> {
    return Catch::Generators::GeneratorWrapper<Quat<T>>(
        Catch::Generators::pf::make_unique<RandomUnitQuaternion<T>>());
}

//****************************************************************************//
//                     Generators for Euler angles type                       //
//****************************************************************************//

//-------------------//
// Custom Generators //
//-------------------//

template <typename T>
class RandomEuler : public Catch::Generators::IGenerator<Euler<T>> {
 public:
    RandomEuler()
        // NOLINTNEXTLINE
        : m_Gen(std::random_device{}()),
          m_Dist(static_cast<T>(-::math::PI), static_cast<T>(::math::PI)) {
        static_cast<void>(next());
    }

    auto get() const -> const Euler<T>& override { return m_Value; }

    auto next() -> bool override {
        m_Value.x = m_Dist(m_Gen);
        m_Value.y = m_Dist(m_Gen);
        m_Value.z = m_Dist(m_Gen);
        return true;
    }

 private:
    /// The method used to generate random numbers
    std::minstd_rand m_Gen;
    /// Distribution from which to generate random real values
    std::uniform_real_distribution<T> m_Dist;
    /// The random value to be exposed
    Euler<T> m_Value;
};

//--------------------//
// Generator wrappers //
//--------------------//

template <typename T>
auto random_euler() -> Catch::Generators::GeneratorWrapper<Euler<T>> {
    return Catch::Generators::GeneratorWrapper<Euler<T>>(
        Catch::Generators::pf::make_unique<RandomEuler<T>>());
}

//****************************************************************************//
//                    Generators for Transform(Mat4) type                     //
//****************************************************************************//

//-------------------//
// Custom Generators //
//-------------------//

template <typename T>
class RandomTransformMat4 : public Catch::Generators::IGenerator<Matrix4<T>> {
 public:
    RandomTransformMat4()
        : m_DistPosition(static_cast<T>(-10.0), static_cast<T>(10.0)),
          m_DistRotation(static_cast<T>(-1.0), static_cast<T>(1.0)),
          m_Gen(std::random_device{}()) {}  // NOLINT

    auto get() const -> const Matrix4<T>& override { return m_Value; }

    auto next() -> bool override {
        m_Position.x() = m_DistPosition(m_Gen);
        m_Position.y() = m_DistPosition(m_Gen);
        m_Position.z() = m_DistPosition(m_Gen);

        m_Orientation.w() = m_DistRotation(m_Gen);
        m_Orientation.x() = m_DistRotation(m_Gen);
        m_Orientation.y() = m_DistRotation(m_Gen);
        m_Orientation.z() = m_DistRotation(m_Gen);
        m_Orientation.normalize();

        return true;
    }

 private:
    /// Distribution from which to generate random values for positions
    std::uniform_real_distribution<T> m_DistPosition;
    /// Distribution from which to generate random values for quaternions
    std::uniform_real_distribution<T> m_DistRotation;
    /// The method used to generate random numbers
    std::minstd_rand m_Gen;
    /// The random transform to be exposed
    Matrix4<T> m_Value;
    /// The position used to generate the transform
    Vector3<T> m_Position;
    /// The orientation used to generate the transform
    Quaternion<T> m_Orientation;
};

//--------------------//
// Generator wrappers //
//--------------------//

template <typename T>
auto random_transform_mat4()
    -> Catch::Generators::GeneratorWrapper<Matrix4<T>> {
    return Catch::Generators::GeneratorWrapper<Matrix4<T>>(
        Catch::Generators::pf::make_unique<RandomTransformMat4<T>>());
}

}  // namespace math
