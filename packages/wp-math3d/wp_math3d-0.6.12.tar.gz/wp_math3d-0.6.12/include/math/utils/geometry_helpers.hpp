#pragma once

#include <array>
#include <initializer_list>
#include <limits>
#include <sstream>
#include <string>
#include <utility>

#include <math/vec3_t.hpp>
#include <math/pose3d_t.hpp>

namespace math {

/// \brief Line segment class represented by both start and end points
template <typename T>
struct Line {
    using Vec3 = ::math::Vector3<T>;

    /// \brief Represents the start point of this line
    Vec3 start;
    /// \brief Represents the end point of this line
    Vec3 end;

    /// \brief Creates a default line with both start and end set to the origin
    Line() = default;

    /// \brief Creates a line with given start and end points
    ///
    /// \param p_start The first|starting point of the line
    /// \param p_end The second/ending point of the line
    Line(Vec3 p_start, Vec3 p_end)
        : start(std::move(p_start)), end(std::move(p_end)) {}

    /// \brief Creates a line from a given initializer list of points
    ///
    /// \param points List of points that define the line (start, end)
    Line(const std::initializer_list<Vec3>& points) {
        assert(points.size() == 2);

        auto it = points.begin();
        start = *it++;
        end = *it;
    }

    /// \brief Returns a string representation of this line
    /// \return The string representation of this line
    auto toString() const -> std::string {
        std::stringstream str_result;
        str_result << "<Line"
                   << "\n";
        str_result << "  start: " << start.toString() << "\n";
        str_result << "  end: " << end.toString() << "\n";
        str_result << ">\n";
        return str_result.str();
    }

    /// \brief Returns the distance from the given point to this line
    ///
    /// \param point The point from which to take the distance
    /// \return The distance from the point to this line
    auto distanceTo(const Vec3& point) const -> T {
        const auto SIDE_A = point - start;
        const auto SIDE_B = point - end;
        const auto SIDE_C = end - start;
        auto cross_ab = SIDE_A.cross(SIDE_B);
        auto len_ab = cross_ab.length();
        auto len_c = SIDE_C.length();
        return len_ab / len_c;
    }
};

/// \brief Plane class, represented by both normal and point vectors
template <typename T>
struct Plane {
    using Vec3 = ::math::Vector3<T>;

    /// \brief Represents a point on the plane
    Vec3 point;
    /// \brief Represents the normal vector to the plane
    Vec3 normal;

    /// \brief Creates a default plane representing the XY plane
    Plane() : point({0.0, 0.0, 0.0}), normal({0.0, 0.0, 1.0}) {}

    /// \brief Creates a plane with given normal and point vectors
    ///
    /// \param p_point A point on the plane
    /// \param p_normal The normal to the plane
    Plane(Vec3 p_point, Vec3 p_normal)
        : point(std::move(p_point)), normal(std::move(p_normal)) {}

    /// \brief Returns a string representation of this plane
    auto toString() const -> std::string {
        std::stringstream sstr_result;
        sstr_result << "<Plane\n";
        sstr_result << "  point: " << point.toString() << "\n";
        sstr_result << "  normal: " << normal.toString() << "\n";
        sstr_result << ">\n";
        return sstr_result.str();
    }

    /// \brief Returns the signed distance from a point to this plane
    ///
    /// \details Unlike the distanceTo method, this includes the effect that
    /// the point can have in the result of the required dot-products. This
    /// takes into account where with respect to the normal direction is located
    /// the given point, either the side which the normal is aligned to (result
    /// is positive, or the other side (result is negative)
    ///
    /// \param p_point The point from which to compute the signed distance to
    /// \return The signed distance to this plane (whether aligned to normal)
    auto signedDistanceTo(const Vec3& p_point) const -> T {
        return (p_point - point).dot(normal);
    }

    /// \brief Returns the distance from a point to this plane
    ///
    /// \param point The point from which to compute the distance to
    /// \return The distance from the given point to the plane
    auto distanceTo(const Vec3& p_point) const -> T {
        return std::abs(signedDistanceTo(p_point));
    }

    /// \brief Returns the projection of the given point into the plane
    auto project(const Vec3& p_point) const -> Vec3 {
        // TODO(wilbert): avoid using static_cast for operator*(double, Vec3)
        return p_point -
               static_cast<double>(signedDistanceTo(p_point)) * normal;
    }
};

/// \brief Class representtation of an AABB
template <typename T>
struct AABB {
    using Vec3 = Vector3<T>;

    /// \brief The lower (x, y, z) boundary of this box
    Vec3 p_min = {-std::numeric_limits<T>::infinity(),
                  -std::numeric_limits<T>::infinity(),
                  -std::numeric_limits<T>::infinity()};
    /// \brief The upper (x, y, z) boundary of this box
    Vec3 p_max = {std::numeric_limits<T>::infinity(),
                  std::numeric_limits<T>::infinity(),
                  std::numeric_limits<T>::infinity()};

    /// \brief Creates a default AABB, representing the max possible box
    AABB() = default;

    /// \brief Creates an AABB with given min-max boundary
    ///
    /// \param min The lower boundary point of this box
    /// \param max The upper boundary point of this box
    AABB(const Vec3& min, const Vec3& max) : p_min(min), p_max(max) {}

    /// \brief Returns a string representation of this bounding box
    auto toString() const -> std::string {
        std::stringstream sstr_result;
        sstr_result << "<AABB\n";
        sstr_result << "  min: " << p_min.toString() << "\n";
        sstr_result << "  max: " << p_max.toString() << "\n";
        sstr_result << ">\n";
        return sstr_result.str();
    }

    /// \brief Returns the center of this box
    auto computeCenter() const -> Vec3 { return 0.5 * (p_min + p_max); }

    /// \brief Returns the points on the boundary of thix box (corners)
    auto computeCorners() const -> std::array<Vec3, 8> {
        std::array<Vec3, 8> corners;
        corners[0] = {p_min.x(), p_min.y(), p_min.z()};
        corners[1] = {p_min.x(), p_min.y(), p_max.z()};
        corners[2] = {p_min.x(), p_max.y(), p_min.z()};
        corners[3] = {p_min.x(), p_max.y(), p_max.z()};
        corners[4] = {p_max.x(), p_min.y(), p_min.z()};
        corners[5] = {p_max.x(), p_min.y(), p_max.z()};
        corners[6] = {p_max.x(), p_max.y(), p_min.z()};
        corners[7] = {p_max.x(), p_max.y(), p_max.z()};
        return corners;
    }

    /// \brief Returns whether or not it intersects the given box
    auto intersects(const AABB<T>& other) -> bool {
        return !(other.p_max.x() < this->p_min.x() ||
                 other.p_min.x() > this->p_max.x() ||
                 other.p_max.y() < this->p_min.y() ||
                 other.p_min.y() > this->p_max.y() ||
                 other.p_max.z() < this->p_min.z() ||
                 other.p_min.z() > this->p_max.z());
    }
};

/// \brief Class representing a simple sphere
template <typename T>
struct Sphere {
    using Vec3 = Vector3<T>;

    /// \brief The center of the sphere
    Vec3 center;
    /// \brief The radius of the sphere
    T radius = static_cast<T>(1.0);

    /// \brief Creates a default sphere of radius 1 centered at the origin
    Sphere() = default;

    /// \brief Creates a sphere with the given center and radius
    Sphere(const Vec3& p_center, T p_radius)
        : center(p_center), radius(p_radius) {}

    /// \brief Returns the distance from the given point to the sphere
    auto distanceTo(const Vec3& point) -> T {
        return (point - center).length() - radius;
    }

    /// \brief Returns whether or not the given point is inside the sphere
    auto contains(const Vec3& point) -> bool {
        return (point - center).lengthSquare() <= radius * radius;
    }

    /// |brief Returns whether it intersects with a given sphere
    auto intersects(const Sphere& other) -> bool {
        auto radius_sum = radius + other.radius;
        return (other.center - center).lengthSquare() <=
               radius_sum * radius_sum;
    }
};

}  // namespace math
