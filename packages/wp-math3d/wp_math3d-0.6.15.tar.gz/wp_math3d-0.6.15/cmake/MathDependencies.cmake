# ~~~
# CMake configuration for third-party dependencies.
#
# Dependencies:
# * pybind11
# * catch2
#
# - Based on the superbuild script by jeffamstutz for ospray
#   https://github.com/jeffamstutz/superbuild_ospray/blob/main/macros.cmake
# - Based on MuJoCo's helper find_or_fetch content macro
#   https://github.com/deepmind/mujoco/blob/main/cmake/FindOrFetch.cmake
# ~~~

set(MATH_DEP_VERSION_catch2
    182c910b4b63ff587a3440e08f84f70497e49a81 # Release 2.13.10
    CACHE STRING "Version of Catch2 to be fetched (used for unittests)")

set(MATH_DEP_VERSION_pybind11
    8a099e44b3d5f85b20f05828d919d2332a8de841 # Release v2.11.1
    CACHE STRING "Version of PyBind11 to be fetched (used for python bindings)")

mark_as_advanced(MATH_DEP_VERSION_catch2)
mark_as_advanced(MATH_DEP_VERSION_pybind11)

# cmake-format: off
# ------------------------------------------------------------------------------
# Catch2 is used for generating unittests for our C++ codebase
# ------------------------------------------------------------------------------

set(CATCH_INSTALL_DOCS OFF CACHE BOOL "" FORCE)
set(CATCH_INSTALL_EXTRAS OFF CACHE BOOL "" FORCE)
set(CATCH_DEVELOPMENT_BUILD OFF CACHE BOOL "" FORCE)

loco_find_or_fetch_dependency(
  USE_SYSTEM_PACKAGE FALSE
  PACKAGE_NAME Catch2
  LIBRARY_NAME catch2
  GIT_REPO https://github.com/catchorg/Catch2.git
  GIT_TAG ${MATH_DEP_VERSION_catch2}
  GIT_PROGRESS FALSE
  GIT_SHALLOW TRUE
  TARGETS Catch2::Catch2
  EXCLUDE_FROM_ALL)

# Add custom scripts for test-case registration to the module path
if (catch2_POPULATED)
  list(APPEND CMAKE_MODULE_PATH "${catch2_SOURCE_DIR}/contrib")
endif()

# ------------------------------------------------------------------------------
# Pybind11 is used for generating Python bindings for this project's C++ API.
# Notice that we're using a forked version in which usage of unique-ptr is
# allowed, as we use this functionality in some other parent projects
# ------------------------------------------------------------------------------

set(PYBIND11_TEST OFF CACHE BOOL "" FORCE)

loco_find_or_fetch_dependency(
  USE_SYSTEM_PACKAGE FALSE
  PACKAGE_NAME pybind11
  LIBRARY_NAME pybind11
  GIT_REPO https://github.com/pybind/pybind11.git
  GIT_TAG ${MATH_DEP_VERSION_pybind11}
  GIT_PROGRESS FALSE
  GIT_SHALLOW TRUE
  TARGETS pybind11::headers
  EXCLUDE_FROM_ALL)

# cmake-format: on
