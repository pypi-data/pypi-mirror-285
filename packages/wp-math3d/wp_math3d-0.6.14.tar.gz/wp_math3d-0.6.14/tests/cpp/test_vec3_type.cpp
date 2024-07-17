#include <catch2/catch.hpp>
#include <math/vec3_t.hpp>

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

constexpr double USER_RANGE_MIN = -1000.0;
constexpr double USER_RANGE_MAX = 1000.0;
constexpr double USER_EPSILON = 1e-5;

constexpr auto NUM_SAMPLES = 10;

// NOLINTNEXTLINE
TEMPLATE_TEST_CASE("Vector3 class (vec3_t) type", "[vec3_t][template]",
                   math::float32_t, math::float64_t) {
    using T = TestType;
    using Vector3 = ::math::Vector3<T>;

    constexpr T RANGE_MIN = static_cast<T>(USER_RANGE_MIN);
    constexpr T RANGE_MAX = static_cast<T>(USER_RANGE_MAX);
    constexpr T EPSILON = static_cast<T>(USER_EPSILON);

    SECTION("Get/Set using .x(), .y()") {
        auto val_x = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto val_y = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto val_z = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);

        Vector3 v;
        v.x() = val_x;
        v.y() = val_y;
        v.z() = val_z;

        REQUIRE(::math::func_value_close<T>(v.x(), val_x, EPSILON));
        REQUIRE(::math::func_value_close<T>(v.y(), val_y, EPSILON));
        REQUIRE(::math::func_value_close<T>(v.z(), val_z, EPSILON));
    }

    SECTION("Default constructor") {
        Vector3 v;
        REQUIRE(::math::func_all_close<T>(v, 0.0, 0.0, 0.0, EPSILON));
    }

    SECTION("From single scalar argument") {
        auto val_x = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);

        Vector3 v(val_x);
        // The given argument is copied to all other entries as well
        REQUIRE(::math::func_all_close<T>(v, val_x, val_x, val_x, EPSILON));
    }

    SECTION("From two scalar arguments") {
        auto val_x = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto val_y = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);

        Vector3 v(val_x, val_y);
        // The y component gets copied for the z component
        REQUIRE(::math::func_all_close<T>(v, val_x, val_y, val_y, EPSILON));
    }

    SECTION(
        "From three scalar arguments, from initializer_list, or using "
        "comma-initializer") {
        auto val_x = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto val_y = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto val_z = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);

        Vector3 v_1(val_x, val_y, val_z);
        Vector3 v_2 = {val_x, val_y, val_z};
        Vector3 v_3;
        // cppcheck-suppress constStatement
        v_3 << val_x, val_y, val_z;

        REQUIRE(::math::func_all_close<T>(v_1, val_x, val_y, val_z, EPSILON));
        REQUIRE(::math::func_all_close<T>(v_2, val_x, val_y, val_z, EPSILON));
        REQUIRE(::math::func_all_close<T>(v_3, val_x, val_y, val_z, EPSILON));
    }

    SECTION("Accessors [index]") {
        auto val_x = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto val_y = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto val_z = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);

        Vector3 v;
        v[0] = val_x;
        v[1] = val_y;
        v[2] = val_z;
        REQUIRE(::math::func_all_close<T>(v, val_x, val_y, val_z, EPSILON));
    }
}

#if defined(__clang__)
#pragma clang diagnostic pop  // NOLINT
#elif defined(__GNUC__)
#pragma GCC diagnostic pop
#elif defined(_MSC_VER)
#pragma warning(pop)
#endif
