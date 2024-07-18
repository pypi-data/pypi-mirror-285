#include <catch2/catch.hpp>
#include <math/utils/geometry_helpers.hpp>

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

TEMPLATE_TEST_CASE("Utilities [Geometric-Helpers]", "[geometric][funcs]",
                   ::math::float32_t, ::math::float64_t) {
    using T = TestType;
    using Vec3 = ::math::Vector3<T>;
    using Line = ::math::Line<T>;
    using Plane = ::math::Plane<T>;
    using AABB = ::math::AABB<T>;
    using Sphere = ::math::Sphere<T>;

    const Vec3 ZERO = {0.0, 0.0, 0.0};
    const Vec3 DIR_X = {1.0, 0.0, 0.0};
    const Vec3 DIR_Y = {0.0, 1.0, 0.0};
    const Vec3 DIR_Z = {0.0, 0.0, 1.0};

    // Line related tests ------------------------------------------------------

    SECTION("Line default constructor") {
        Line line;

        REQUIRE(line.start == ZERO);
        REQUIRE(line.end == ZERO);
    }

    SECTION("Line constructor from points") {
        Line line({1.0, 1.0, 1.0}, {2.0, 3.0, 4.0});

        REQUIRE(line.start == Vec3(1.0, 1.0, 1.0));
        REQUIRE(line.end == Vec3(2.0, 3.0, 4.0));
    }

    SECTION("Line constructor from initializer list") {
        Line line = {{1.0, 1.0, 1.0}, {2.0, 3.0, 4.0}};

        REQUIRE(line.start == Vec3(1.0, 1.0, 1.0));
        REQUIRE(line.end == Vec3(2.0, 3.0, 4.0));
    }

    SECTION("Line distanceTo point func") {
        // Line = x-axis, points = {(1, 0, 0), (0, 1, 0), (0, 0, 1)}
        {
            Line line = {{0.0, 0.0, 0.0}, {1.0, 0.0, 0.0}};
            Vec3 p_a = {1.0, 0.0, 0.0};
            Vec3 p_b = {0.0, 1.0, 0.0};
            Vec3 p_c = {0.0, 0.0, 1.0};

            REQUIRE(std::abs(line.distanceTo(p_a) - 0.0) < 1e-5);
            REQUIRE(std::abs(line.distanceTo(p_b) - 1.0) < 1e-5);
            REQUIRE(std::abs(line.distanceTo(p_c) - 1.0) < 1e-5);
        }
    }

    // Plane related tests -----------------------------------------------------

    SECTION("Plane default constructor") {
        Plane plane;

        REQUIRE(plane.point == ZERO);
        REQUIRE(plane.normal == Vec3(0.0, 0.0, 1.0));
    }

    SECTION("Plane constructor from point and normal") {
        Plane plane({1.0, 1.0, 1.0}, {1.0, 2.0, 3.0});

        REQUIRE(plane.point == Vec3(1.0, 1.0, 1.0));
        REQUIRE(plane.normal == Vec3(1.0, 2.0, 3.0));
    }

    SECTION("Plane distance methods") {
        // Plane XY, point (0, 0, 1), distance=+1
        {
            Plane plane(ZERO, DIR_Z);
            Vec3 point(0.0, 0.0, 1.0);
            constexpr T EXPECTED_DISTANCE = static_cast<T>(1.0);
            constexpr T EXPECTED_SIGNED_DISTANCE = EXPECTED_DISTANCE;
            REQUIRE(std::abs(plane.signedDistanceTo(point) -
                             EXPECTED_SIGNED_DISTANCE) < 1e-5);
            REQUIRE(std::abs(plane.distanceTo(point) - EXPECTED_DISTANCE) <
                    1e-5);
        }

        // Plane XY, point (0, 0, -1), distance=-1
        {
            Plane plane(ZERO, DIR_Z);
            Vec3 point(0.0, 0.0, -1.0);
            constexpr T EXPECTED_DISTANCE = static_cast<T>(1.0);
            constexpr T EXPECTED_SIGNED_DISTANCE = -EXPECTED_DISTANCE;
            REQUIRE(std::abs(plane.signedDistanceTo(point) -
                             EXPECTED_SIGNED_DISTANCE) < 1e-5);
            REQUIRE(std::abs(plane.distanceTo(point) - EXPECTED_DISTANCE) <
                    1e-5);
        }

        // Plane YZ, point (1, 0, 0), distance=+1
        {
            Plane plane(ZERO, DIR_X);
            Vec3 point(1.0, 0.0, 0.0);
            constexpr T EXPECTED_DISTANCE = static_cast<T>(1.0);
            constexpr T EXPECTED_SIGNED_DISTANCE = EXPECTED_DISTANCE;
            REQUIRE(std::abs(plane.signedDistanceTo(point) -
                             EXPECTED_SIGNED_DISTANCE) < 1e-5);
            REQUIRE(std::abs(plane.distanceTo(point) - EXPECTED_DISTANCE) <
                    1e-5);
        }

        // Plane YZ, point (-1, 0, 0), distance=-1
        {
            Plane plane(ZERO, DIR_X);
            Vec3 point(-1.0, 0.0, 0.0);
            constexpr T EXPECTED_DISTANCE = static_cast<T>(1.0);
            constexpr T EXPECTED_SIGNED_DISTANCE = -EXPECTED_DISTANCE;
            REQUIRE(std::abs(plane.signedDistanceTo(point) -
                             EXPECTED_SIGNED_DISTANCE) < 1e-5);
            REQUIRE(std::abs(plane.distanceTo(point) - EXPECTED_DISTANCE) <
                    1e-5);
        }

        // Plane ZX, point (0, 1, 0), distance=+1
        {
            Plane plane(ZERO, DIR_Y);
            Vec3 point(0.0, 1.0, 0.0);
            constexpr T EXPECTED_DISTANCE = static_cast<T>(1.0);
            constexpr T EXPECTED_SIGNED_DISTANCE = EXPECTED_DISTANCE;
            REQUIRE(std::abs(plane.signedDistanceTo(point) -
                             EXPECTED_SIGNED_DISTANCE) < 1e-5);
            REQUIRE(std::abs(plane.distanceTo(point) - EXPECTED_DISTANCE) <
                    1e-5);
        }

        // Plane ZX, point (0, -1, 0), distance=-1
        {
            Plane plane(ZERO, DIR_Y);
            Vec3 point(0.0, -1.0, 0.0);
            constexpr T EXPECTED_DISTANCE = static_cast<T>(1.0);
            constexpr T EXPECTED_SIGNED_DISTANCE = -EXPECTED_DISTANCE;
            REQUIRE(std::abs(plane.signedDistanceTo(point) -
                             EXPECTED_SIGNED_DISTANCE) < 1e-5);
            REQUIRE(std::abs(plane.distanceTo(point) - EXPECTED_DISTANCE) <
                    1e-5);
        }
    }

    SECTION("Plane projection method") {
        // Plane through points (1,0,0), (0,1,0), (0,0,1), Point (0, 0, 0)
        {
            Vec3 p_a(1.0, 0.0, 0.0);
            Vec3 p_b(0.0, 1.0, 0.0);
            Vec3 p_c(0.0, 0.0, 1.0);

            Vec3 p_ab = p_b - p_a;
            Vec3 p_ac = p_c - p_a;
            Vec3 normal = p_ab.cross(p_ac).normalized();

            Plane plane(p_a, normal);
            const Vec3 EXPECTED_PROJECTION(1. / 3., 1. / 3., 1. / 3.);
            REQUIRE(plane.project(ZERO) == EXPECTED_PROJECTION);
        }
    }

    // AABB related tests ------------------------------------------------------

    SECTION("AABB default ctor") {
        AABB bbox;

        REQUIRE(bbox.p_min.x() == -std::numeric_limits<T>::infinity());
        REQUIRE(bbox.p_min.y() == -std::numeric_limits<T>::infinity());
        REQUIRE(bbox.p_min.z() == -std::numeric_limits<T>::infinity());

        REQUIRE(bbox.p_max.x() == std::numeric_limits<T>::infinity());
        REQUIRE(bbox.p_max.y() == std::numeric_limits<T>::infinity());
        REQUIRE(bbox.p_max.z() == std::numeric_limits<T>::infinity());
    }

    SECTION("AABB from args ctor (min,max)") {
        AABB bbox({0.0, 0.0, 0.0}, {1.0, 1.0, 1.0});

        REQUIRE(bbox.p_min == Vec3(0.0, 0.0, 0.0));
        REQUIRE(bbox.p_max == Vec3(1.0, 1.0, 1.0));
    }

    SECTION("AABB method computeCenter") {
        {
            AABB bbox({0.0, 0.0, 0.0}, {1.0, 1.0, 1.0});
            auto center = bbox.computeCenter();
            REQUIRE(center == Vec3(0.5, 0.5, 0.5));
        }

        {
            AABB bbox({-1.0, -1.0, -1.0}, {1.0, 1.0, 1.0});
            auto center = bbox.computeCenter();
            REQUIRE(center == Vec3(0.0, 0.0, 0.0));
        }
    }

    SECTION("AABB method computeCorners") {
        AABB bbox({-1.0, -1.0, -1.0}, {1.0, 1.0, 1.0});
        auto corners = bbox.computeCorners();

        REQUIRE(corners.at(0) == Vec3(-1.0, -1.0, -1.0));
        REQUIRE(corners.at(1) == Vec3(-1.0, -1.0, 1.0));
        REQUIRE(corners.at(2) == Vec3(-1.0, 1.0, -1.0));
        REQUIRE(corners.at(3) == Vec3(-1.0, 1.0, 1.0));
        REQUIRE(corners.at(4) == Vec3(1.0, -1.0, -1.0));
        REQUIRE(corners.at(5) == Vec3(1.0, -1.0, 1.0));
        REQUIRE(corners.at(6) == Vec3(1.0, 1.0, -1.0));
        REQUIRE(corners.at(7) == Vec3(1.0, 1.0, 1.0));
    }

    SECTION("AABB intersects AABB") {
        AABB bbox_a({0.0, 0.0, 0.0}, {2.0, 2.0, 2.0});
        AABB bbox_b({0.0, 1.0, 0.0}, {2.0, 3.0, 2.0});
        AABB bbox_c({0.0, 3.0, 0.0}, {2.0, 5.0, 2.0});

        REQUIRE(bbox_a.intersects(bbox_b));
        REQUIRE(!bbox_a.intersects(bbox_c));
    }

    // Sphere related tests ----------------------------------------------------

    SECTION("Sphere default ctor") {
        Sphere s;

        REQUIRE(s.center == ZERO);
        constexpr auto EXPECTED_RADIUS = static_cast<T>(1.0);
        REQUIRE(std::abs(s.radius - EXPECTED_RADIUS) < 1e-5);
    }

    SECTION("Sphere from args ctor (center, radius)") {
        Sphere s({1.0, 2.0, 3.0}, 2.0);

        REQUIRE(s.center == Vec3(1.0, 2.0, 3.0));
        constexpr auto EXPECTED_RADIUS = static_cast<T>(2.0);
        REQUIRE(std::abs(s.radius - EXPECTED_RADIUS) < 1e-5);
    }

    SECTION("Sphere distanceTo method") {
        /// sphere={(1.0, 1.0, 1.0), 2.0}, point=(2.0, 3.0, 4.0)
        {
            Sphere sph({1.0, 1.0, 1.0}, 2.0);
            Vec3 pt(2.0, 3.0, 4.0);

            constexpr auto EXPECTED_DISTANCE = static_cast<T>(1.7416573867);
            const auto CALCULATED_DISTANCE = sph.distanceTo(pt);
            REQUIRE(std::abs(EXPECTED_DISTANCE - CALCULATED_DISTANCE) < 1e-5);
        }
    }

    SECTION("Sphere contains method") {
        /// sphere={(0.0, 0.0, 0.0), 1.0}, point=ZERO
        {
            Sphere sph(ZERO, 1.0);
            REQUIRE(sph.contains(ZERO));
        }
    }

    SECTION("Sphere intersects method") {
        /// sphere1={ZERO, 1.0}, sphere2={(0.0, 0.0, 1.0), 1.0}
        {
            Sphere sph1(ZERO, 1.0);
            Sphere sph2({0.0, 0.0, 1.0}, 1.0);

            REQUIRE(sph1.intersects(sph2));
        }
    }
}
