#include <cmath>
#include <random>

#include <catch2/catch.hpp>
#include <math/pose3d_t.hpp>

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

// NOLINTNEXTLINE
TEMPLATE_TEST_CASE("Pose3d class (pose3d_t) constructors",
                   "[pose3d_t][template]", ::math::float32_t,
                   ::math::float64_t) {
    using T = TestType;
    using Pose = ::math::Pose3d<T>;
    using Quat = ::math::Quaternion<T>;
    using Mat3 = ::math::Matrix3<T>;
    using Vec3 = ::math::Vector3<T>;

    SECTION("Default constructor") {
        Pose X;  // NOLINT
        REQUIRE(X.position == Vec3(0.0, 0.0, 0.0));
        REQUIRE(X.orientation == Quat(1.0, 0.0, 0.0, 0.0));
    }

    SECTION("From position(Vec3) and orientation(Quat)") {
        auto position = GENERATE(take(10, ::math::random_vec3<T>(-10.0, 10.0)));
        auto orientation = GENERATE(take(10, ::math::random_quaternion<T>()));

        Pose X(position, orientation);  // NOLINT
        // Position should be copied directly to the pose object
        REQUIRE(X.position == position);
        // Orientation normalized to ensure it represents a rotation
        REQUIRE(std::abs(X.orientation.length() - 1.0) < 1e-5);
    }

    SECTION("From position(Vec3) and rotation matrix(Mat3)") {
        auto position = GENERATE(take(4, ::math::random_vec3<T>(-10.0, 10.0)));
        auto angle =
            GENERATE(take(4, random(-::math::PI / 2.0, ::math::PI / 2.0)));

        SECTION("Using an x-axis rotation matrix") {
            auto rotmat = Mat3::RotationX(angle);
            Pose X(position, rotmat);  // NOLINT
            // Position should be copied directly to the pose object
            REQUIRE(X.position == position);
            // Orientation is transformed internally into a unit quaternion
            REQUIRE(std::abs(X.orientation.length() - 1.0) < 1e-5);
            // Make sure that our orientation is (as created above) a rotation
            // quaternion around the x axis
            REQUIRE(X.orientation == Quat::RotationX(angle));
        }

        SECTION("Using a y-axis rotation matrix") {
            auto rotmat = Mat3::RotationY(angle);
            Pose X(position, rotmat);  // NOLINT
            // Position should be copied directly to the pose object
            REQUIRE(X.position == position);
            // Orientation is transformed internally into a unit quaternion
            REQUIRE(std::abs(X.orientation.length() - 1.0) < 1e-5);
            // Make sure that our orientation is (as created above) a rotation
            // quaternion around the y axis
            REQUIRE(X.orientation == Quat::RotationY(angle));
        }

        SECTION("Using a z-axis rotation matrix") {
            auto rotmat = Mat3::RotationZ(angle);
            Pose X(position, rotmat);  // NOLINT
            // Position should be copied directly to the pose object
            REQUIRE(X.position == position);
            // Orientation is transformed internally into a unit quaternion
            REQUIRE(std::abs(X.orientation.length() - 1.0) < 1e-5);
            // Make sure that our orientation is (as created above) a rotation
            // quaternion around the z axis
            REQUIRE(X.orientation == Quat::RotationZ(angle));
        }
    }

    SECTION("From position(Vec3) and Euler angles(Euler)") {
        auto position = GENERATE(take(4, ::math::random_vec3<T>(-10.0, 10.0)));
        auto euler = GENERATE(take(4, ::math::random_euler<T>()));
        Pose X(position, euler);  // NOLINT
        // Position should be copied directly to the pose object
        REQUIRE(X.position == position);
        // Orientation is transformed internally into a unit quaternion
        REQUIRE(std::abs(X.orientation.length() - 1.0) < 1e-5);
    }

    SECTION("From matrix transform(Mat4)") {
        auto tf = GENERATE(take(4, ::math::random_transform_mat4<T>()));
        Pose X(tf);  // NOLINT
        // Position should be copied directly to the pose object
        REQUIRE(X.position == Vec3(tf[3]));
        // Orientation is transformed internally into a unit quaternion
        REQUIRE(std::abs(X.orientation.length() - 1.0) < 1e-5);
    }
}

// NOLINTNEXTLINE
TEMPLATE_TEST_CASE("Pose3d class (pose3d_t) API", "[pose3d_t][template]",
                   ::math::float32_t, ::math::float64_t) {
    using T = TestType;
    using Pose = ::math::Pose3d<T>;
    using Quat = ::math::Quaternion<T>;
    using Mat3 = ::math::Matrix3<T>;
    using Vec3 = ::math::Vector3<T>;

    SECTION("'Apply' method (transform a vec3)") {
        // Point B in A = (1.0, 1.0, 1.0)
        // X of A in W = {pos=(-3.0, 0.0, 0.0), rot=quat_rot_z(PI / 2)}
        // Point B in W = (-4.0, 1.0, 1.0)
        {
            // NOLINTNEXTLINE
            Vec3 p_BA(1.0, 1.0, 1.0);
            // NOLINTNEXTLINE
            Pose X_AW(Vec3(-3.0, 0.0, 0.0), Quat::RotationZ(::math::PI / 2.0));
            // NOLINTNEXTLINE
            auto p_BW = X_AW.apply(p_BA);

            REQUIRE(p_BW == Vec3(-4.0, 1.0, 1.0));
        }

        // Point C in B = (1.0, 1.0, 1.0)
        // X of B in A = {pos(0.0, 5.0, 0.0), rot=quat_rot_x(PI / 2)}
        // Point C in A = (1.0, 6.0, -1.0)
        // X of A in W = {pos(0.0, 5.0, 0.0), rot=quat_rot_y(PI / 2)}
        // Point C in W = (1.0, 6.0, 6.0)
        {
            // NOLINTNEXTLINE
            Vec3 p_CB(1.0, 1.0, 1.0);
            // NOLINTNEXTLINE
            Pose X_BA(Vec3(0.0, 5.0, 0.0), Quat::RotationY(::math::PI / 2.0));
            // NOLINTNEXTLINE
            auto p_CA = X_BA.apply(p_CB);
            REQUIRE(p_CA == Vec3(1.0, 6.0, -1.0));

            // NOLINTNEXTLINE
            Pose X_AW(Vec3(0.0, 5.0, 0.0), Quat::RotationX(::math::PI / 2.0));
            // NOLINTNEXTLINE
            auto p_CW = X_AW.apply(p_CA);
            REQUIRE(p_CW == Vec3(1.0, 6.0, 6.0));
        }
    }

    SECTION("'Inverse' method (inverts the transform)") {
        // X of A in W = {pos=(0.0, 3.0, 0.0), rot=quat_rot_x(PI / 2)}
        // X of W in A = (pos=(0.0, 0.0, 3.0), rot=quat_rot_x(-PI / 2))
        {
            // NOLINTNEXTLINE
            Pose X_AW(Vec3(0.0, 3.0, 0.0), Quat::RotationX(::math::PI / 2.0));
            // NOLINTNEXTLINE
            auto X_WA = X_AW.inverse();

            REQUIRE(X_WA.position == Vec3(0.0, 0.0, 3.0));
            REQUIRE(X_WA.orientation == Quat::RotationX(-::math::PI / 2.0));
        }
    }

    SECTION("'Operator *' method (compounds transforms)") {
        // Point C in B = (1.0, 1.0, 1.0)
        // X of B in A = {pos(0.0, 5.0, 0.0), rot=quat_rot_x(PI / 2)}
        // Point C in A = (1.0, 6.0, -1.0)
        // X of A in W = {pos(0.0, 5.0, 0.0), rot=quat_rot_y(PI / 2)}
        // Point C in W = (1.0, 6.0, 6.0)
        // X of B in W = X_AW * X_BA = ...
        // ... {pos(0.0, 5.0, 5.0), rot=quat_rot_x(PI / 2) * quat_rot_y(PI / 2)}
        {
            // NOLINTNEXTLINE
            Vec3 p_CB(1.0, 1.0, 1.0);
            // NOLINTNEXTLINE
            Pose X_BA(Vec3(0.0, 5.0, 0.0), Quat::RotationY(::math::PI / 2.0));
            // NOLINTNEXTLINE
            Pose X_AW(Vec3(0.0, 5.0, 0.0), Quat::RotationX(::math::PI / 2.0));
            // NOLINTNEXTLINE
            auto X_BW = X_AW * X_BA;
            REQUIRE(X_BW.position == Vec3(0.0, 5.0, 5.0));
            REQUIRE(X_BW.orientation == Quat::RotationX(::math::PI / 2.0) *
                                            Quat::RotationY(::math::PI / 2.0));

            // NOLINTNEXTLINE
            auto p_CW = X_BW.apply(p_CB);
            REQUIRE(p_CW == Vec3(1.0, 6.0, 6.0));
        }
    }

    SECTION("'toMatrix' method (converts pose to 4x4 transform matrix)") {
        // NOLINTNEXTLINE
        Pose X(Vec3(0.0, 5.0, 0.0), Quat::RotationX(::math::PI / 2.0));
        auto tf_mat = X.toMatrix();
        // Position should be at last column
        REQUIRE(Vec3(tf_mat[3]) == Vec3(0.0, 5.0, 0.0));
        // Rotation matrix should be the upper-left 3x3 matrix
        REQUIRE(Mat3(tf_mat) == Mat3::RotationX(::math::PI / 2.0));
    }

    SECTION("'Operator*' method (transforms a given vector)") {
        // Should behave the same as the 'apply' method.

        // Point B in A = (1.0, 1.0, 1.0)
        // X of A in W = {pos=(-3.0, 0.0, 0.0), rot=quat_rot_z(PI / 2)}
        // Point B in W = (-4.0, 1.0, 1.0)
        {
            // NOLINTNEXTLINE
            Vec3 p_BA(1.0, 1.0, 1.0);
            // NOLINTNEXTLINE
            Pose X_AW(Vec3(-3.0, 0.0, 0.0), Quat::RotationZ(::math::PI / 2.0));
            // NOLINTNEXTLINE
            auto p_BW = X_AW * p_BA;

            REQUIRE(p_BW == Vec3(-4.0, 1.0, 1.0));
        }

        // Point C in B = (1.0, 1.0, 1.0)
        // X of B in A = {pos(0.0, 5.0, 0.0), rot=quat_rot_x(PI / 2)}
        // Point C in A = (1.0, 6.0, -1.0)
        // X of A in W = {pos(0.0, 5.0, 0.0), rot=quat_rot_y(PI / 2)}
        // Point C in W = (1.0, 6.0, 6.0)
        {
            // NOLINTNEXTLINE
            Pose X_BA(Vec3(0.0, 5.0, 0.0), Quat::RotationY(::math::PI / 2.0));
            // NOLINTNEXTLINE
            Pose X_AW(Vec3(0.0, 5.0, 0.0), Quat::RotationX(::math::PI / 2.0));

            // NOLINTNEXTLINE
            Vec3 p_CB(1.0, 1.0, 1.0);
            // NOLINTNEXTLINE
            auto p_CA = X_BA * p_CB;
            REQUIRE(p_CA == Vec3(1.0, 6.0, -1.0));
            // NOLINTNEXTLINE
            auto p_CW = X_AW * X_BA * p_CB;
            REQUIRE(p_CW == Vec3(1.0, 6.0, 6.0));
        }
    }
}

#if defined(__clang__)
#pragma clang diagnostic pop  // NOLINT
#elif defined(__GNUC__)
#pragma GCC diagnostic pop
#elif defined(_MSC_VER)
#pragma warning(pop)
#endif
