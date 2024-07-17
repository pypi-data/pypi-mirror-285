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

constexpr auto NUM_SAMPLES = 10;

// NOLINTNEXTLINE
TEMPLATE_TEST_CASE("Matrix2 class (mat2_t) core operations", "[mat2_t][ops]",
                   ::math::float32_t, ::math::float64_t) {
    using T = TestType;
    using Matrix2 = math::Matrix2<T>;
    using Vector2 = math::Vector2<T>;

    constexpr T EPSILON = static_cast<T>(USER_EPSILON);
    constexpr T RANGE_MIN = static_cast<T>(USER_RANGE_MIN);
    constexpr T RANGE_MAX = static_cast<T>(USER_RANGE_MAX);

    SECTION("Matrix comparison ==, !=") {
        // clang-format off
        Matrix2 m_1(1.0, 0.0,
                    0.0, 2.0);
        Matrix2 m_2(1.0, 2.0);
        Matrix2 m_3(1.1, 2.1);
        // clang-format on

        REQUIRE(m_1 == m_2);
        REQUIRE(m_2 != m_3);
        REQUIRE(m_3 != m_1);
    }

    // Generate first random matrix
    const auto MAT_A = GENERATE(
        take(NUM_SAMPLES, ::math::random_mat2<T>(RANGE_MIN, RANGE_MAX)));
    // Generate second random matrix
    const auto MAT_B = GENERATE(
        take(NUM_SAMPLES, ::math::random_mat2<T>(RANGE_MIN, RANGE_MAX)));

    // Get a handle of the entries of these matrices
    auto x00 = MAT_A(0, 0);
    auto x10 = MAT_A(1, 0);
    auto x01 = MAT_A(0, 1);
    auto x11 = MAT_A(1, 1);

    auto y00 = MAT_B(0, 0);
    auto y10 = MAT_B(1, 0);
    auto y01 = MAT_B(0, 1);
    auto y11 = MAT_B(1, 1);

    SECTION("Matrix addition") {
        auto mat_sum = MAT_A + MAT_B;

        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_sum,
            x00 + y00, x01 + y01,
            x10 + y10, x11 + y11, EPSILON));
        // clang-format on
    }

    SECTION("Matrix substraction") {
        auto mat_sub = MAT_A - MAT_B;

        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_sub,
            x00 - y00, x01 - y01,
            x10 - y10, x11 - y11, EPSILON));
        // clang-format on
    }

    SECTION("Matrix-Scalar product") {
        auto scale_1 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto scale_2 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);

        auto mat_scaled_1 = scale_1 * MAT_A;
        auto mat_scaled_2 = MAT_B * scale_2;

        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_scaled_1,
            x00 * scale_1, x01 * scale_1,
            x10 * scale_1, x11 * scale_1, EPSILON));

        REQUIRE(::math::func_all_close<T>(mat_scaled_2,
            y00 * scale_2, y01 * scale_2,
            y10 * scale_2, y11 * scale_2, EPSILON));
        // clang-format on
    }

    SECTION("Matrix-Matrix product") {
        // Fixed test-case -------------------------------
        // clang-format off
        Matrix2 m_1(-6.0,  6.0,
                    -8.0, -1.0);
        Matrix2 m_2(6.0, 4.0,
                    2.0, 1.0);

        auto mat_mul = m_1 * m_2;

        REQUIRE(::math::func_all_close<T>(mat_mul,
            -24.0, -18.0,
            -50.0, -33.0, EPSILON));
        // clang-format on
        // -----------------------------------------------

        // Test-cases using the random matrices ----------
        auto mat_mul_ab = MAT_A * MAT_B;

        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_mul_ab,
            x00 * y00 + x01 * y10,
            x00 * y01 + x01 * y11,
            x10 * y00 + x11 * y10,
            x10 * y01 + x11 * y11, EPSILON));
        // clang-format on
        // -----------------------------------------------
    }

    SECTION("Matrix-Vector product") {
        // Fixed test-case -------------------------------
        // clang-format off
        Matrix2 mat(9.0,  8.0,
                    6.0, -4.0);
        // clang-format on
        Vector2 vec(6.0, 7.0);

        auto mat_vec_mul_1 = mat * vec;

        REQUIRE(::math::func_all_close<T>(mat_vec_mul_1, 110.0, 8.0, EPSILON));
        // -----------------------------------------------

        // Test-cases using the random matrices ----------
        auto v_a = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec2<T>(RANGE_MIN, RANGE_MAX)));

        auto mat_vec_mul_2 = MAT_A * v_a;

        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_vec_mul_2,
            x00 * v_a.x() + x01 * v_a.y(),
            x10 * v_a.x() + x11 * v_a.y(), EPSILON));
        // clang-format on
        // -----------------------------------------------
    }

    SECTION("Element-wise matrix product") {
        auto mat_ewise = ::math::hadamard(MAT_A, MAT_B);

        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_ewise,
            x00 * y00, x01 * y01,
            x10 * y10, x11 * y11, EPSILON));
        // clang-format on
    }

    SECTION("Matrix transposition") {
        // clang-format off
        // NOLINTNEXTLINE
        REQUIRE(::math::func_all_close<T>(::math::transpose(MAT_A),
            x00, x10,
            x01, x11, EPSILON));
        // NOLINTNEXTLINE
        REQUIRE(::math::func_all_close<T>(math::transpose(MAT_B),
            y00, y10,
            y01, y11, EPSILON));
        // clang-format on
    }

    SECTION("Matrix trace") {
        auto calc_trace_1 = ::math::trace(MAT_A);
        auto calc_trace_2 = ::math::trace(MAT_B);
        auto expected_trace_1 = x00 + x11;
        auto expected_trace_2 = y00 + y11;

        REQUIRE(::math::func_value_close<T>(calc_trace_1, expected_trace_1,
                                            EPSILON));
        REQUIRE(::math::func_value_close<T>(calc_trace_2, expected_trace_2,
                                            EPSILON));
    }

    SECTION("Matrix determinant") {
        // clang-format off
        auto mat = Matrix2(5.0, 5.0,
                           4.0, 8.0);
        // clang-format on

        auto calc_det = ::math::determinant(mat);
        auto expected_det = static_cast<T>(20.0);

        REQUIRE(::math::func_value_close<T>(calc_det, expected_det, EPSILON));
    }

    SECTION("Matrix inverse") {
        // clang-format off
        auto mat = Matrix2(5.0, 5.0,
                           4.0, 8.0);
        // clang-format on

        auto inv_mat = ::math::inverse(mat);
        // clang-format off
        REQUIRE(::math::func_all_close<T>(inv_mat,
             0.4, -0.25,
            -0.2,  0.25, EPSILON));
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
