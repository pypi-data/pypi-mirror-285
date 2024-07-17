#include <catch2/catch.hpp>
#include <math/mat2_t.hpp>

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

constexpr double USER_ANGLE_MIN = -::math::PI;
constexpr double USER_ANGLE_MAX = ::math::PI;
constexpr double USER_SCALE_MIN = -10.0;
constexpr double USER_SCALE_MAX = 10.0;
constexpr double USER_EPSILON = 1e-5;

constexpr auto NUM_SAMPLES = 100;

// NOLINTNEXTLINE
TEMPLATE_TEST_CASE("Matrix2 class (mat2_t) factory functions",
                   "[mat2_t][funcs]", ::math::float32_t, ::math::float64_t) {
    using T = TestType;
    using Matrix2 = ::math::Matrix2<T>;

    constexpr T EPSILON = static_cast<T>(USER_EPSILON);
    constexpr T ANGLE_MIN = static_cast<T>(USER_ANGLE_MIN);
    constexpr T ANGLE_MAX = static_cast<T>(USER_ANGLE_MAX);
    constexpr T SCALE_MIN = static_cast<T>(USER_SCALE_MIN);
    constexpr T SCALE_MAX = static_cast<T>(USER_SCALE_MAX);

    SECTION("Rotation matrix") {
        auto angle = gen_random_value(T, ANGLE_MIN, ANGLE_MAX, NUM_SAMPLES);
        auto rot_mat = Matrix2::Rotation(angle);

        // clang-format off
        REQUIRE(::math::func_all_close<T>(rot_mat,
            std::cos(angle), -std::sin(angle),
            std::sin(angle),  std::cos(angle), EPSILON));
        // clang-format on
    }

    SECTION("Scale matrix - from scalars") {
        auto scale_x = gen_random_value(T, SCALE_MIN, SCALE_MAX, NUM_SAMPLES);
        auto scale_y = gen_random_value(T, SCALE_MIN, SCALE_MAX, NUM_SAMPLES);
        auto scale_mat = Matrix2::Scale(scale_x, scale_y);

        // clang-format off
        REQUIRE(::math::func_all_close<T>(scale_mat,
            scale_x, 0.0,
              0.0, scale_y, EPSILON));
        // clang-format on
    }

    SECTION("Scale matrix - from vec2") {
        auto scale = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec2<T>(SCALE_MIN, SCALE_MAX)));
        auto scale_mat = Matrix2::Scale(scale);

        // clang-format off
        REQUIRE(::math::func_all_close<T>(scale_mat,
            scale.x(), 0.0,
            0.0, scale.y(), EPSILON));
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
