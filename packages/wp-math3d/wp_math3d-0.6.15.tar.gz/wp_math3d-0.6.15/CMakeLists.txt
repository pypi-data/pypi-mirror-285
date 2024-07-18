cmake_minimum_required(VERSION 3.15 FATAL_ERROR)

# -------------------------------------
# Get loco_cmake to help us configure our CMake based project
include(FetchContent)
FetchContent_Declare(
  loco_cmake
  GIT_REPOSITORY https://github.com/wpumacay/loco_cmake.git
  GIT_TAG 0270626101bec01dbf9ae7f1b5febfb82092bf0c # Version v0.1.5
  GIT_PROGRESS FALSE
  GIT_SHALLOW TRUE)
FetchContent_MakeAvailable(loco_cmake)
include(${loco_cmake_SOURCE_DIR}/Index.cmake)

# -------------------------------------
# Define our project :)
project(
  math3d
  VERSION 0.6.15
  DESCRIPTION "A basic math library for spatial algebra"
  HOMEPAGE_URL "https://github.com/wpumacay/math"
  LANGUAGES C CXX)

# -------------------------------------
# Define some options the user can set before|while configuring the project
option(MATH_BUILD_SSE "Build using SSE SIMD-extensions support" ON)
option(MATH_BUILD_AVX "Build using AVX SIMD-extensions support" ON)
option(MATH_BUILD_FORCE_INLINE "Build with inlining when requested" OFF)
option(MATH_BUILD_PYTHON_BINDINGS "Build bindings (requires Pybind11)" ON)
option(MATH_BUILD_DOCS "Build documentation (requires Doxygen+Breathe)" OFF)
option(MATH_BUILD_TESTS "Build C++ unit-tests (requires Catch2)" ON)
option(MATH_BUILD_EXAMPLES "Build C++ examples" ON)

# cmake-format: off
set(MATH_BUILD_CXX_STANDARD 17 CACHE STRING "The C++ standard to be used")
set_property(CACHE MATH_BUILD_CXX_STANDARD PROPERTY STRINGS 11 14 17 20)
# cmake-format: on

# -------------------------------------
# Initialize the project using our helper modules :D
loco_initialize_project(CXX_STANDARD ${MATH_BUILD_CXX_STANDARD})

# -------------------------------------
# Allow the usage of our helper macros and functions
list(APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake")

# -------------------------------------
# Bring our dependencies accordingly
include(MathDependencies)

# cmake-format: off
# -------------------------------------
# Setup the main C++ target `MathCpp`
loco_create_target(MathCpp INTERFACE
  SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/common.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/vec2_t_decl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/vec2_t.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/vec3_t_decl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/vec3_t.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/vec4_t_decl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/vec4_t.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/quat_t_decl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/quat_t.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/mat2_t_decl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/mat2_t.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/mat3_t_decl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/mat3_t.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/mat4_t_decl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/mat4_t.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/pose3d_t_decl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/vec2_t_scalar_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/vec2_t_sse_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/vec3_t_scalar_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/vec3_t_sse_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/vec3_t_avx_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/vec4_t_scalar_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/vec4_t_sse_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/vec4_t_avx_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/quat_t_scalar_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/quat_t_sse_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/quat_t_avx_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/mat2_t_scalar_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/mat2_t_sse_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/mat2_t_avx_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/mat3_t_scalar_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/mat3_t_sse_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/mat3_t_avx_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/mat4_t_scalar_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/mat4_t_sse_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/impl/mat4_t_avx_impl.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/utils/spherical_coordinates.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/math/utils/geometry_helpers.hpp
  INCLUDE_DIRECTORIES
    ${CMAKE_CURRENT_SOURCE_DIR}/include
  WARNINGS_AS_ERRORS
    FALSE
  ENABLE_SSE
    ${MATH_BUILD_SSE}
  ENABLE_AVX
    ${MATH_BUILD_AVX}
  CXX_STANDARD
    ${MATH_BUILD_CXX_STANDARD}
)
# cmake-format: on

# -------------------------------------
# If force-inline is being requested, then add it to the target
if(MATH_BUILD_FORCE_INLINE)
  # @todo(wilbert): Move this to one of the setup helpers on the loco-cmake repo
  target_compile_definitions(MathCpp INTERFACE -DMATH_FORCE_INLINE)
endif()

# -------------------------------------
# Expose an alias for the library (CMake namespace convention)
add_library(math::math ALIAS MathCpp)

# -------------------------------------
# Add C++ examples to the build process
if(MATH_BUILD_EXAMPLES)
  add_subdirectory(examples/cpp)
endif()

# -------------------------------------
# Add C++ tests to the build process
if(MATH_BUILD_TESTS)
  add_subdirectory(tests/cpp)
endif()

# HACK: Add the conversions headers directly, without exposing target math_py
target_include_directories(
  MathCpp INTERFACE ${PROJECT_SOURCE_DIR}/python/math3d/bindings/)
# -------------------------------------
# Add Python bindings to the build process
if(MATH_BUILD_PYTHON_BINDINGS)
  add_subdirectory(python/math3d/bindings)
endif()

# -------------------------------------
# Build the required documentation accordingly
if(MATH_BUILD_DOCS)
  # cmake-format: off
  # -------------------------------------
  # Setup documentation for our target
  loco_setup_cppdocs(MathCpp
    DOXYGEN_FILE_IN ${CMAKE_CURRENT_SOURCE_DIR}/docs/Doxyfile.in
    DOXYGEN_OUTPUT_DIR ${CMAKE_CURRENT_BINARY_DIR}/docs/Doxygen
    DOXYGEN_GENERATE_HTML FALSE
    DOXYGEN_GENERATE_LATEX FALSE
    DOXYGEN_GENERATE_XML TRUE
    DOXYGEN_QUIET TRUE
    SPHINX_FILE_IN ${CMAKE_CURRENT_SOURCE_DIR}/docs/conf.py.in
    SPHINX_OUTPUT_DIR ${CMAKE_CURRENT_BINARY_DIR}/docs/Sphinx
    SPHINX_BREATHE_PROJECT MathCpp
    SPHINX_DOXYGEN_XML_OUTDIR ${CMAKE_CURRENT_BINARY_DIR}/docs/Doxygen/xml)
  # cmake-format: on
endif()

# -------------------------------------
# Show the properties of our main target
loco_print_target_properties(MathCpp)

# -------------------------------------
# Show some info of the this project
loco_print_project_info()
