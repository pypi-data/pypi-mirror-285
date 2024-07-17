#include <conversions_py.hpp>

namespace math {

auto bindings_conversions_functions(py::module m) -> void {
    m.def("quat_to_nparray_f32", ::math::quat_to_nparray<::math::float32_t>);
    m.def("quat_to_nparray_f64", ::math::quat_to_nparray<::math::float64_t>);
    m.def("vec2_to_nparray_f32", ::math::vec2_to_nparray<::math::float32_t>);
    m.def("vec2_to_nparray_f64", ::math::vec2_to_nparray<::math::float64_t>);
    m.def("vec3_to_nparray_f32", ::math::vec3_to_nparray<::math::float32_t>);
    m.def("vec3_to_nparray_f64", ::math::vec3_to_nparray<::math::float64_t>);
    m.def("vec4_to_nparray_f32", ::math::vec4_to_nparray<::math::float32_t>);
    m.def("vec4_to_nparray_f64", ::math::vec4_to_nparray<::math::float64_t>);
    m.def("mat2_to_nparray_f32", ::math::mat2_to_nparray<::math::float32_t>);
    m.def("mat2_to_nparray_f64", ::math::mat2_to_nparray<::math::float64_t>);
    m.def("mat3_to_nparray_f32", ::math::mat3_to_nparray<::math::float32_t>);
    m.def("mat3_to_nparray_f64", ::math::mat3_to_nparray<::math::float64_t>);
    m.def("mat4_to_nparray_f32", ::math::mat4_to_nparray<::math::float32_t>);
    m.def("mat4_to_nparray_f64", ::math::mat4_to_nparray<::math::float64_t>);

    m.def("nparray_to_quat_f32", ::math::nparray_to_quat<::math::float32_t>);
    m.def("nparray_to_quat_f64", ::math::nparray_to_quat<::math::float64_t>);
    m.def("nparray_to_vec2_f32", ::math::nparray_to_vec2<::math::float32_t>);
    m.def("nparray_to_vec2_f64", ::math::nparray_to_vec2<::math::float64_t>);
    m.def("nparray_to_vec3_f32", ::math::nparray_to_vec3<::math::float32_t>);
    m.def("nparray_to_vec3_f64", ::math::nparray_to_vec3<::math::float64_t>);
    m.def("nparray_to_vec4_f32", ::math::nparray_to_vec4<::math::float32_t>);
    m.def("nparray_to_vec4_f64", ::math::nparray_to_vec4<::math::float64_t>);
    m.def("nparray_to_mat2_f32", ::math::nparray_to_mat2<::math::float32_t>);
    m.def("nparray_to_mat2_f64", ::math::nparray_to_mat2<::math::float64_t>);
    m.def("nparray_to_mat3_f32", ::math::nparray_to_mat3<::math::float32_t>);
    m.def("nparray_to_mat3_f64", ::math::nparray_to_mat3<::math::float64_t>);
    m.def("nparray_to_mat4_f32", ::math::nparray_to_mat4<::math::float32_t>);
    m.def("nparray_to_mat4_f64", ::math::nparray_to_mat4<::math::float64_t>);
}

}  // namespace math
