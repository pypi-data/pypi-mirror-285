# ~~~
# CMake configuration for C++ unittests
# ~~~
if(NOT TARGET math::math)
  loco_message("Unittests require target [math::math], but wasn't found"
               LOG_LEVEL WARNING)
  return()
endif()

if(NOT TARGET Catch2::Catch2)
  loco_message("Unittests require target [Catch2::Catch2], but wasn't found"
               LOG_LEVEL WARNING)
  return()
endif()

include(CTest)
include(Catch)

add_executable(
  MathCppTests
  ${CMAKE_CURRENT_SOURCE_DIR}/test_main.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_vec2_type.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_vec2_operations.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_vec3_type.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_vec3_operations.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_vec4_type.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_vec4_operations.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_mat2_type.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_mat2_operations.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_mat3_type.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_mat3_operations.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_mat4_type.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_mat4_operations.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_quat_type.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_quat_operations.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_euler_type.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_pose3d_type.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_mat2_functions.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_mat3_functions.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_mat4_functions.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_utils_spherical_coordinates.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_geometry_helpers.cpp)
# TODO(wilbert): Making it public to avoid weird issue wirh clangd and LSP
target_link_libraries(MathCppTests PUBLIC math::math Catch2::Catch2)
target_include_directories(MathCppTests PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
# Discover tets and pick an integer as the random seed
catch_discover_tests(MathCppTests)
