#include <catch2/catch.hpp>
#include <math/vec2_t.hpp>

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

constexpr double USER_RANGE_MIN = -1000.0;
constexpr double USER_RANGE_MAX = 1000.0;

// NOLINTNEXTLINE
TEMPLATE_TEST_CASE("Vector2 class (vec2_t) core Operations", "[vec2_t][ops]",
                   math::float32_t, math::float64_t) {
    using T = TestType;
    using Vector2 = math::Vector2<T>;

    constexpr T EPSILON = static_cast<T>(math::EPS);
    constexpr T RANGE_MIN = static_cast<T>(USER_RANGE_MIN);
    constexpr T RANGE_MAX = static_cast<T>(USER_RANGE_MAX);

    SECTION("Vector comparison ==, !=") {
        Vector2 v_1(1.0, 2.0);
        Vector2 v_2(1.0, 2.0);
        Vector2 v_3(1.1, 2.1);

        REQUIRE(v_1 == v_2);
        REQUIRE(v_2 != v_3);
        REQUIRE(v_3 != v_1);
    }

    SECTION("Vector addition") {
        auto v_a =
            GENERATE(take(10, ::math::random_vec2<T>(RANGE_MIN, RANGE_MAX)));
        auto v_b =
            GENERATE(take(10, ::math::random_vec2<T>(RANGE_MIN, RANGE_MAX)));

        auto v_result = v_a + v_b;

        // clang-format off
        REQUIRE(::math::func_all_close<T>(v_result,
            v_a.x() + v_b.x(),
            v_a.y() + v_b.y(),
            EPSILON));
        // clang-format on
    }

    SECTION("Vector substraction") {
        auto v_a =
            GENERATE(take(10, ::math::random_vec2<T>(RANGE_MIN, RANGE_MAX)));
        auto v_b =
            GENERATE(take(10, ::math::random_vec2<T>(RANGE_MIN, RANGE_MAX)));

        auto v_result = v_a - v_b;

        // clang-format off
        REQUIRE(::math::func_all_close<T>(v_result,
            v_a.x() - v_b.x(),
            v_a.y() - v_b.y(),
            EPSILON));
        // clang-format on
    }

    SECTION("Vector element-wise product") {
        auto v_a =
            GENERATE(take(10, ::math::random_vec2<T>(RANGE_MIN, RANGE_MAX)));
        auto v_b =
            GENERATE(take(10, ::math::random_vec2<T>(RANGE_MIN, RANGE_MAX)));

        auto v_result = v_a * v_b;

        // clang-format off
        REQUIRE(::math::func_all_close<T>(v_result,
            v_a.x() * v_b.x(),
            v_a.y() * v_b.y(),
            EPSILON));
        // clang-format on
    }

    SECTION("Vector scale (by single scalar)") {
        auto v =
            GENERATE(take(10, ::math::random_vec2<T>(RANGE_MIN, RANGE_MAX)));
        auto scale = gen_random_value(T, RANGE_MIN, RANGE_MAX, 10);

        auto v_1 = scale * v;
        auto v_2 = v * scale;

        REQUIRE(::math::func_all_close<T>(v_1, v.x() * scale, v.y() * scale,
                                          EPSILON));
        REQUIRE(::math::func_all_close<T>(v_2, v.x() * scale, v.y() * scale,
                                          EPSILON));
    }

    SECTION("Vector length") {
        auto v =
            GENERATE(take(10, ::math::random_vec2<T>(RANGE_MIN, RANGE_MAX)));

        auto length_square = v.x() * v.x() + v.y() * v.y();
        auto length = std::sqrt(length_square);

        auto v_length_square = ::math::squareNorm(v);
        auto v_length = ::math::norm(v);

        REQUIRE(::math::func_value_close<T>(v_length_square, length_square,
                                            EPSILON));
        REQUIRE(::math::func_value_close<T>(v_length, length, EPSILON));
    }

    SECTION("Vector normalization (in place)") {
        auto v =
            GENERATE(take(10, ::math::random_vec2<T>(RANGE_MIN, RANGE_MAX)));
        // Compute the norm and normalize the vector manually
        auto norm = std::sqrt(v.x() * v.x() + v.y() * v.y());
        auto val_xnorm = v.x() / norm;
        auto val_ynorm = v.y() / norm;

        // Normalize the vector and make sure it gives the expected result
        ::math::normalize_in_place(v);
        REQUIRE(::math::func_all_close<T>(v, val_xnorm, val_ynorm, EPSILON));

        // Make sure the norm of the normalized vector is 1.0
        auto v_norm = ::math::norm(v);
        REQUIRE(::math::func_value_close<T>(v_norm, 1.0, EPSILON));
    }

    SECTION("Vector normalization (out-of place)") {
        auto v =
            GENERATE(take(10, ::math::random_vec2<T>(RANGE_MIN, RANGE_MAX)));
        // Compute the norm and normalize the vector manually
        auto norm = std::sqrt(v.x() * v.x() + v.y() * v.y());
        auto val_xnorm = v.x() / norm;
        auto val_ynorm = v.y() / norm;

        // Normalize the vector and make sure it gives the expected result
        auto vn = ::math::normalize(v);
        REQUIRE(::math::func_all_close<T>(vn, val_xnorm, val_ynorm, EPSILON));

        // Make sure the norm of the normalized vector is 1.0
        auto vn_norm = math::norm(vn);
        REQUIRE(::math::func_value_close<T>(vn_norm, 1.0, EPSILON));
    }

    SECTION("Vector dot-product") {
        auto v_a =
            GENERATE(take(10, ::math::random_vec2<T>(RANGE_MIN, RANGE_MAX)));
        auto v_b =
            GENERATE(take(10, ::math::random_vec2<T>(RANGE_MIN, RANGE_MAX)));

        auto dot = v_a.x() * v_b.x() + v_a.y() * v_b.y();
        auto v_dot = ::math::dot(v_a, v_b);

        REQUIRE(::math::func_value_close<T>(v_dot, dot, EPSILON));
    }

    SECTION("Vector additive inverse") {
        auto v =
            GENERATE(take(10, ::math::random_vec2<T>(RANGE_MIN, RANGE_MAX)));
        auto inv_v = -v;

        REQUIRE(::math::func_all_close<T>(inv_v, -v.x(), -v.y(), EPSILON));
    }
}

#if defined(__clang__)
#pragma clang diagnostic pop  // NOLINT
#elif defined(__GNUC__)
#pragma GCC diagnostic pop
#elif defined(_MSC_VER)
#pragma warning(pop)
#endif
