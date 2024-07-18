#include <catch2/catch.hpp>
#include <math/vec3_t.hpp>

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
constexpr double USER_EPSILON = 1e-5;

constexpr auto NUM_SAMPLES = 10;

// NOLINTNEXTLINE
TEMPLATE_TEST_CASE("Vector3 class (vec3_t) core Operations", "[vec3_t][ops]",
                   math::float32_t, math::float64_t) {
    using T = TestType;
    using Vector3 = math::Vector3<T>;

    constexpr T EPSILON = static_cast<T>(USER_EPSILON);
    constexpr T RANGE_MIN = static_cast<T>(USER_RANGE_MIN);
    constexpr T RANGE_MAX = static_cast<T>(USER_RANGE_MAX);

    SECTION("Vector comparison ==, !=") {
        Vector3 v_1(1.0, 2.0, 3.0);
        Vector3 v_2(1.0, 2.0, 3.0);
        Vector3 v_3(1.1, 2.1, 3.1);

        REQUIRE(v_1 == v_2);
        REQUIRE(v_2 != v_3);
        REQUIRE(v_3 != v_1);
    }

    SECTION("Vector addition") {
        auto v_a = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec3<T>(RANGE_MIN, RANGE_MAX)));
        auto v_b = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec3<T>(RANGE_MIN, RANGE_MAX)));

        auto v_result = v_a + v_b;
        // clang-format off
        REQUIRE(::math::func_all_close<T>(v_result,
            v_a.x() + v_b.x(),
            v_a.y() + v_b.y(),
            v_a.z() + v_b.z(), EPSILON));
        // clang-format on
    }

    SECTION("Vector substraction") {
        auto v_a = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec3<T>(RANGE_MIN, RANGE_MAX)));
        auto v_b = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec3<T>(RANGE_MIN, RANGE_MAX)));

        auto v_result = v_a - v_b;

        // clang-format off
        REQUIRE(::math::func_all_close<T>(v_result,
            v_a.x() - v_b.x(),
            v_a.y() - v_b.y(),
            v_a.z() - v_b.z(), EPSILON));
        // clang-format on
    }

    SECTION("Vector element-wise product") {
        auto v_a = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec3<T>(RANGE_MIN, RANGE_MAX)));
        auto v_b = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec3<T>(RANGE_MIN, RANGE_MAX)));

        auto v_result = v_a * v_b;

        // clang-format off
        REQUIRE(::math::func_all_close<T>(v_result,
            v_a.x() * v_b.x(),
            v_a.y() * v_b.y(),
            v_a.z() * v_b.z(), EPSILON));
        // clang-format on
    }

    SECTION("Vector scale (by single scalar)") {
        auto v = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec3<T>(RANGE_MIN, RANGE_MAX)));
        auto scale = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);

        auto v_1 = scale * v;
        auto v_2 = v * scale;

        REQUIRE(::math::func_all_close<T>(v_1, v.x() * scale, v.y() * scale,
                                          v.z() * scale, EPSILON));
        REQUIRE(::math::func_all_close<T>(v_2, v.x() * scale, v.y() * scale,
                                          v.z() * scale, EPSILON));
    }

    SECTION("Vector length") {
        auto v = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec3<T>(RANGE_MIN, RANGE_MAX)));

        auto length_square = v.x() * v.x() + v.y() * v.y() + v.z() * v.z();
        auto length = std::sqrt(length_square);

        auto v_length_square = ::math::squareNorm(v);
        auto v_length = ::math::norm(v);

        REQUIRE(::math::func_value_close<T>(v_length_square, length_square,
                                            EPSILON));
        REQUIRE(::math::func_value_close<T>(v_length, length, EPSILON));
    }

    SECTION("Vector normalization (in place)") {
        auto v = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec3<T>(RANGE_MIN, RANGE_MAX)));
        // Compute the norm and normalize the vector manually
        auto norm = std::sqrt(v.x() * v.x() + v.y() * v.y() + v.z() * v.z());
        auto val_xnorm = v.x() / norm;
        auto val_ynorm = v.y() / norm;
        auto val_znorm = v.z() / norm;

        // Normalize the vector and make sure it gives the expected result
        ::math::normalize_in_place(v);
        REQUIRE(::math::func_all_close<T>(v, val_xnorm, val_ynorm, val_znorm,
                                          EPSILON));

        // Make sure the norm of the normalized vector is 1.0
        auto v_norm = ::math::norm(v);
        REQUIRE(::math::func_value_close<T>(v_norm, 1.0, EPSILON));
    }

    SECTION("Vector normalization (out-of place)") {
        auto v = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec3<T>(RANGE_MIN, RANGE_MAX)));
        // Compute the norm and normalize the vector manually
        auto norm = std::sqrt(v.x() * v.x() + v.y() * v.y() + v.z() * v.z());
        auto val_xnorm = v.x() / norm;
        auto val_ynorm = v.y() / norm;
        auto val_znorm = v.z() / norm;

        // Normalize the vector and make sure it gives the expected result
        auto vn = ::math::normalize(v);
        REQUIRE(::math::func_all_close<T>(vn, val_xnorm, val_ynorm, val_znorm,
                                          EPSILON));

        // Make sure the norm of the normalized vector is 1.0
        auto vn_norm = ::math::norm(vn);
        REQUIRE(::math::func_value_close<T>(vn_norm, 1.0, EPSILON));
    }

    SECTION("Vector dot-product") {
        auto v_a = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec3<T>(RANGE_MIN, RANGE_MAX)));
        auto v_b = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec3<T>(RANGE_MIN, RANGE_MAX)));

        auto dot = v_a.x() * v_b.x() + v_a.y() * v_b.y() + v_a.z() * v_b.z();
        auto v_dot = ::math::dot(v_a, v_b);

        REQUIRE(::math::func_value_close<T>(v_dot, dot, EPSILON));
    }

    SECTION("Vector cross-product") {
        // Checking standard basis vectors: i, j, k
        {
            Vector3 v_i(1.0, 0.0, 0.0);
            Vector3 v_j(0.0, 1.0, 0.0);
            Vector3 v_k(0.0, 0.0, 1.0);

            auto v_ij = ::math::cross(v_i, v_j);
            auto v_jk = ::math::cross(v_j, v_k);
            auto v_ki = ::math::cross(v_k, v_i);

            // i x j = k
            REQUIRE(::math::func_all_close<T>(v_ij, 0.0, 0.0, 1.0, EPSILON));

            // j x k = i
            REQUIRE(::math::func_all_close<T>(v_jk, 1.0, 0.0, 0.0, EPSILON));

            // k x i = j
            REQUIRE(::math::func_all_close<T>(v_ki, 0.0, 1.0, 0.0, EPSILON));
        }

        // Checking a fixed case (a.cross(b) + c)
        {
            Vector3 v_a(1.0, 2.0, 3.0);
            Vector3 v_b(4.0, 5.0, 6.0);
            Vector3 v_c(7.0, 8.0, 9.0);

            auto result = ::math::cross(v_a, v_b) + v_c;
            REQUIRE(::math::func_all_close<T>(result, 4.0, 14.0, 6.0, EPSILON));
        }
    }

    SECTION("Vector additive inverse") {
        auto v = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec3<T>(RANGE_MIN, RANGE_MAX)));
        auto inv_v = -v;

        REQUIRE(
            ::math::func_all_close<T>(inv_v, -v.x(), -v.y(), -v.z(), EPSILON));
    }
}

#if defined(__clang__)
#pragma clang diagnostic pop  // NOLINT
#elif defined(__GNUC__)
#pragma GCC diagnostic pop
#elif defined(_MSC_VER)
#pragma warning(pop)
#endif
