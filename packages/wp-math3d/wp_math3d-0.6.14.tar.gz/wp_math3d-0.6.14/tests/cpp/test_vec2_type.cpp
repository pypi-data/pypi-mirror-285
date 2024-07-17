#include <catch2/catch.hpp>
#include <math/vec2_t.hpp>

#include "./common_math_helpers.hpp"

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
TEMPLATE_TEST_CASE("Vector2 class (vec2_t) type", "[vec2_t][template]",
                   ::math::float32_t, ::math::float64_t) {
    using T = TestType;
    using Vector2 = ::math::Vector2<T>;

    constexpr T RANGE_MIN = static_cast<T>(USER_RANGE_MIN);
    constexpr T RANGE_MAX = static_cast<T>(USER_RANGE_MAX);
    constexpr T EPSILON = static_cast<T>(USER_EPSILON);

    SECTION("Get/Set using .x(), .y()") {
        auto val_x = gen_random_value(T, RANGE_MIN, RANGE_MAX, 10);
        auto val_y = gen_random_value(T, RANGE_MIN, RANGE_MAX, 10);

        Vector2 v;
        v.x() = val_x;
        v.y() = val_y;

        REQUIRE(::math::func_value_close<T>(v.x(), val_x, EPSILON));
        REQUIRE(::math::func_value_close<T>(v.y(), val_y, EPSILON));
    }

    SECTION("Default constructor") {
        Vector2 v;
        // Default constructor initializes the vector entries to zeros
        REQUIRE(::math::func_all_close<T>(v, 0.0, 0.0, EPSILON));
    }

    SECTION("From single scalar argument") {
        auto val_x = gen_random_value(T, RANGE_MIN, RANGE_MAX, 10);

        Vector2 v(val_x);
        // The given argument is copied for the second entry
        REQUIRE(::math::func_all_close<T>(v, val_x, val_x, EPSILON));
    }

    SECTION(
        "From two scalar arguments, from initializer_list, or using "
        "comma-initializer") {
        auto val_x = gen_random_value(T, RANGE_MIN, RANGE_MAX, 10);
        auto val_y = gen_random_value(T, RANGE_MIN, RANGE_MAX, 10);

        Vector2 v_1(val_x, val_y);
        Vector2 v_2 = {val_x, val_y};
        Vector2 v_3;
        // cppcheck-suppress constStatement
        v_3 << val_x, val_y;

        REQUIRE(::math::func_all_close<T>(v_1, val_x, val_y, EPSILON));
        REQUIRE(::math::func_all_close<T>(v_2, val_x, val_y, EPSILON));
        REQUIRE(::math::func_all_close<T>(v_3, val_x, val_y, EPSILON));
    }

    SECTION("Accessors [index]") {
        auto val_x = gen_random_value(T, RANGE_MIN, RANGE_MAX, 10);
        auto val_y = gen_random_value(T, RANGE_MIN, RANGE_MAX, 10);

        Vector2 v;
        v[0] = val_x;
        v[1] = val_y;
        REQUIRE(::math::func_all_close<T>(v, val_x, val_y, EPSILON));
    }
}

#if defined(__clang__)
#pragma clang diagnostic pop  // NOLINT
#elif defined(__GNUC__)
#pragma GCC diagnostic pop
#elif defined(_MSC_VER)
#pragma warning(pop)
#endif
