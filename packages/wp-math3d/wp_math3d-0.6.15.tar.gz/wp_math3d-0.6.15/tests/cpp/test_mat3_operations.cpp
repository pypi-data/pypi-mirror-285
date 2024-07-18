#include <catch2/catch.hpp>
#include <math/mat3_t.hpp>

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

constexpr auto NUM_SAMPLES = 8;

// NOLINTNEXTLINE
TEMPLATE_TEST_CASE("Matrix3 class (mat3_t) core operations", "[mat3_t][ops]",
                   ::math::float32_t, ::math::float64_t) {
    using T = TestType;
    using Matrix3 = ::math::Matrix3<T>;
    using Vector3 = ::math::Vector3<T>;

    constexpr T EPSILON = static_cast<T>(USER_EPSILON);
    constexpr T RANGE_MIN = static_cast<T>(USER_RANGE_MIN);
    constexpr T RANGE_MAX = static_cast<T>(USER_RANGE_MAX);

    SECTION("Matrix comparison ==, !=") {
        // clang-format off
        Matrix3 m_1(1.0, 0.0, 0.0,
                    0.0, 2.0, 0.0,
                    0.0, 0.0, 3.0);
        Matrix3 m_2(1.0, 2.0, 3.0);
        Matrix3 m_3(static_cast<T>(1.1),
                    static_cast<T>(2.1),
                    static_cast<T>(3.1));
        // clang-format on
        REQUIRE(m_1 == m_2);
        REQUIRE(m_2 != m_3);
        REQUIRE(m_3 != m_1);
    }

    // Generate first random matrix
    const auto MAT_A = GENERATE(
        take(NUM_SAMPLES, ::math::random_mat3<T>(RANGE_MIN, RANGE_MAX)));
    // Generate second random matrix
    const auto MAT_B = GENERATE(
        take(NUM_SAMPLES, ::math::random_mat3<T>(RANGE_MIN, RANGE_MAX)));

    // Get a handle of the entries of these matrices
    auto x00 = MAT_A(0, 0);
    auto x01 = MAT_A(0, 1);
    auto x02 = MAT_A(0, 2);

    auto x10 = MAT_A(1, 0);
    auto x11 = MAT_A(1, 1);
    auto x12 = MAT_A(1, 2);

    auto x20 = MAT_A(2, 0);
    auto x21 = MAT_A(2, 1);
    auto x22 = MAT_A(2, 2);

    auto y00 = MAT_B(0, 0);
    auto y01 = MAT_B(0, 1);
    auto y02 = MAT_B(0, 2);

    auto y10 = MAT_B(1, 0);
    auto y11 = MAT_B(1, 1);
    auto y12 = MAT_B(1, 2);

    auto y20 = MAT_B(2, 0);
    auto y21 = MAT_B(2, 1);
    auto y22 = MAT_B(2, 2);

    SECTION("Matrix addition") {
        auto mat_sum = MAT_A + MAT_B;
        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_sum,
            x00 + y00, x01 + y01, x02 + y02,
            x10 + y10, x11 + y11, x12 + y12,
            x20 + y20, x21 + y21, x22 + y22, EPSILON));
        // clang-format on
    }

    SECTION("Matrix substraction") {
        auto mat_sub = MAT_A - MAT_B;
        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_sub,
            x00 - y00, x01 - y01, x02 - y02,
            x10 - y10, x11 - y11, x12 - y12,
            x20 - y20, x21 - y21, x22 - y22, EPSILON));
        // clang-format on
    }

    SECTION("Matrix-Scalar product") {
        auto scale_1 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto scale_2 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);

        auto mat_scaled_1 = scale_1 * MAT_A;
        auto mat_scaled_2 = MAT_B * scale_2;

        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_scaled_1,
            x00 * scale_1, x01 * scale_1, x02 * scale_1,
            x10 * scale_1, x11 * scale_1, x12 * scale_1,
            x20 * scale_1, x21 * scale_1, x22 * scale_1, EPSILON));
        // clang-format on

        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_scaled_2,
            y00 * scale_2, y01 * scale_2, y02 * scale_2,
            y10 * scale_2, y11 * scale_2, y12 * scale_2,
            y20 * scale_2, y21 * scale_2, y22 * scale_2, EPSILON));
        // clang-format on
    }

    SECTION("Matrix-Matrix product") {
        // clang-format off
        // Fixed test-case ---------------------------------------
        Matrix3 m_1(-10.0, -10.0, -2.0,
                     -8.0,  -8.0,  1.0,
                      5.0,  -7.0, -3.0);

        Matrix3 m_2(-1.0, -1.0,  8.0,
                     6.0,  6.0,  0.0,
                    -8.0,  2.0, -9.0);

        auto mat_mul = m_1 * m_2;
        REQUIRE(::math::func_all_close<T>(mat_mul,
            -34.0, -54.0, -62.0,
            -48.0, -38.0, -73.0,
            -23.0, -53.0,  67.0, EPSILON));
        // -------------------------------------------------------
        // clang-format on

        // Test-cases using the random matrices ------------------
        auto mat_mul_ab = MAT_A * MAT_B;
        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_mul_ab,
                // First row
                x00 * y00 + x01 * y10 + x02 * y20,
                x00 * y01 + x01 * y11 + x02 * y21,
                x00 * y02 + x01 * y12 + x02 * y22,
                // Second row
                x10 * y00 + x11 * y10 + x12 * y20,
                x10 * y01 + x11 * y11 + x12 * y21,
                x10 * y02 + x11 * y12 + x12 * y22,
                // Third row
                x20 * y00 + x21 * y10 + x22 * y20,
                x20 * y01 + x21 * y11 + x22 * y21,
                x20 * y02 + x21 * y12 + x22 * y22, EPSILON));
        // clang-format on
        // ------------------------------------------------------
        // @todo(wilbert): test with poorly conditioned matrices
    }

    SECTION("Matrix-Vector product") {
        // clang-format off
        // Fixed test-case --------------------------------------
        Matrix3 mat(1.0, -4.0, 1.0,
                   -6.0, -7.0, 9.0,
                   -4.0,  6.0, 0.0);
        Vector3 vec(2.0, 7.0, 6.0);
        // clang-format on

        auto mat_vec_mul_1 = mat * vec;

        REQUIRE(::math::func_all_close<T>(mat_vec_mul_1, -20.0, -7.0, 34.0,
                                          EPSILON));
        // ------------------------------------------------------

        // Test-cases using the random matrices -----------------
        auto v_a = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec3<T>(RANGE_MIN, RANGE_MAX)));

        auto mat_vec_mul_2 = MAT_A * v_a;

        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_vec_mul_2,
            x00 * v_a.x() + x01 * v_a.y() + x02 * v_a.z(),
            x10 * v_a.x() + x11 * v_a.y() + x12 * v_a.z(),
            x20 * v_a.x() + x21 * v_a.y() + x22 * v_a.z(), EPSILON));
        // clang-format on
        // ------------------------------------------------------
    }

    SECTION("Element-wise matrix product") {
        auto mat_elmwise = math::hadamard(MAT_A, MAT_B);
        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_elmwise,
            x00 * y00, x01 * y01, x02 * y02,
            x10 * y10, x11 * y11, x12 * y12,
            x20 * y20, x21 * y21, x22 * y22, EPSILON));
        // clang-format on
    }

    SECTION("Matrix transposition") {
        // clang-format off
        // NOLINTNEXTLINE
        ::math::func_all_close<T>(math::transpose(MAT_A),
            x00, x10, x20,
            x01, x11, x21,
            x02, x12, x22, EPSILON);
        // NOLINTNEXTLINE
        ::math::func_all_close<T>(math::transpose(MAT_B),
            y00, y10, y20,
            y01, y11, y21,
            y02, y12, y22, EPSILON);
        // clang-format on
    }

    SECTION("Matrix trace") {
        auto calc_trace_1 = math::trace(MAT_A);
        auto calc_trace_2 = math::trace(MAT_B);
        auto expected_trace_1 = x00 + x11 + x22;
        auto expected_trace_2 = y00 + y11 + y22;

        REQUIRE(::math::func_value_close<T>(calc_trace_1, expected_trace_1,
                                            EPSILON));
        REQUIRE(::math::func_value_close<T>(calc_trace_2, expected_trace_2,
                                            EPSILON));
    }

    SECTION("Matrix determinant") {
        // clang-format off
        auto mat = Matrix3(6.0, 5.0, 9.0,
                           0.0, 2.0, 0.0,
                           5.0, 3.0, 6.0);
        // clang-format on
        auto calc_det = math::determinant(mat);
        auto expected_det = static_cast<T>(-18.0);
        REQUIRE(::math::func_value_close<T>(calc_det, expected_det, EPSILON));
    }

    SECTION("Matrix inverse") {
        // clang-format off
        auto mat = Matrix3(6.0, 5.0, 9.0,
                           0.0, 2.0, 0.0,
                           5.0, 3.0, 6.0);
        // clang-format on
        auto inv_mat = math::inverse(mat);
        // clang-format off
        REQUIRE(::math::func_all_close<T>(inv_mat,
            -0.666667,  0.166667,       1.0,
                  0.0,       0.5,       0.0,
             0.555556, -0.388889, -0.666667, EPSILON));
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
