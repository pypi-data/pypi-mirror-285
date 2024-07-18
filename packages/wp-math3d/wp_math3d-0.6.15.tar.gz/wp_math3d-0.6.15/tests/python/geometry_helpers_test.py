from typing import Type, Union, cast

import numpy as np
import pytest
from numpy.typing import NDArray

import math3d as m3d

LineCls = Type[Union[m3d.Line_f, m3d.Line_d]]
PlaneCls = Type[Union[m3d.Plane_f, m3d.Plane_d]]
AABBCls = Type[Union[m3d.AABB_f, m3d.AABB_d]]
Vector3Cls = Type[Union[m3d.Vector3f, m3d.Vector3d]]

Vector3 = Union[m3d.Vector3f, m3d.Vector3d]

# Make sure our generators are seeded with the answer to the universe :D
np.random.seed(42)
# The delta used for tolerance (due to floating point precision mismatches)
EPSILON = 1e-5


def vec3_all_close(
    vec: Vector3, vec_np: NDArray, epsilon: float = EPSILON
) -> bool:
    return np.allclose(cast(NDArray, vec), vec_np, atol=epsilon)


# Tests for Line type ----------------------------------------------------------


@pytest.mark.parametrize("Line", [(m3d.Line_f), (m3d.Line_d)])
def test_line_attrs(Line: LineCls) -> None:
    assert hasattr(Line, "start") and hasattr(Line, "end")


@pytest.mark.parametrize(
    "Line, FloatType", [(m3d.Line_f, np.float32), (m3d.Line_d, np.float64)]
)
def test_line_ctor_default(Line: LineCls, FloatType: type) -> None:
    line = Line()

    assert vec3_all_close(line.start, np.zeros((3,)).astype(FloatType))
    assert vec3_all_close(line.end, np.zeros((3,)).astype(FloatType))


@pytest.mark.parametrize(
    "Line, Vec3, FloatType",
    [
        (m3d.Line_f, m3d.Vector3f, np.float32),
        (m3d.Line_d, m3d.Vector3f, np.float64),
    ],
)
def test_line_ctor_vec_args(
    Line: LineCls, Vec3: Vector3Cls, FloatType: type
) -> None:
    v_start = Vec3(1.0, 1.0, 1.0)
    v_end = Vec3(2.0, 3.0, 4.0)
    line = Line(v_start, v_end)

    assert vec3_all_close(
        line.start, np.array([1.0, 1.0, 1.0], dtype=FloatType)
    )
    assert vec3_all_close(line.end, np.array([2.0, 3.0, 4.0], dtype=FloatType))


@pytest.mark.parametrize(
    "Line, FloatType", [(m3d.Line_f, np.float32), (m3d.Line_d, np.float64)]
)
def test_line_ctor_npvec_args(Line: LineCls, FloatType: type) -> None:
    np_start = np.array([1.0, 1.0, 1.0], dtype=FloatType)
    np_end = np.array([2.0, 3.0, 4.0], dtype=FloatType)
    line = Line(np_start, np_end)

    assert vec3_all_close(line.start, np_start)
    assert vec3_all_close(line.end, np_end)


@pytest.mark.parametrize(
    "Line, Vec3", [(m3d.Line_f, m3d.Vector3f), (m3d.Line_d, m3d.Vector3f)]
)
def test_line_distanceTo_method(Line: LineCls, Vec3: Vector3Cls) -> None:
    # Line = x-axis, points = {(1, 0, 0), (0, 1, 0), (0, 0, 1)}
    line = Line([0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
    p_a = Vec3(1.0, 0.0, 0.0)
    p_b = Vec3(0.0, 1.0, 0.0)
    p_c = Vec3(0.0, 0.0, 1.0)

    assert np.abs(line.distanceTo(p_a) - 0.0) < EPSILON
    assert np.abs(line.distanceTo(p_b) - 1.0) < EPSILON
    assert np.abs(line.distanceTo(p_c) - 1.0) < EPSILON


@pytest.mark.parametrize(
    "Line, FloatType", [(m3d.Line_f, np.float32), (m3d.Line_d, np.float64)]
)
def test_line_distanceTo_method_npargs(Line: LineCls, FloatType: type) -> None:
    # Line = x-axis, points = {(1, 0, 0), (0, 1, 0), (0, 0, 1)}
    line = Line([0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
    p_a = np.array([1.0, 0.0, 0.0], dtype=FloatType)
    p_b = np.array([0.0, 1.0, 0.0], dtype=FloatType)
    p_c = np.array([0.0, 0.0, 1.0], dtype=FloatType)

    assert np.abs(line.distanceTo(p_a) - 0.0) < EPSILON
    assert np.abs(line.distanceTo(p_b) - 1.0) < EPSILON
    assert np.abs(line.distanceTo(p_c) - 1.0) < EPSILON


# Tests for Plane type ---------------------------------------------------------


@pytest.mark.parametrize("Plane", [(m3d.Plane_f), (m3d.Plane_d)])
def test_plane_attrs(Plane: PlaneCls) -> None:
    assert hasattr(Plane, "point") and hasattr(Plane, "normal")


@pytest.mark.parametrize(
    "Plane, FloatType", [(m3d.Plane_f, np.float32), (m3d.Plane_d, np.float64)]
)
def test_plane_ctor_default(Plane: PlaneCls, FloatType: type) -> None:
    plane = Plane()

    assert vec3_all_close(
        plane.point, np.array([0.0, 0.0, 0.0], dtype=FloatType)
    )
    assert vec3_all_close(
        plane.normal, np.array([0.0, 0.0, 1.0], dtype=FloatType)
    )


@pytest.mark.parametrize(
    "Plane, Vec3, FloatType",
    [
        (m3d.Plane_f, m3d.Vector3f, np.float32),
        (m3d.Plane_d, m3d.Vector3d, np.float64),
    ],
)
def test_plane_ctor_vec_args(
    Plane: PlaneCls, Vec3: Vector3Cls, FloatType: type
) -> None:
    v_point = Vec3(1.0, 1.0, 1.0)
    v_normal = Vec3(1.0, 2.0, 3.0)
    plane = Plane(v_point, v_normal)

    assert vec3_all_close(
        plane.point, np.array([1.0, 1.0, 1.0], dtype=FloatType)
    )
    assert vec3_all_close(
        plane.normal, np.array([1.0, 2.0, 3.0], dtype=FloatType)
    )


@pytest.mark.parametrize(
    "Plane, FloatType", [(m3d.Plane_f, np.float32), (m3d.Plane_d, np.float64)]
)
def test_plane_ctor_npvec_args(Plane: PlaneCls, FloatType: type) -> None:
    np_point = np.array([1.0, 1.0, 1.0], dtype=FloatType)
    np_normal = np.array([1.0, 2.0, 3.0], dtype=FloatType)
    plane = Plane(np_point, np_normal)

    assert vec3_all_close(plane.point, np_point)
    assert vec3_all_close(plane.normal, np_normal)


@pytest.mark.parametrize(
    "Plane, Vec3, FloatType",
    [
        (m3d.Plane_f, m3d.Vector3f, np.float32),
        (m3d.Plane_d, m3d.Vector3d, np.float64),
    ],
)
def test_plane_distance_methods(
    Plane: PlaneCls, Vec3: Vector3Cls, FloatType: type
) -> None:
    ZERO = np.array([0.0, 0.0, 0.0], dtype=FloatType)
    DIR_X = np.array([1.0, 0.0, 0.0], dtype=FloatType)
    DIR_Y = np.array([0.0, 1.0, 0.0], dtype=FloatType)
    DIR_Z = np.array([0.0, 0.0, 1.0], dtype=FloatType)

    # Plane XY, point (0, 0, 1), distance=+1 -------------------
    plane = Plane(ZERO, DIR_Z)
    v_point = Vec3(0.0, 0.0, 1.0)
    np_point = np.array([0.0, 0.0, 1.0], dtype=FloatType)
    EXPECTED_DISTANCE = 1.0
    EXPECTED_SIGNED_DISTANCE = EXPECTED_DISTANCE

    assert (
        np.abs(plane.signedDistanceTo(v_point) - EXPECTED_SIGNED_DISTANCE)
        < EPSILON
    )
    assert (
        np.abs(plane.signedDistanceTo(np_point) - EXPECTED_SIGNED_DISTANCE)
        < EPSILON
    )
    assert np.abs(plane.distanceTo(v_point) - EXPECTED_DISTANCE) < EPSILON
    assert np.abs(plane.distanceTo(np_point) - EXPECTED_DISTANCE) < EPSILON
    # ----------------------------------------------------------

    # Plane XY, point (0, 0, -1), distance=-1 ------------------
    plane = Plane(ZERO, DIR_Z)
    v_point = Vec3(0.0, 0.0, -1.0)
    np_point = np.array([0.0, 0.0, -1.0], dtype=FloatType)
    EXPECTED_DISTANCE = 1
    EXPECTED_SIGNED_DISTANCE = -EXPECTED_DISTANCE

    assert (
        np.abs(plane.signedDistanceTo(v_point) - EXPECTED_SIGNED_DISTANCE)
        < EPSILON
    )
    assert (
        np.abs(plane.signedDistanceTo(np_point) - EXPECTED_SIGNED_DISTANCE)
        < EPSILON
    )
    assert np.abs(plane.distanceTo(v_point) - EXPECTED_DISTANCE) < EPSILON
    assert np.abs(plane.distanceTo(np_point) - EXPECTED_DISTANCE) < EPSILON
    # ----------------------------------------------------------

    # Plane YZ, point (1, 0, 0), distance=+1 -------------------
    plane = Plane(ZERO, DIR_X)
    v_point = Vec3(1.0, 0.0, 0.0)
    np_point = np.array([1.0, 0.0, 0.0], dtype=FloatType)
    EXPECTED_DISTANCE = 1
    EXPECTED_SIGNED_DISTANCE = EXPECTED_DISTANCE

    assert (
        np.abs(plane.signedDistanceTo(v_point) - EXPECTED_SIGNED_DISTANCE)
        < EPSILON
    )
    assert (
        np.abs(plane.signedDistanceTo(np_point) - EXPECTED_SIGNED_DISTANCE)
        < EPSILON
    )
    assert np.abs(plane.distanceTo(v_point) - EXPECTED_DISTANCE) < EPSILON
    assert np.abs(plane.distanceTo(np_point) - EXPECTED_DISTANCE) < EPSILON
    # ----------------------------------------------------------

    # Plane YZ, point (-1, 0, 0), distance=-1 ------------------
    plane = Plane(ZERO, DIR_X)
    v_point = Vec3(-1.0, 0.0, 0.0)
    np_point = np.array([-1.0, 0.0, 0.0], dtype=FloatType)
    EXPECTED_DISTANCE = 1
    EXPECTED_SIGNED_DISTANCE = -EXPECTED_DISTANCE

    assert (
        np.abs(plane.signedDistanceTo(v_point) - EXPECTED_SIGNED_DISTANCE)
        < EPSILON
    )
    assert (
        np.abs(plane.signedDistanceTo(np_point) - EXPECTED_SIGNED_DISTANCE)
        < EPSILON
    )
    assert np.abs(plane.distanceTo(v_point) - EXPECTED_DISTANCE) < EPSILON
    assert np.abs(plane.distanceTo(np_point) - EXPECTED_DISTANCE) < EPSILON
    # ----------------------------------------------------------

    # Plane ZX, point (0, 1, 0), distance=+1 -------------------
    plane = Plane(ZERO, DIR_Y)
    v_point = Vec3(0.0, 1.0, 0.0)
    np_point = np.array([0.0, 1.0, 0.0], dtype=FloatType)
    EXPECTED_DISTANCE = 1
    EXPECTED_SIGNED_DISTANCE = EXPECTED_DISTANCE

    assert (
        np.abs(plane.signedDistanceTo(v_point) - EXPECTED_SIGNED_DISTANCE)
        < EPSILON
    )
    assert (
        np.abs(plane.signedDistanceTo(np_point) - EXPECTED_SIGNED_DISTANCE)
        < EPSILON
    )
    assert np.abs(plane.distanceTo(v_point) - EXPECTED_DISTANCE) < EPSILON
    assert np.abs(plane.distanceTo(np_point) - EXPECTED_DISTANCE) < EPSILON
    # ----------------------------------------------------------

    # Plane ZX, point (0, -1, 0), distance=-1 ------------------
    plane = Plane(ZERO, DIR_Y)
    v_point = Vec3(0.0, -1.0, 0.0)
    np_point = np.array([0.0, -1.0, 0.0], dtype=FloatType)
    EXPECTED_DISTANCE = 1
    EXPECTED_SIGNED_DISTANCE = -EXPECTED_DISTANCE

    assert (
        np.abs(plane.signedDistanceTo(v_point) - EXPECTED_SIGNED_DISTANCE)
        < EPSILON
    )
    assert (
        np.abs(plane.signedDistanceTo(np_point) - EXPECTED_SIGNED_DISTANCE)
        < EPSILON
    )
    assert np.abs(plane.distanceTo(v_point) - EXPECTED_DISTANCE) < EPSILON
    assert np.abs(plane.distanceTo(np_point) - EXPECTED_DISTANCE) < EPSILON
    # ----------------------------------------------------------


@pytest.mark.parametrize(
    "Plane, Vec3, FloatType",
    [
        (m3d.Plane_f, m3d.Vector3f, np.float32),
        (m3d.Plane_d, m3d.Vector3d, np.float64),
    ],
)
def test_plane_project_method_vec_args(
    Plane: PlaneCls, Vec3: Vector3Cls, FloatType: type
) -> None:
    # Plane through points (1,0,0), (0,1,0), (0,0,1), Point (0, 0, 0) ----------
    ZERO = Vec3(0.0, 0.0, 0.0)
    vec_a = Vec3(1.0, 0.0, 0.0)
    vec_b = Vec3(0.0, 1.0, 0.0)
    vec_c = Vec3(0.0, 0.0, 1.0)

    vec_ab = vec_b - vec_a
    vec_ac = vec_c - vec_a
    vec_normal = vec_ab.cross(vec_ac).normalize()

    plane = Plane(vec_a, vec_normal)
    EXPECTED_PROJECTION = Vec3(1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)
    assert plane.project(ZERO) == EXPECTED_PROJECTION


@pytest.mark.parametrize(
    "Plane, Vec3, FloatType",
    [
        (m3d.Plane_f, m3d.Vector3f, np.float32),
        (m3d.Plane_d, m3d.Vector3d, np.float64),
    ],
)
def test_plane_project_method_np_args(
    Plane: PlaneCls, Vec3: Vector3Cls, FloatType: type
) -> None:
    # Plane through points (1,0,0), (0,1,0), (0,0,1), Point (0, 0, 0) ----------
    ZERO = np.array([0.0, 0.0, 0.0], dtype=FloatType)
    vec_a = np.array([1.0, 0.0, 0.0], dtype=FloatType)
    vec_b = np.array([0.0, 1.0, 0.0], dtype=FloatType)
    vec_c = np.array([0.0, 0.0, 1.0], dtype=FloatType)

    vec_ab = vec_b - vec_a
    vec_ac = vec_c - vec_a
    vec_normal = np.cross(vec_ab, vec_ac)
    vec_normal = vec_normal / np.linalg.norm(vec_normal)

    plane = Plane(vec_a, vec_normal)
    EXPECTED_PROJECTION = np.array(
        [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0], dtype=FloatType
    )
    assert np.allclose(plane.project(ZERO), EXPECTED_PROJECTION, atol=EPSILON)


# Tests for AABB type ----------------------------------------------------------


@pytest.mark.parametrize("AABB", [(m3d.AABB_f), (m3d.AABB_d)])
def test_aabb_attrs(AABB: AABBCls) -> None:
    assert hasattr(AABB, "min") and hasattr(AABB, "max")


@pytest.mark.parametrize(
    "AABB, FloatType", [(m3d.AABB_f, np.float32), (m3d.AABB_d, np.float64)]
)
def test_aabb_default_ctor(AABB: AABBCls, FloatType: type) -> None:
    bbox = AABB()

    assert vec3_all_close(
        bbox.min, np.array([-np.inf, -np.inf, -np.inf], dtype=FloatType)
    )
    assert vec3_all_close(
        bbox.max, np.array([np.inf, np.inf, np.inf], dtype=FloatType)
    )


@pytest.mark.parametrize(
    "AABB, FloatType", [(m3d.AABB_f, np.float32), (m3d.AABB_d, np.float64)]
)
def test_aabb_from_args_min_max(AABB: AABBCls, FloatType: type) -> None:
    bbox = AABB([0.0, 0.0, 0.0], [1.0, 1.0, 1.0])

    assert vec3_all_close(bbox.min, np.array([0.0, 0.0, 0.0], dtype=FloatType))
    assert vec3_all_close(bbox.max, np.array([1.0, 1.0, 1.0], dtype=FloatType))


@pytest.mark.parametrize(
    "AABB, FloatType", [(m3d.AABB_f, np.float32), (m3d.AABB_d, np.float64)]
)
def test_aabb_method_computeCenter(AABB: AABBCls, FloatType: type) -> None:
    bbox = AABB([0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
    center = bbox.computeCenter()
    EXPECTED_CENTER = np.array([0.5, 0.5, 0.5], dtype=FloatType)

    assert vec3_all_close(center, EXPECTED_CENTER)

    bbox = AABB([-1.0, -1.0, -1.0], [1.0, 1.0, 1.0])
    center = bbox.computeCenter()
    EXPECTED_CENTER = np.array([0.0, 0.0, 0.0], dtype=FloatType)

    assert vec3_all_close(center, EXPECTED_CENTER)


@pytest.mark.parametrize(
    "AABB, FloatType", [(m3d.AABB_f, np.float32), (m3d.AABB_d, np.float64)]
)
def test_aabb_method_computeCorners(AABB: AABBCls, FloatType: type) -> None:
    bbox = AABB([-1.0, -1.0, -1.0], [1.0, 1.0, 1.0])
    corners = bbox.computeCorners()

    assert vec3_all_close(
        corners[0], np.array([-1.0, -1.0, -1.0], dtype=FloatType)
    )
    assert vec3_all_close(
        corners[1], np.array([-1.0, -1.0, 1.0], dtype=FloatType)
    )
    assert vec3_all_close(
        corners[2], np.array([-1.0, 1.0, -1.0], dtype=FloatType)
    )
    assert vec3_all_close(
        corners[3], np.array([-1.0, 1.0, 1.0], dtype=FloatType)
    )
    assert vec3_all_close(
        corners[4], np.array([1.0, -1.0, -1.0], dtype=FloatType)
    )
    assert vec3_all_close(
        corners[5], np.array([1.0, -1.0, 1.0], dtype=FloatType)
    )
    assert vec3_all_close(
        corners[6], np.array([1.0, 1.0, -1.0], dtype=FloatType)
    )
    assert vec3_all_close(
        corners[7], np.array([1.0, 1.0, 1.0], dtype=FloatType)
    )
