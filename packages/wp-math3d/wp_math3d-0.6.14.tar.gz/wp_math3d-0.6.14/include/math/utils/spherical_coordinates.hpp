#pragma once

// Adapted from ThreeJS Spherical Coordinates helper
// https://github.com/mrdoob/three.js/blob/dev/src/math/Spherical.js
//
// The convention we use is different to the one used by three.js, as we usually
// deal with physics simulations that define the up direction as Z. Moreover, we
// will make use of the convention used in mathematics, which defines the polar
// angle "phi" as the angle between the positive Z-axis and the defined line
// segment OP, and the azimuthal angle "theta" as the angle between the positive
// X-axis and the projection of the line segment OP into the XY plane

#include <cmath>
#include <string>
#include <initializer_list>

#include <math/common.hpp>
#include <math/vec3_t_decl.hpp>

#define CLAMP(x, min_x, max_x) std::max(std::min(x, max_x), min_x)

namespace math {

template <typename T>
class SphericalCoords {
 public:
    SphericalCoords() = default;

    explicit SphericalCoords(T p_rho, T p_theta, T p_phi)
        : rho(p_rho), theta(p_theta), phi(p_phi) {}

    auto SetFromCartesian(const Vector3<T>& vec) -> void {
        SetFromCartesian(vec.x(), vec.y(), vec.z());
    }

    auto SetFromCartesian(T x, T y, T z) -> void {
        rho = std::sqrt(x * x + y * y + z * z);
        constexpr auto EPS_RADIUS = static_cast<T>(1e-10);
        if (rho < EPS_RADIUS) {
            theta = static_cast<T>(0.0);
            phi = static_cast<T>(0.0);
        } else {
            theta = std::atan2(y, x);
            constexpr auto MIN_RATIO = static_cast<T>(-1.0);
            constexpr auto MAX_RATIO = static_cast<T>(1.0);
            phi = std::acos(CLAMP(z / rho, MIN_RATIO, MAX_RATIO));
        }
    }

    auto GetCartesian() const -> Vector3<T> {
        const auto sin_theta = std::sin(theta);  // NOLINT
        const auto cos_theta = std::cos(theta);  // NOLINT
        const auto sin_phi = std::sin(phi);      // NOLINT
        const auto cos_phi = std::cos(phi);      // NOLINT

        auto x = rho * cos_theta * sin_phi;
        auto y = rho * sin_theta * sin_phi;
        auto z = rho * cos_phi;

        return {x, y, z};
    }

    auto MakeSafe() -> void {
        // Restrict phi to be between EPS and PI-EPS
        constexpr auto MIN_PHI = static_cast<T>(math::EPS);
        constexpr auto MAX_PHI = static_cast<T>(math::PI - math::EPS);
        phi = CLAMP(phi, MIN_PHI, MAX_PHI);
    }

    /// The distance from the origin to the end point
    T rho = static_cast<T>(0.0);
    /// The polar angle (measured w.r.t. the positive Z-axis)
    T phi = static_cast<T>(0.0);
    /// The azimuthal angle (measured w.r.t. the positive X-axis)
    T theta = static_cast<T>(0.0);
};

}  // namespace math
