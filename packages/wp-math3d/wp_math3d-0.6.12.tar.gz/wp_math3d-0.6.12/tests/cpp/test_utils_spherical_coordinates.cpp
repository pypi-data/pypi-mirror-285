#include <catch2/catch.hpp>
#include <math/utils/spherical_coordinates.hpp>

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
TEMPLATE_TEST_CASE("Utilities [Spherical-Coordinates]", "[sph_coords][funcs]",
                   math::float32_t, math::float64_t) {
    using T = TestType;
    constexpr auto EPSILON = static_cast<T>(math::EPS);

    SECTION("SphericalCoords::SetFromCartesian") {
        math::SphericalCoords<T> sph_coords;

        // (x=1, y=0, z=0) -> (rho=1, theta=0, phi=pi/2)
        {
            sph_coords.SetFromCartesian(1.0, 0.0, 0.0);
            // Expected values for spherical coordinates
            auto exp_rho = static_cast<T>(1.0);
            auto exp_theta = static_cast<T>(0.0);
            auto exp_phi = static_cast<T>(math::PI / 2.0);
            REQUIRE(std::abs(sph_coords.rho - exp_rho) < EPSILON);
            REQUIRE(std::abs(sph_coords.theta - exp_theta) < EPSILON);
            REQUIRE(std::abs(sph_coords.phi - exp_phi) < EPSILON);
        }

        // (x=0, y=1, z=0) -> (rho=1, theta=pi/2, phi=pi/2)
        {
            sph_coords.SetFromCartesian(0.0, 1.0, 0.0);
            // Expected values for spherical coordinates
            auto exp_rho = static_cast<T>(1.0);
            auto exp_theta = static_cast<T>(math::PI / 2.0);
            auto exp_phi = static_cast<T>(math::PI / 2.0);
            REQUIRE(std::abs(sph_coords.rho - exp_rho) < EPSILON);
            REQUIRE(std::abs(sph_coords.theta - exp_theta) < EPSILON);
            REQUIRE(std::abs(sph_coords.phi - exp_phi) < EPSILON);
        }

        // (x=-1, y=0, z=0) -> (rho=1, theta=pi, phi=pi/2)
        {
            sph_coords.SetFromCartesian(-1.0, 0.0, 0.0);
            // Expected values for spherical coordinates
            auto exp_rho = static_cast<T>(1.0);
            auto exp_theta = static_cast<T>(math::PI);
            auto exp_phi = static_cast<T>(math::PI / 2.0);
            REQUIRE(std::abs(sph_coords.rho - exp_rho) < EPSILON);
            REQUIRE(std::abs(sph_coords.theta - exp_theta) < EPSILON);
            REQUIRE(std::abs(sph_coords.phi - exp_phi) < EPSILON);
        }

        // (x=0, y=-1, z=0) -> (rho=1, theta=-pi/2, phi=pi/2)
        {
            sph_coords.SetFromCartesian(0.0, -1.0, 0.0);
            // Expected values for spherical coordinates
            auto exp_rho = static_cast<T>(1.0);
            auto exp_theta = static_cast<T>(-math::PI / 2.0);
            auto exp_phi = static_cast<T>(math::PI / 2.0);
            REQUIRE(std::abs(sph_coords.rho - exp_rho) < EPSILON);
            REQUIRE(std::abs(sph_coords.theta - exp_theta) < EPSILON);
            REQUIRE(std::abs(sph_coords.phi - exp_phi) < EPSILON);
        }
    }

    SECTION("SphericalCoords::GetCartesian") {}
}

#if defined(__clang__)
#pragma clang diagnostic pop  // NOLINT
#elif defined(__GNUC__)
#pragma GCC diagnostic pop
#elif defined(_MSC_VER)
#pragma warning(pop)
#endif
