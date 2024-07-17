#include <catch2/catch.hpp>
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

constexpr double USER_RANGE_MIN = -10.0;
constexpr double USER_RANGE_MAX = 10.0;
constexpr double USER_EPSILON = 1e-5;

// NOLINTNEXTLINE
TEMPLATE_TEST_CASE("Quaternion class (quat_t) core Operations", "[quat_t][ops]",
                   ::math::float32_t, ::math::float64_t) {
    using T = TestType;
    using Quat = ::math::Quaternion<T>;
    using Vec3 = ::math::Vector3<T>;

    constexpr T EPSILON = static_cast<T>(USER_EPSILON);
    constexpr T RANGE_MIN = static_cast<T>(USER_RANGE_MIN);
    constexpr T RANGE_MAX = static_cast<T>(USER_RANGE_MAX);

    SECTION("Quaternion comparison ==, !=") {
        Quat q_1(4.0, 1.0, 2.0, 3.0);
        Quat q_2(4.0, 1.0, 2.0, 3.0);
        Quat q_3(4.1, 1.1, 2.1, 3.1);

        REQUIRE(q_1 == q_2);
        REQUIRE(q_2 != q_3);
        REQUIRE(q_3 != q_1);
    }

    SECTION("Quaternion addition") {
        constexpr auto NUM_SAMPLES = 10;
        auto q_a = GENERATE(take(NUM_SAMPLES, ::math::random_quaternion<T>()));
        auto q_b = GENERATE(take(NUM_SAMPLES, ::math::random_quaternion<T>()));

        auto q_sum = q_a + q_b;

        // clang-format off
        REQUIRE(::math::func_all_close<T>(q_sum,
            q_a.w() + q_b.w(),
            q_a.x() + q_b.x(),
            q_a.y() + q_b.y(),
            q_a.z() + q_b.z(), EPSILON));
        // clang-format on
    }

    SECTION("Quaternion substraction") {
        constexpr auto NUM_SAMPLES = 10;
        auto q_a = GENERATE(take(NUM_SAMPLES, ::math::random_quaternion<T>()));
        auto q_b = GENERATE(take(NUM_SAMPLES, ::math::random_quaternion<T>()));

        auto q_diff = q_a - q_b;

        // clang-format off
        REQUIRE(::math::func_all_close<T>(q_diff,
            q_a.w() - q_b.w(),
            q_a.x() - q_b.x(),
            q_a.y() - q_b.y(),
            q_a.z() - q_b.z(), EPSILON));
        // clang-format on
    }

    SECTION("Quaternion product") {
        constexpr auto NUM_SAMPLES = 10;
        auto q_a = GENERATE(take(NUM_SAMPLES, ::math::random_quaternion<T>()));
        auto q_b = GENERATE(take(NUM_SAMPLES, ::math::random_quaternion<T>()));

        auto q_prod = q_a * q_b;

        // clang-format off
        REQUIRE(::math::func_all_close<T>(q_prod,
            q_a.w() * q_b.w() - q_a.x() * q_b.x() -
            q_a.y() * q_b.y() - q_a.z() * q_b.z(),
            q_a.w() * q_b.x() + q_b.w() * q_a.x() +
            q_a.y() * q_b.z() - q_b.y() * q_a.z(),
            q_a.w() * q_b.y() + q_b.w() * q_a.y() +
            q_a.z() * q_b.x() - q_b.z() * q_a.x(),
            q_a.w() * q_b.z() + q_b.w() * q_a.z() +
            q_a.x() * q_b.y() - q_b.x() * q_a.y(), EPSILON));
        // clang-format on
    }

    SECTION("Quaternion scale (by single scalar)") {
        constexpr auto NUM_SAMPLES = 10;
        auto q = GENERATE(take(NUM_SAMPLES, ::math::random_quaternion<T>()));
        auto scale = gen_random_value(T, RANGE_MIN, RANGE_MAX, NUM_SAMPLES);

        auto q_1 = scale * q;
        auto q_2 = q * scale;

        // clang-format off
        REQUIRE(::math::func_all_close<T>(q_1,
            q.w() * scale,
            q.x() * scale,
            q.y() * scale,
            q.z() * scale, EPSILON));
        REQUIRE(::math::func_all_close<T>(q_2,
            q.w() * scale,
            q.x() * scale,
            q.y() * scale,
            q.z() * scale, EPSILON));
        // clang-format on
    }

    SECTION("Quaternion length") {
        constexpr auto NUM_SAMPLES = 10;
        auto q = GENERATE(take(NUM_SAMPLES, ::math::random_quaternion<T>()));

        auto length = std::sqrt(q.w() * q.w() + q.x() * q.x() + q.y() * q.y() +
                                q.z() * q.z());
        auto q_length = ::math::norm(q);

        // TODO(wilbert): should check with small generated values as well. Most
        // of the values returned by the generator are quite large (their
        // squares)

        if (::math::IsFloat32<T>::value) {
            // Use larger delta, as we're losing precision quickly on f32
            REQUIRE(::math::func_value_close<T>(q_length, length, 1e-3));
        } else {
            REQUIRE(::math::func_value_close<T>(q_length, length, EPSILON));
        }
    }

    SECTION("Quaternion normalization (in place)") {
        constexpr auto NUM_SAMPLES = 10;
        auto q = GENERATE(take(NUM_SAMPLES, ::math::random_quaternion<T>()));
        // Compute the norm and normalize the quaternion manually
        auto norm = std::sqrt(q.w() * q.w() + q.x() * q.x() + q.y() * q.y() +
                              q.z() * q.z());
        auto val_wnorm = q.w() / norm;
        auto val_xnorm = q.x() / norm;
        auto val_ynorm = q.y() / norm;
        auto val_znorm = q.z() / norm;

        // Normalize the quaternion and make sure it gives the expected result
        ::math::normalize_in_place(q);
        REQUIRE(::math::func_all_close<T>(q, val_wnorm, val_xnorm, val_ynorm,
                                          val_znorm, EPSILON));

        // Make sure the norm of the normalized quaternion is 1.0
        auto q_norm = math::norm(q);
        REQUIRE(::math::func_value_close<T>(q_norm, 1.0, EPSILON));
    }

    SECTION("Quaternion normalization (out-of place)") {
        constexpr auto NUM_SAMPLES = 10;
        auto q = GENERATE(take(NUM_SAMPLES, ::math::random_quaternion<T>()));
        // Compute the norm and normalize the quaternion manually
        auto norm = std::sqrt(q.w() * q.w() + q.x() * q.x() + q.y() * q.y() +
                              q.z() * q.z());
        auto val_wnorm = q.w() / norm;
        auto val_xnorm = q.x() / norm;
        auto val_ynorm = q.y() / norm;
        auto val_znorm = q.z() / norm;

        // Normalize the quaternion and make sure it gives the expected result
        auto qn = ::math::normalize(q);
        REQUIRE(::math::func_all_close<T>(qn, val_wnorm, val_xnorm, val_ynorm,
                                          val_znorm, EPSILON));

        // Make sure the norm of the normalized quaternion is 1.0
        auto qn_norm = ::math::norm(qn);
        REQUIRE(::math::func_value_close<T>(qn_norm, 1.0, EPSILON));
    }

    SECTION("Quaternion conjugate") {
        constexpr auto NUM_SAMPLES = 10;
        auto q = GENERATE(take(NUM_SAMPLES, ::math::random_quaternion<T>()));

        auto q_conj = ::math::conjugate<T>(q);
        REQUIRE(::math::func_all_close<T>(q_conj, q.w(), -q.x(), -q.y(), -q.z(),
                                          EPSILON));
    }

    SECTION("Quaternion inverse") {
        constexpr auto NUM_SAMPLES = 10;
        auto q = GENERATE(take(NUM_SAMPLES, ::math::random_quaternion<T>()));

        auto length_sq =
            q.w() * q.w() + q.x() * q.x() + q.y() * q.y() + q.z() * q.z();
        auto qinv_w = q.w() / length_sq;
        auto qinv_x = -q.x() / length_sq;
        auto qinv_y = -q.y() / length_sq;
        auto qinv_z = -q.z() / length_sq;

        auto q_inv = ::math::inverse<T>(q);
        REQUIRE(::math::func_all_close<T>(q_inv, qinv_w, qinv_x, qinv_y, qinv_z,
                                          EPSILON));
    }

    SECTION("Quaternion as rotations") {
        // Check the rotation of the basis vectors around each of the three axes
        Vec3 vec_i(1.0, 0.0, 0.0);
        Vec3 vec_j(0.0, 1.0, 0.0);
        Vec3 vec_k(0.0, 0.0, 1.0);

        auto q_x = Quat::RotationX(::math::PI / 2.0);
        auto q_y = Quat::RotationY(::math::PI / 2.0);
        auto q_z = Quat::RotationZ(::math::PI / 2.0);

        REQUIRE(vec_j == ::math::rotate<T>(q_z, vec_i));
        REQUIRE(vec_k == ::math::rotate<T>(q_x, vec_j));
        REQUIRE(vec_i == ::math::rotate<T>(q_y, vec_k));
    }
}

#if defined(__clang__)
#pragma clang diagnostic pop  // NOLINT
#elif defined(__GNUC__)
#pragma GCC diagnostic pop
#elif defined(_MSC_VER)
#pragma warning(pop)
#endif
