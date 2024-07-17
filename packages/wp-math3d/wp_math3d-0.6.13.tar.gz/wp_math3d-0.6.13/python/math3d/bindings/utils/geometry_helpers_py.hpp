#pragma once

#include <memory>
#include <utility>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include <math/utils/geometry_helpers.hpp>

#include "../conversions_py.hpp"

namespace py = pybind11;

namespace math {

template <typename T>
using SFINAE_LINE_BINDINGS = typename std::enable_if<IsScalar<T>::value>::type*;

template <typename T, SFINAE_LINE_BINDINGS<T> = nullptr>
// NOLINTNEXTLINE
auto bindings_utils_line(py::module& m, const char* class_name) -> void {
    using Line = ::math::Line<T>;
    using Vec3 = ::math::Vector3<T>;
    py::class_<Line>(m, class_name)
        .def(py::init<>())
        .def(py::init<Vec3, Vec3>())
        .def(py::init([](const py::array_t<T>& np_start,
                         const py::array_t<T>& np_end) -> Line {
            return Line(nparray_to_vec3<T>(np_start),
                        nparray_to_vec3<T>(np_end));
        }))
        .def_readwrite("start", &Line::start)
        .def_readwrite("end", &Line::end)
        .def("distanceTo",
             [](const Line& self, const Vec3& point) -> T {
                 return self.distanceTo(point);
             })
        .def("distanceTo",
             [](const Line& self, const py::array_t<T>& np_point) -> T {
                 return self.distanceTo(nparray_to_vec3<T>(np_point));
             })
        .def("__repr__", [](const Line& self) -> py::str {
            return py::str(self.toString());
        });
}

template <typename T>
using SFINAE_PLANE_BINDINGS =
    typename std::enable_if<IsScalar<T>::value>::type*;

template <typename T, SFINAE_PLANE_BINDINGS<T> = nullptr>
// NOLINTNEXTLINE
auto bindings_utils_plane(py::module& m, const char* class_name) -> void {
    using Plane = ::math::Plane<T>;
    using Vec3 = ::math::Vector3<T>;
    py::class_<Plane>(m, class_name)
        .def(py::init<>())
        .def(py::init<Vec3, Vec3>())
        .def(py::init([](const py::array_t<T>& np_point,
                         const py::array_t<T>& np_normal) -> Plane {
            return Plane(::math::nparray_to_vec3<T>(np_point),
                         ::math::nparray_to_vec3<T>(np_normal));
        }))
        .def_readwrite("point", &Plane::point)
        .def_readwrite("normal", &Plane::normal)
        .def("signedDistanceTo",
             [](const Plane& self, const Vec3& point) -> T {
                 return self.signedDistanceTo(point);
             })
        .def("signedDistanceTo",
             [](const Plane& self, const py::array_t<T>& np_point) -> T {
                 return self.signedDistanceTo(
                     ::math::nparray_to_vec3<T>(np_point));
             })
        .def("distanceTo",
             [](const Plane& self, const Vec3& point) -> T {
                 return self.distanceTo(point);
             })
        .def("distanceTo",
             [](const Plane& self, const py::array_t<T>& np_point) -> T {
                 return self.distanceTo(::math::nparray_to_vec3<T>(np_point));
             })
        .def("project",
             [](const Plane& self, const Vec3& point) -> Vec3 {
                 return self.project(point);
             })
        .def("project",
             [](const Plane& self,
                const py::array_t<T>& np_point) -> py::array_t<T> {
                 return ::math::vec3_to_nparray<T>(
                     self.project(::math::nparray_to_vec3<T>(np_point)));
             })
        .def("__repr__", [](const Plane& self) -> py::str {
            return py::str(self.toString());
        });
}

template <typename T>
using SFINAE_AABB_BINDINGS = typename std::enable_if<IsScalar<T>::value>::type*;

template <typename T>
// NOLINTNEXTLINE
auto bindings_utils_aabb(py::module& m, const char* class_name) -> void {
    using AABB = ::math::AABB<T>;
    using Vec3 = ::math::Vector3<T>;
    py::class_<AABB>(m, class_name)
        .def(py::init<>())
        .def(py::init<Vec3, Vec3>())
        .def(py::init([](const py::array_t<T>& np_min,
                         const py::array_t<T>& np_max) -> AABB {
            return AABB(::math::nparray_to_vec3<T>(np_min),
                        ::math::nparray_to_vec3<T>(np_max));
        }))
        .def_readwrite("min", &AABB::p_min)
        .def_readwrite("max", &AABB::p_max)
        .def("computeCenter", &AABB::computeCenter)
        .def("computeCorners", &AABB::computeCorners)
        .def("intersects", &AABB::intersects)
        .def("__repr__", [](const AABB& self) -> py::str {
            return py::str(self.toString());
        });
}

}  // namespace math
