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

constexpr double USER_RANGE_MIN = -10.0;
constexpr double USER_RANGE_MAX = 10.0;
constexpr double USER_EPSILON = 1e-5;

// NOLINTNEXTLINE
TEMPLATE_TEST_CASE("Matrix4 class (mat2_t) constructors", "[mat2_t][template]",
                   ::math::float32_t, ::math::float64_t) {
    using T = TestType;
    using Matrix2 = ::math::Matrix2<T>;

    constexpr T EPSILON = static_cast<T>(USER_EPSILON);
    constexpr T RANGE_MIN = static_cast<T>(USER_RANGE_MIN);
    constexpr T RANGE_MAX = static_cast<T>(USER_RANGE_MAX);

    SECTION("Default constructor") {
        Matrix2 mat;
        // Default constructor creates zero-initialized matrix
        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat,
            0.0, 0.0,
            0.0, 0.0, EPSILON));
        // clang-format on
    }

    SECTION("From all matrix entries") {
        constexpr auto NUM_SAMPLES = 4;
        auto x00 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto x01 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto x10 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto x11 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);

        Matrix2 mat(x00, x01, x10, x11);
        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat,
            x00, x01,
            x10, x11, EPSILON));
        // clang-format on
    }

    SECTION("From diagonal entries") {
        constexpr auto NUM_SAMPLES = 8;
        auto x00 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto x11 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);

        Matrix2 mat(x00, x11);
        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat,
            x00, 0.0,
            0.0, x11, EPSILON));
        // clang-format on
    }

    SECTION("From column vectors") {
        constexpr auto NUM_SAMPLES = 8;
        auto col0 = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec2<T>(RANGE_MIN, RANGE_MAX)));
        auto col1 = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec2<T>(RANGE_MIN, RANGE_MAX)));

        Matrix2 mat(col0, col1);
        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat,
            col0.x(), col1.x(),
            col0.y(), col1.y(), EPSILON));
        // clang-format on
    }

    SECTION("Accessor (i, j) returns scalar entry") {
        Matrix2 mat;
        // Update entries in first column
        mat(0, 0) = 1.0;
        mat(1, 0) = 2.0;
        // Update entries in second column
        mat(0, 1) = 3.0;
        mat(1, 1) = 4.0;
        // Make sure all entries are set accordingly
        REQUIRE(::math::func_value_close<T>(mat(0, 0), 1.0, EPSILON));
        REQUIRE(::math::func_value_close<T>(mat(1, 0), 2.0, EPSILON));
        REQUIRE(::math::func_value_close<T>(mat(0, 1), 3.0, EPSILON));
        REQUIRE(::math::func_value_close<T>(mat(1, 1), 4.0, EPSILON));
    }

    SECTION("Accessor [idx] returns column at index 'idx'") {
        // clang-format off
        Matrix2 mat(
            1.0, 2.0,
            3.0, 4.0);
        // clang-format on
        auto col0 = mat[0];
        auto col1 = mat[1];
        // Make sure we got the right column vectors from the matrix
        REQUIRE(::math::func_all_close<T>(col0, 1.0, 3.0, EPSILON));
        REQUIRE(::math::func_all_close<T>(col1, 2.0, 4.0, EPSILON));
    }
}

#if defined(__clang__)
#pragma clang diagnostic pop  // NOLINT
#elif defined(__GNUC__)
#pragma GCC diagnostic pop
#elif defined(_MSC_VER)
#pragma warning(pop)
#endif
