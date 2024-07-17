#include <catch2/catch.hpp>
#include <math/mat4_t.hpp>

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

constexpr double USER_RANGE_MIN = -10.0;
constexpr double USER_RANGE_MAX = 10.0;
constexpr double USER_EPSILON = 1e-5;

// NOLINTNEXTLINE
TEMPLATE_TEST_CASE("Matrix4 class (mat4_t) constructors", "[mat4_t][template]",
                   ::math::float32_t, ::math::float64_t) {
    using T = TestType;
    using Euler = ::math::Euler<T>;
    using Quat = ::math::Quaternion<T>;
    using Mat3 = ::math::Matrix3<T>;
    using Mat4 = ::math::Matrix4<T>;

    constexpr T EPSILON = static_cast<T>(USER_EPSILON);
    constexpr T RANGE_MIN = static_cast<T>(USER_RANGE_MIN);
    constexpr T RANGE_MAX = static_cast<T>(USER_RANGE_MAX);

    // Checking all exposed constructors
    SECTION("Default constructor") {
        Mat4 mat;
        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat,
                0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, EPSILON));
        // clang-format on
    }

    SECTION("From all matrix entries") {
        // clang-format off
        Mat4 mat(1.0,  2.0,  3.0,  4.0,
                 5.0,  6.0,  7.0,  8.0,
                 9.0,  10.0, 11.0, 12.0,
                 13.0, 14.0, 15.0, 16.0);

        REQUIRE(::math::func_all_close<T>(mat,
                1.0,  2.0,  3.0,  4.0,
                5.0,  6.0,  7.0,  8.0,
                9.0,  10.0, 11.0, 12.0,
                13.0, 14.0, 15.0, 16.0, EPSILON));
        // clang-format on
    }

    SECTION("From diagonal entries") {
        constexpr auto NUM_SAMPLES = 2;
        auto x00 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto x11 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto x22 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto x33 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        Mat4 mat(x00, x11, x22, x33);
        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat,
                x00, 0.0, 0.0, 0.0,
                0.0, x11, 0.0, 0.0,
                0.0, 0.0, x22, 0.0,
                0.0, 0.0, 0.0, x33, EPSILON));
        // clang-format on
    }

    SECTION("From column vectors") {
        constexpr auto NUM_SAMPLES = 2;
        auto col0 = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec4<T>(RANGE_MIN, RANGE_MAX)));
        auto col1 = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec4<T>(RANGE_MIN, RANGE_MAX)));
        auto col2 = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec4<T>(RANGE_MIN, RANGE_MAX)));
        auto col3 = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec4<T>(RANGE_MIN, RANGE_MAX)));

        Mat4 mat(col0, col1, col2, col3);
        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat,
                col0.x(), col1.x(), col2.x(), col3.x(),
                col0.y(), col1.y(), col2.y(), col3.y(),
                col0.z(), col1.z(), col2.z(), col3.z(),
                col0.w(), col1.w(), col2.w(), col3.w(), EPSILON));
        // clang-format on
    }

    SECTION("From position and orientation") {
        constexpr auto NUM_SAMPLES = 8;
        auto position = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec3<T>(RANGE_MIN, RANGE_MAX)));

        SECTION("Orientation given as a rotation matrix") {
            auto angle =
                gen_random_value(T, -::math::PI, ::math::PI, NUM_SAMPLES);
            auto cos_t = std::cos(angle);
            auto sin_t = std::sin(angle);
            auto orientation = Mat3::RotationX(angle);

            Mat4 tf(position, orientation);
            // clang-format off
            REQUIRE(::math::func_all_close<T>(tf,
                    1.0,  0.0 ,   0.0  , position.x(),
                    0.0, cos_t, -sin_t , position.y(),
                    0.0, sin_t,  cos_t , position.z(),
                    0.0,  0.0 ,   0.0  , 1.0, EPSILON));
            // clang-format on
        }

        SECTION("Orientation given as a quaternion") {
            auto angle =
                gen_random_value(T, -::math::PI, ::math::PI, NUM_SAMPLES);
            auto cos_t = std::cos(angle);
            auto sin_t = std::sin(angle);
            auto orientation = Quat::RotationY(angle);

            Mat4 tf(position, orientation);
            // clang-format off
            REQUIRE(::math::func_all_close<T>(tf,
                     cos_t , 0.0 , sin_t , position.x(),
                      0.0  , 1.0 ,  0.0  , position.y(),
                    -sin_t , 0.0 , cos_t , position.z(),
                      0.0  , 0.0 ,  0.0  , 1.0, EPSILON));
            // clang-format on
        }

        SECTION("Orientation given as euler angles") {
            auto angle =
                gen_random_value(T, -::math::PI, ::math::PI, NUM_SAMPLES);
            auto cos_t = std::cos(angle);
            auto sin_t = std::sin(angle);
            auto orientation = Euler(0.0, 0.0, angle);

            Mat4 tf(position, orientation);
            // clang-format off
            REQUIRE(::math::func_all_close<T>(tf,
                    cos_t, -sin_t , 0.0 , position.x(),
                    sin_t,  cos_t , 0.0 , position.y(),
                     0.0 ,   0.0  , 1.0 , position.z(),
                     0.0 ,   0.0  , 0.0 , 1.0, EPSILON));
            // clang-format on
        }
    }
}

#if defined(__clang__)
#pragma clang diagnostic pop  // NOLINT
#elif defined(__GNUC__)
#pragma GCC diagnostic pop
#elif defined(_MSC_VER)
#pragma warning(pop)
#endif
