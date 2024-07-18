#include <catch2/catch.hpp>
#include <math/mat4_t.hpp>

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
TEMPLATE_TEST_CASE("Matrix4 class (mat4_t) core operations", "[mat4_t][ops]",
                   ::math::float32_t, ::math::float64_t) {
    using T = TestType;
    using Matrix4 = ::math::Matrix4<T>;
    using Vector4 = ::math::Vector4<T>;

    constexpr T EPSILON = static_cast<T>(USER_EPSILON);
    constexpr T RANGE_MIN = static_cast<T>(USER_RANGE_MIN);
    constexpr T RANGE_MAX = static_cast<T>(USER_RANGE_MAX);

    SECTION("Matrix comparison ==, !=") {
        // clang-format off
        Matrix4 m_1(1.0, 0.0, 0.0, 0.0,
                    0.0, 2.0, 0.0, 0.0,
                    0.0, 0.0, 3.0, 0.0,
                    0.0, 0.0, 0.0, 4.0);
        // clang-format on

        Matrix4 m_2(1.0, 2.0, 3.0, 4.0);
        Matrix4 m_3(1.1, 2.1, 3.1, 4.1);

        REQUIRE(m_1 == m_2);
        REQUIRE(m_2 != m_3);
        REQUIRE(m_3 != m_1);
    }

    // Generate first random matrix
    const auto MAT_A = GENERATE(
        take(NUM_SAMPLES, ::math::random_mat4<T>(RANGE_MIN, RANGE_MAX)));
    // Generate second random matrix
    const auto MAT_B = GENERATE(
        take(NUM_SAMPLES, ::math::random_mat4<T>(RANGE_MIN, RANGE_MAX)));

    // Get a handle of the entries of these matrices
    auto x00 = MAT_A(0, 0);
    auto x01 = MAT_A(0, 1);
    auto x02 = MAT_A(0, 2);
    auto x03 = MAT_A(0, 3);

    auto x10 = MAT_A(1, 0);
    auto x11 = MAT_A(1, 1);
    auto x12 = MAT_A(1, 2);
    auto x13 = MAT_A(1, 3);

    auto x20 = MAT_A(2, 0);
    auto x21 = MAT_A(2, 1);
    auto x22 = MAT_A(2, 2);
    auto x23 = MAT_A(2, 3);

    auto x30 = MAT_A(3, 0);
    auto x31 = MAT_A(3, 1);
    auto x32 = MAT_A(3, 2);
    auto x33 = MAT_A(3, 3);

    auto y00 = MAT_B(0, 0);
    auto y01 = MAT_B(0, 1);
    auto y02 = MAT_B(0, 2);
    auto y03 = MAT_B(0, 3);

    auto y10 = MAT_B(1, 0);
    auto y11 = MAT_B(1, 1);
    auto y12 = MAT_B(1, 2);
    auto y13 = MAT_B(1, 3);

    auto y20 = MAT_B(2, 0);
    auto y21 = MAT_B(2, 1);
    auto y22 = MAT_B(2, 2);
    auto y23 = MAT_B(2, 3);

    auto y30 = MAT_B(3, 0);
    auto y31 = MAT_B(3, 1);
    auto y32 = MAT_B(3, 2);
    auto y33 = MAT_B(3, 3);

    SECTION("Matrix addition") {
        auto mat_sum = MAT_A + MAT_B;
        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_sum,
            x00 + y00, x01 + y01, x02 + y02, x03 + y03,
            x10 + y10, x11 + y11, x12 + y12, x13 + y13,
            x20 + y20, x21 + y21, x22 + y22, x23 + y23,
            x30 + y30, x31 + y31, x32 + y32, x33 + y33, EPSILON));
        // clang-format on
    }
    SECTION("Matrix substraction") {
        auto mat_sub = MAT_A - MAT_B;
        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_sub,
            x00 - y00, x01 - y01, x02 - y02, x03 - y03,
            x10 - y10, x11 - y11, x12 - y12, x13 - y13,
            x20 - y20, x21 - y21, x22 - y22, x23 - y23,
            x30 - y30, x31 - y31, x32 - y32, x33 - y33, EPSILON));
        // clang-format on
    }
    SECTION("Matrix-Scalar product") {
        auto scale_1 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);
        auto scale_2 = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);

        auto mat_scaled_1 = scale_1 * MAT_A;
        auto mat_scaled_2 = MAT_B * scale_2;

        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_scaled_1,
            x00 * scale_1, x01 * scale_1, x02 * scale_1, x03 * scale_1,
            x10 * scale_1, x11 * scale_1, x12 * scale_1, x13 * scale_1,
            x20 * scale_1, x21 * scale_1, x22 * scale_1, x23 * scale_1,
            x30 * scale_1, x31 * scale_1, x32 * scale_1, x33 * scale_1,
            EPSILON));
        // clang-format on

        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_scaled_2,
            y00 * scale_2, y01 * scale_2, y02 * scale_2, y03 * scale_2,
            y10 * scale_2, y11 * scale_2, y12 * scale_2, y13 * scale_2,
            y20 * scale_2, y21 * scale_2, y22 * scale_2, y23 * scale_2,
            y30 * scale_2, y31 * scale_2, y32 * scale_2, y33 * scale_2,
            EPSILON));
        // clang-format on
    }
    SECTION("Matrix-Matrix product") {
        // clang-format off
        // Fixed test-case -------------------------------------
        Matrix4 m_1(-10.0, -6.0, -6.0,  2.0,
                    -8.0,  -6.0, -6.0, -5.0,
                     7.0, -10.0,  5.0,  7.0,
                    -2.0,  -9.0, -8.0,  6.0);

        Matrix4 m_2(7.0,  7.0, -6.0,  3.0,
                   -7.0,  1.0,  8.0,  5.0,
                    7.0, -2.0,  0.0, -4.0,
                   -9.0,  2.0,  5.0, -3.0);

        auto mat_mul = m_1 * m_2;
        REQUIRE(::math::func_all_close<T>(mat_mul,
            -88.0, -60.0,  22.0, -42.0,
            -11.0, -60.0, -25.0, -15.0,
             91.0,  43.0, -87.0, -70.0,
            -61.0,   5.0, -30.0, -37.0, EPSILON));
        // -----------------------------------------------------
        // clang-format on

        // clang-format off
        // Test-cases using the random matrices ----------------
        auto mat_mul_ab = MAT_A * MAT_B;
        REQUIRE(::math::func_all_close<T>(mat_mul_ab,
            // First row
            x00 * y00 + x01 * y10 + x02 * y20 + x03 * y30,
            x00 * y01 + x01 * y11 + x02 * y21 + x03 * y31,
            x00 * y02 + x01 * y12 + x02 * y22 + x03 * y32,
            x00 * y03 + x01 * y13 + x02 * y23 + x03 * y33,
            // Second row
            x10 * y00 + x11 * y10 + x12 * y20 + x13 * y30,
            x10 * y01 + x11 * y11 + x12 * y21 + x13 * y31,
            x10 * y02 + x11 * y12 + x12 * y22 + x13 * y32,
            x10 * y03 + x11 * y13 + x12 * y23 + x13 * y33,
            // Third row
            x20 * y00 + x21 * y10 + x22 * y20 + x23 * y30,
            x20 * y01 + x21 * y11 + x22 * y21 + x23 * y31,
            x20 * y02 + x21 * y12 + x22 * y22 + x23 * y32,
            x20 * y03 + x21 * y13 + x22 * y23 + x23 * y33,
            // Fourth row
            x30 * y00 + x31 * y10 + x32 * y20 + x33 * y30,
            x30 * y01 + x31 * y11 + x32 * y21 + x33 * y31,
            x30 * y02 + x31 * y12 + x32 * y22 + x33 * y32,
            x30 * y03 + x31 * y13 + x32 * y23 + x33 * y33, EPSILON));
        // ----------------------------------------------------
        // clang-format on
        // @todo(wilbert): test with poorly conditioned matrices
    }

    SECTION("Matrix-Vector product") {
        // Fixed test-case --------------------------------------
        // clang-format off
        Matrix4 mat(9.0, 5.0,  9.0,  8.0,
                   -9.0, 1.0, -6.0,  8.0,
                  -10.0, 1.0,  3.0,  6.0,
                   -8.0, 2.0, -2.0, -2.0);
        Vector4 vec(6.0, 7.0, -7.0, 5.0);
        // clang-format on
        auto mat_vec_mul_1 = mat * vec;
        REQUIRE(::math::func_all_close<T>(mat_vec_mul_1, 66.0, 35.0, -44.0,
                                          -30.0, EPSILON));
        // ------------------------------------------------------

        // Test-cases using the random matrices -----------------
        auto v_a = GENERATE(
            take(NUM_SAMPLES, ::math::random_vec4<T>(RANGE_MIN, RANGE_MAX)));

        auto mat_vec_mul_2 = MAT_A * v_a;
        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_vec_mul_2,
             x00 * v_a.x() + x01 * v_a.y() + x02 * v_a.z() + x03 * v_a.w(),
             x10 * v_a.x() + x11 * v_a.y() + x12 * v_a.z() + x13 * v_a.w(),
             x20 * v_a.x() + x21 * v_a.y() + x22 * v_a.z() + x23 * v_a.w(),
             x30 * v_a.x() + x31 * v_a.y() + x32 * v_a.z() + x33 * v_a.w(),
             EPSILON));
        // clang-format on
        // ------------------------------------------------------
    }

    SECTION("Element-wise matrix product") {
        auto mat_elmwise = ::math::hadamard(MAT_A, MAT_B);
        // clang-format off
        REQUIRE(::math::func_all_close<T>(mat_elmwise,
            x00 * y00, x01 * y01, x02 * y02, x03 * y03,
            x10 * y10, x11 * y11, x12 * y12, x13 * y13,
            x20 * y20, x21 * y21, x22 * y22, x23 * y23,
            x30 * y30, x31 * y31, x32 * y32, x33 * y33, EPSILON));
        // clang-format on
    }

    SECTION("Matrix transposition") {
        // clang-format off
        // NOLINTNEXTLINE
        REQUIRE(::math::func_all_close<T>(::math::transpose(MAT_A),
            x00, x10, x20, x30,
            x01, x11, x21, x31,
            x02, x12, x22, x32,
            x03, x13, x23, x33, EPSILON));
        // NOLINTNEXTLINE
        REQUIRE(::math::func_all_close<T>(math::transpose(MAT_B),
            y00, y10, y20, y30,
            y01, y11, y21, y31,
            y02, y12, y22, y32,
            y03, y13, y23, y33, EPSILON));
        // clang-format on
    }

    SECTION("Matrix trace") {
        auto calc_trace_1 = ::math::trace(MAT_A);
        auto calc_trace_2 = ::math::trace(MAT_B);
        auto expected_trace_1 = x00 + x11 + x22 + x33;
        auto expected_trace_2 = y00 + y11 + y22 + y33;

        REQUIRE(::math::func_value_close<T>(calc_trace_1, expected_trace_1,
                                            EPSILON));
        REQUIRE(::math::func_value_close<T>(calc_trace_2, expected_trace_2,
                                            EPSILON));
    }

    SECTION("Matrix determinant") {
        // clang-format off
        auto mat = Matrix4(1.0, 1.0, 6.0, 7.0,
                           0.0, 8.0, 9.0, 7.0,
                           2.0, 7.0, 8.0, 9.0,
                           6.0, 3.0, 4.0, 0.0);
        // clang-format on
        auto calc_det = ::math::determinant(mat);
        auto expected_det = static_cast<T>(885);
        REQUIRE(::math::func_value_close<T>(calc_det, expected_det, EPSILON));
    }

    SECTION("Matrix inverse") {
        // clang-format off
        auto mat = Matrix4(1.0, 1.0, 6.0, 7.0,
                           0.0, 8.0, 9.0, 7.0,
                           2.0, 7.0, 8.0, 9.0,
                           6.0, 3.0, 4.0, 0.0);
        // clang-format on
        auto inv_mat = ::math::inverse(mat);
        // clang-format off
        REQUIRE(::math::func_all_close<T>(inv_mat,
            -0.019209, -0.174011,  0.150282,   0.119774,
            -0.232768, 0.0090395,  0.174011,  -0.019209,
              0.20339,  0.254237, -0.355932,  0.0847458,
           0.00451977,  -0.19435,  0.258757, -0.0870056, EPSILON));
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
