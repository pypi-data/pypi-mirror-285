#include <catch2/catch.hpp>
#include <math/quat_t.hpp>

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
TEMPLATE_TEST_CASE("Quaternion class (quat_t) constructors",
                   "[quat_t][template]", ::math::float32_t, ::math::float64_t) {
    using T = TestType;
    using Quat = ::math::Quaternion<T>;
    using Euler = ::math::Euler<T>;
    using Mat3 = ::math::Matrix3<T>;

    constexpr T EPSILON = static_cast<T>(USER_EPSILON);
    constexpr T RANGE_MIN = static_cast<T>(USER_RANGE_MIN);
    constexpr T RANGE_MAX = static_cast<T>(USER_RANGE_MAX);

    SECTION("Default constructor") {
        Quat q;
        REQUIRE(::math::func_all_close<T>(q, 1.0, 0.0, 0.0, 0.0, EPSILON));
    }

    SECTION("From single scalar argument") {
        constexpr auto NUM_SAMPLES = 32;
        auto val_w = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);

        Quat q(val_w);  // Real valued quaternion
        REQUIRE(::math::func_all_close<T>(q, val_w, 0.0, 0.0, 0.0, EPSILON));
    }

    SECTION("From four scalar arguments, and from initializer_list") {
        constexpr auto NUM_SAMPLES = 4;
        auto val_w = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto val_x = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto val_y = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto val_z = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);

        Quat q_1(val_w, val_x, val_y, val_z);
        Quat q_2 = {val_w, val_x, val_y, val_z};
        REQUIRE(::math::func_all_close<T>(q_1, val_w, val_x, val_y, val_z,
                                          EPSILON));
        REQUIRE(::math::func_all_close<T>(q_2, val_w, val_x, val_y, val_z,
                                          EPSILON));
    }

    SECTION("From rotation matrix") {
        // rot = Rot_x(t)
        // q = (cos(t/2), sin(t/2), 0.0, 0.0)
        {
            auto angle = ::math::PI / 4.0;
            auto rotmat = Mat3::RotationX(angle);
            Quat q(rotmat);
            auto cos_half = std::cos(angle / 2.0);
            auto sin_half = std::sin(angle / 2.0);
            REQUIRE(::math::func_all_close<T>(q, cos_half, sin_half, 0.0, 0.0,
                                              EPSILON));
        }

        // rot = Rot_y(t)
        // q = (cos(t/2), 0.0, sin(t/2), 0.0)
        {
            auto angle = ::math::PI / 4.0;
            auto rotmat = Mat3::RotationY(angle);
            Quat q(rotmat);
            auto cos_half = std::cos(angle / 2.0);
            auto sin_half = std::sin(angle / 2.0);
            REQUIRE(::math::func_all_close<T>(q, cos_half, 0.0, sin_half, 0.0,
                                              EPSILON));
        }

        // rot = Rot_z(t)
        // q = (cos(t/2), 0.0, 0.0, sin(t/2))
        {
            auto angle = ::math::PI / 4.0;
            auto rotmat = Mat3::RotationZ(angle);
            Quat q(rotmat);
            auto cos_half = std::cos(angle / 2.0);
            auto sin_half = std::sin(angle / 2.0);
            REQUIRE(::math::func_all_close<T>(q, cos_half, 0.0, 0.0, sin_half,
                                              EPSILON));
        }
    }

    SECTION("From Euler angles") {
        // ea = (0.0, 0.0, 0.0, XYZ, INTRINSIC)
        // q = (w, x, y, z) = (1.0, 0.0, 0.0, 0.0)
        {
            Euler e(0.0, 0.0, 0.0, ::math::euler::Order::XYZ,
                    ::math::euler::Convention::INTRINSIC);
            Quat q(e);
            REQUIRE(::math::func_all_close<T>(q, 1.0, 0.0, 0.0, 0.0, EPSILON));
        }

        // ea = (t, 0.0, 0.0, XYZ, INTRINSIC)
        // q = (cos(t/2), sint(t/2), 0.0, 0.0)
        {
            auto angle = math::PI / 4.0;
            Euler e(angle, 0.0, 0.0);
            Quat q(e);
            auto cos_half = std::cos(angle / 2.0);
            auto sin_half = std::sin(angle / 2.0);
            REQUIRE(::math::func_all_close<T>(q, cos_half, sin_half, 0.0, 0.0,
                                              EPSILON));
        }

        // ea = (0.0, t, 0.0, XYZ, INTRINSIC)
        // q = (cos(t/2), 0.0, sin(t/2), 0.0)
        {
            auto angle = math::PI / 4.0;
            Euler e(0.0, angle, 0.0);
            Quat q(e);
            auto cos_half = std::cos(angle / 2.0);
            auto sin_half = std::sin(angle / 2.0);
            REQUIRE(::math::func_all_close<T>(q, cos_half, 0.0, sin_half, 0.0,
                                              EPSILON));
        }

        // ea = (0.0, 0.0, t, XYZ, INTRINSIC)
        // q = (cos(t/2), 0.0, 0.0, sin(t/2))
        {
            auto angle = math::PI / 4.0;
            Euler e(0.0, 0.0, angle);
            Quat q(e);
            auto cos_half = std::cos(angle / 2.0);
            auto sin_half = std::sin(angle / 2.0);
            REQUIRE(::math::func_all_close<T>(q, cos_half, 0.0, 0.0, sin_half,
                                              EPSILON));
        }

        // e = (30°, 45°, 60°, XYZ, INTRINSIC)
        {
            Euler e(::math::PI / 6, ::math::PI / 4, ::math::PI / 3,
                    ::math::euler::Order::XYZ);
            Quat q(e);

            REQUIRE(::math::func_all_close<T>(q, 0.7233174, 0.3919038,
                                              0.2005621, 0.5319757, EPSILON));
        }

        // e = (30°, 45°, 60°, YXZ, INTRINSIC)
        {
            Euler e(::math::PI / 6, ::math::PI / 4, ::math::PI / 3,
                    ::math::euler::Order::YXZ);
            Quat q(e);

            REQUIRE(::math::func_all_close<T>(q, 0.8223632, 0.3919038,
                                              0.2005621, 0.3604234, EPSILON));
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
