# ~~~
# CMake configuration rules used to generate Python Bindings via Pybind11
# ~~~
if(NOT TARGET math::math)
  loco_message("Bindings require the math::math target" LOG_LEVEL WARNING)
  return()
endif()

pybind11_add_module(math3d_bindings ${CMAKE_CURRENT_SOURCE_DIR}/bindings_py.cpp
                    ${CMAKE_CURRENT_SOURCE_DIR}/conversions_py.cpp)
target_include_directories(math3d_bindings PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(math3d_bindings PRIVATE math::math)

add_library(math_py_helpers INTERFACE)
target_include_directories(math_py_helpers
                           INTERFACE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(math_py_helpers INTERFACE math::math)

add_library(math::math_py_helpers ALIAS math_py_helpers)
