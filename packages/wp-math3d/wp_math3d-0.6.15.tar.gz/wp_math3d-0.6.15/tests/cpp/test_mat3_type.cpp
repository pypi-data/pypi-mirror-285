#include <catch2/catch.hpp>
#include <math/mat3_t.hpp>

#include "./common_math_helpers.hpp"
#include "./common_math_generators.hpp"

#if defined(__clang__)
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wimplicit-float-conversion"
#pragma clang diagnostic ignored "-Wdouble-promotion"
#elif defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wfloat-conversion"
#pragma GCC diagnostic ignored "-Wdouble-promotion"
#elif defined(_MSC_VER)
#pragma warning(push)
#pragma warning(disable : 4305)
#pragma warning(disable : 4244)
#endif

constexpr double USER_RANGE_MIN = -100.0;
constexpr double USER_RANGE_MAX = 100.0;
constexpr double USER_EPSILON = 1e-5;

// NOLINTNEXTLINE
TEMPLATE_TEST_CASE("Matrix3 class (mat3_t) constructors", "[mat3_t][template]",
                   ::math::float32_t, ::math::float64_t) {
    using T = TestType;
    using Vec3 = ::math::Vector3<T>;
    using Euler = ::math::Euler<T>;
    using Mat3 = ::math::Matrix3<T>;
    using Mat4 = ::math::Matrix4<T>;
    using Quat = ::math::Quaternion<T>;

    constexpr T EPSILON = static_cast<T>(USER_EPSILON);
    constexpr T RANGE_MIN = static_cast<T>(USER_RANGE_MIN);
    constexpr T RANGE_MAX = static_cast<T>(USER_RANGE_MAX);

    // Checking all exposed constructors
    SECTION("Default constructor") {
        Mat3 mat;
        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat,
            0.0, 0.0, 0.0,
            0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, EPSILON));
        // clang-format on
    }

    SECTION("From all matrix entries") {
        // clang-format off
        Mat3 mat(1.0, 2.0, 3.0,
                 4.0, 5.0, 6.0,
                 7.0, 8.0, 9.0);

        REQUIRE(::math::func_all_close<T>(mat,
            1.0, 2.0, 3.0,
            4.0, 5.0, 6.0,
            7.0, 8.0, 9.0, EPSILON));
        // clang-format on
    }

    SECTION("From diagonal entries") {
        constexpr auto NUM_SAMPLES = 8;
        auto x00 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto x11 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto x22 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);

        Mat3 mat(x00, x11, x22);

        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat,
            x00, 0.0, 0.0,
            0.0, x11, 0.0,
            0.0, 0.0, x22, EPSILON));
        // clang-format on
    }

    SECTION("From column vectors") {
        constexpr auto NUM_SAMPLES = 8;
        auto x00 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto x11 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto x22 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);

        Vec3 col0 = {x00, 2.0, 3.0};
        Vec3 col1 = {4.0, x11, 6.0};
        Vec3 col2 = {7.0, 8.0, x22};

        Mat3 mat(col0, col1, col2);

        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat,
            x00, 4.0, 7.0,
            2.0, x11, 8.0,
            3.0, 6.0, x22, EPSILON));
        // clang-format on
    }

    SECTION("From quaternion") {
        // q = (1.0, 0.0, 0.0, 0.0)
        // m = Identity
        {
            Quat q(1.0, 0.0, 0.0, 0.0);
            Mat3 mat(q);

            // clang-format off
            REQUIRE(::math::func_all_close<T>(mat,
                1.0, 0.0, 0.0,
                0.0, 1.0, 0.0,
                0.0, 0.0, 1.0, EPSILON));
            // clang-format on
        }

        // q = (cos(t/2), sin(t/2), 0.0, 0.0) (rot. angle t around x-axis)
        // m = Rot_x(t)
        {
            auto angle = math::PI / 3.0;
            auto cos_half = std::cos(angle / 2.0);
            auto sin_half = std::sin(angle / 2.0);
            Quat q(cos_half, sin_half, 0.0, 0.0);

            Mat3 m(q);

            auto cos_t = std::cos(angle);
            auto sin_t = std::sin(angle);
            // clang-format off
            REQUIRE(::math::func_all_close<T>(m,
                1.0,  0.0 ,   0.0,
                0.0, cos_t, -sin_t,
                0.0, sin_t,  cos_t, EPSILON));
            // clang-format on
        }

        // q = (cos(t/2), 0.0, sin(t/2), 0.0) (rot. angle t around y-axis)
        // m = Rot_y(t)
        {
            auto angle = math::PI / 4.0;
            auto cos_half = std::cos(angle / 2.0);
            auto sin_half = std::sin(angle / 2.0);
            Quat q(cos_half, 0.0, sin_half, 0.0);

            Mat3 m(q);

            auto cos_t = std::cos(angle);
            auto sin_t = std::sin(angle);
            // clang-format off
            REQUIRE(::math::func_all_close<T>(m,
                 cos_t, 0.0, sin_t,
                  0.0 , 1.0,  0.0 ,
                -sin_t, 0.0, cos_t, EPSILON));
            // clang-format on
        }

        // q = (cos(t/2), 0.0, 0.0, sin(t/2)) (rot. angle t around z-axis)
        // m = Rot_z(t)
        {
            auto angle = ::math::PI / 4;
            auto cos_half = std::cos(angle / 2);
            auto sin_half = std::sin(angle / 2);
            Quat q(cos_half, 0.0, 0.0, sin_half);

            Mat3 m(q);

            auto cos_t = std::cos(angle);
            auto sin_t = std::sin(angle);
            // clang-format off
            REQUIRE(::math::func_all_close<T>(m,
                cos_t, -sin_t, 0.0,
                sin_t,  cos_t, 0.0,
                 0.0 ,   0.0 , 1.0, EPSILON));
            // clang-format on
        }

        // q = (0.7233174, 0.3919038, 0.2005621, 0.5319757)
        // e = (30°, 45°, 60°, XYZ, INTRINSIC)
        // m = ...
        {
            Quat q(0.7233174, 0.3919038, 0.2005621, 0.5319757);
            Mat3 m(q);

            // clang-format off
            REQUIRE(::math::func_all_close<T>(m,
                0.3535534, -0.6123725,  0.7071068,
                0.9267767,  0.1268265, -0.3535534,
                0.1268265,  0.7803301,  0.6123725, EPSILON));
            // clang-format on
        }
    }

    SECTION("From Euler angles") {
        constexpr auto NUM_SAMPLES = 8;
        auto theta = gen_random_value(T, -::math::PI, ::math::PI, NUM_SAMPLES);
        auto cos_t = std::cos(theta);
        auto sin_t = std::sin(theta);

        Euler e_x(theta, 0.0, 0.0);
        Euler e_y(0.0, theta, 0.0);
        Euler e_z(0.0, 0.0, theta);
        Mat3 mat_x(e_x);
        Mat3 mat_y(e_y);
        Mat3 mat_z(e_z);

        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_x,
            1.0,  0.0 ,   0.0 ,
            0.0, cos_t, -sin_t,
            0.0, sin_t,  cos_t, EPSILON));

        REQUIRE(::math::func_all_close<T>(mat_y,
            cos_t , 0.0,  sin_t ,
             0.0  , 1.0,   0.0  ,
           -sin_t , 0.0,  cos_t , EPSILON));

        REQUIRE(::math::func_all_close<T>(mat_z,
            cos_t , -sin_t , 0.0,
            sin_t ,  cos_t , 0.0,
             0.0  ,   0.0  , 1.0, EPSILON));
        // clang-format on
    }

    SECTION("From 4x4 transform matrix") {
        constexpr auto NUM_SAMPLES = 8;
        auto theta = gen_random_value(T, -::math::PI, ::math::PI, NUM_SAMPLES);
        auto cos_t = std::cos(theta);
        auto sin_t = std::sin(theta);

        Mat4 tf_x = Mat4::RotationX(theta);
        Mat4 tf_y = Mat4::RotationY(theta);
        Mat4 tf_z = Mat4::RotationZ(theta);
        Mat3 mat_x(tf_x);
        Mat3 mat_y(tf_y);
        Mat3 mat_z(tf_z);

        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_x,
            1.0,  0.0 ,   0.0 ,
            0.0, cos_t, -sin_t,
            0.0, sin_t,  cos_t, EPSILON));

        REQUIRE(::math::func_all_close<T>(mat_y,
            cos_t , 0.0,  sin_t ,
             0.0  , 1.0,   0.0  ,
           -sin_t , 0.0,  cos_t , EPSILON));

        REQUIRE(::math::func_all_close<T>(mat_z,
            cos_t , -sin_t , 0.0,
            sin_t ,  cos_t , 0.0,
             0.0  ,   0.0  , 1.0, EPSILON));
        // clang-format on
    }
}

#if defined(__clang__)
#pragma clang diagnostic pop  // NOLINT
#elif defined(__GNUC__)
#pragma GCC diagnostic pop
#elif defined(_MSC_VER)
#pragma warning(pop)
#endif
