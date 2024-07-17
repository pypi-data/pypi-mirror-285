#include <catch2/catch.hpp>
#include <math/mat3_t.hpp>
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

constexpr double USER_ANGLE_MIN = -math::PI;
constexpr double USER_ANGLE_MAX = math::PI;
constexpr double USER_SCALE_MIN = -10.0;
constexpr double USER_SCALE_MAX = 10.0;
constexpr double USER_RANGE_MIN = -10.0;
constexpr double USER_RANGE_MAX = 10.0;
constexpr double USER_EPSILON = 1e-5;

// NOLINTNEXTLINE
TEMPLATE_TEST_CASE("Matrix3 class (mat3_t) factory functions",
                   "[mat3_t][funcs]", ::math::float32_t, ::math::float64_t) {
    using T = TestType;
    using Matrix3 = ::math::Matrix3<T>;
    using Quaternion = ::math::Quaternion<T>;

    constexpr T EPSILON = static_cast<T>(USER_EPSILON);
    constexpr T ANGLE_MIN = static_cast<T>(USER_ANGLE_MIN);
    constexpr T ANGLE_MAX = static_cast<T>(USER_ANGLE_MAX);
    constexpr T SCALE_MIN = static_cast<T>(USER_SCALE_MIN);
    constexpr T SCALE_MAX = static_cast<T>(USER_SCALE_MAX);
    constexpr T RANGE_MIN = static_cast<T>(USER_RANGE_MIN);
    constexpr T RANGE_MAX = static_cast<T>(USER_RANGE_MAX);

    SECTION("Rotation matrix - from Quaternion") {
        // TODO(wilbert): replace by random generator for quat
        constexpr auto NUM_SAMPLES = 4;
        auto w = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto x = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto y = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto z = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);

        auto quat = Quaternion(w, x, y, z);
        auto rot_mat = Matrix3(quat);

        auto length = std::sqrt(w * w + x * x + y * y + z * z);
        w /= length;
        x /= length;
        y /= length;
        z /= length;

        auto xx = x * x;
        auto yy = y * y;
        auto zz = z * z;
        auto xy = x * y;
        auto wz = w * z;
        auto xz = x * z;
        auto wy = w * y;
        auto yz = y * z;
        auto wx = w * x;

        // clang-format off
        REQUIRE(::math::func_all_close<T>(rot_mat,
        1.0 - 2.0 * (yy + zz),     2.0 * (xy - wz)   ,    2.0 * (xz + wy)   ,
            2.0 * (xy + wz)  , 1.0 - 2.0 * (xx + zz) ,    2.0 * (yz - wx)   ,
            2.0 * (xz - wy)  ,     2.0 * (yz + wx)   , 1.0 - 2.0 * (xx + yy),
        EPSILON));
        // clang-format on
    }

    SECTION("Rotation matrix - X") {
        constexpr auto NUM_SAMPLES = 100;
        auto angle = gen_random_value(T, ANGLE_MIN, ANGLE_MAX, NUM_SAMPLES);
        auto rot_mat = Matrix3::RotationX(angle);

        // clang-format off
        REQUIRE(::math::func_all_close<T>(rot_mat,
                1.0,        0.0     ,       0.0       ,
                0.0, std::cos(angle), -std::sin(angle),
                0.0, std::sin(angle),  std::cos(angle), EPSILON));
        // clang-format on
    }

    SECTION("Rotation matrix - Y") {
        constexpr auto NUM_SAMPLES = 100;
        auto angle = gen_random_value(T, ANGLE_MIN, ANGLE_MAX, NUM_SAMPLES);
        auto rot_mat = Matrix3::RotationY(angle);

        // clang-format off
        REQUIRE(::math::func_all_close<T>(rot_mat,
                 std::cos(angle), 0.0, std::sin(angle),
                       0.0      , 1.0,       0.0      ,
                -std::sin(angle), 0.0, std::cos(angle), EPSILON));
        // clang-format on
    }

    SECTION("Rotation matrix - Z") {
        constexpr auto NUM_SAMPLES = 100;
        auto angle = gen_random_value(T, ANGLE_MIN, ANGLE_MAX, NUM_SAMPLES);
        auto rot_mat = Matrix3::RotationZ(angle);

        // clang-format off
        REQUIRE(::math::func_all_close<T>(rot_mat,
                std::cos(angle), -std::sin(angle), 0.0,
                std::sin(angle),  std::cos(angle), 0.0,
                     0.0       ,        0.0      , 1.0, EPSILON));
        // clang-format on
    }

    SECTION("Scale matrix - from scalars") {
        constexpr auto NUM_SAMPLES = 10;
        auto scale_x = gen_random_value(T, SCALE_MIN, SCALE_MAX, NUM_SAMPLES);
        auto scale_y = gen_random_value(T, SCALE_MIN, SCALE_MAX, NUM_SAMPLES);
        auto scale_z = gen_random_value(T, SCALE_MIN, SCALE_MAX, NUM_SAMPLES);
        auto scale_mat = Matrix3::Scale(scale_x, scale_y, scale_z);

        // clang-format off
        REQUIRE(::math::func_all_close<T>(scale_mat,
                scale_x,   0.0  ,   0.0  ,
                    0.0, scale_y,   0.0  ,
                    0.0,   0.0  , scale_z, EPSILON));
        // clang-format on
    }

    SECTION("Scale matrix - from vec3") {
        constexpr auto NUM_SAMPLES = 10;
        auto scale = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec3<T>(SCALE_MIN, SCALE_MAX)));
        auto scale_mat = Matrix3::Scale(scale);

        // clang-format off
        REQUIRE(::math::func_all_close<T>(scale_mat,
                scale.x(),   0.0  ,   0.0  ,
                    0.0, scale.y(),   0.0  ,
                    0.0,   0.0  , scale.z(), EPSILON));
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
