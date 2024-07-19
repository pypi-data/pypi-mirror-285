use argmax::arg_max_positive_diff;
use bcr::bearing_change_rate;
use filter::filter;
use meeting::find_meeting;
use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;
use thermal::compute_thermals;
use time_limit::apply_time_limit;
use viterbi::viterbi_decode;

mod argmax;
mod bcr;
mod filter;
mod meeting;
mod thermal;
mod time_limit;
mod viterbi;

#[pymodule]
fn flower_crane(_py: Python, m: &PyModule) -> PyResult<()> {
    #[pyfn(m)]
    #[pyo3(name = "viterbi_decode")]
    fn viterbi_decode_py(
        init_probs: [f64; 2],
        transition_probs: [[f64; 2]; 2],
        emissions: PyReadonlyArray1<'_, f64>,
    ) -> PyResult<Vec<usize>> {
        viterbi_decode(init_probs, transition_probs, emissions.as_slice().unwrap())
    }

    #[pyfn(m)]
    #[pyo3(name = "compute_thermals")]
    fn compute_thermals_py<'py>(
        scoring_windows: Vec<[usize; 2]>,
        circling: PyReadonlyArray1<'py, bool>,
        raw_time: PyReadonlyArray1<'py, i64>,
        bearing_change_rate: PyReadonlyArray1<'py, f64>,
        abs_bearing_change_rate: PyReadonlyArray1<'py, f64>,
        min_time_for_thermal: i64,
        min_time_for_glide: i64,
        min_bearing_change_thermal: f64,
        min_abs_bearing_change_thermal: f64,
    ) -> PyResult<(Vec<[usize; 2]>, Vec<[usize; 2]>)> {
        compute_thermals(
            scoring_windows,
            circling.as_slice().unwrap(),
            raw_time.as_slice().unwrap(),
            bearing_change_rate.as_slice().unwrap(),
            abs_bearing_change_rate.as_slice().unwrap(),
            min_time_for_thermal,
            min_time_for_glide,
            min_bearing_change_thermal,
            min_abs_bearing_change_thermal,
        )
    }

    #[pyfn(m)]
    #[pyo3(name = "apply_time_limit")]
    fn apply_time_limit_py<'py>(
        array: PyReadonlyArray1<'py, bool>,
        raw_time: PyReadonlyArray1<'py, i64>,
        min_time: i64,
        base_state: bool,
    ) -> PyResult<Vec<bool>> {
        apply_time_limit(
            array.as_slice().unwrap(),
            raw_time.as_slice().unwrap(),
            min_time,
            base_state,
        )
    }

    #[pyfn(m)]
    #[pyo3(name = "bearing_change_rate")]
    fn bearing_change_rate_py<'py>(
        bearing: PyReadonlyArray1<'py, f64>,
        time: PyReadonlyArray1<'py, i64>,
        ratio: i64,
    ) -> PyResult<Vec<f64>> {
        bearing_change_rate(bearing.as_slice().unwrap(), time.as_slice().unwrap(), ratio)
    }
    #[pyfn(m)]
    #[pyo3(name = "arg_max_positive_diff")]
    fn arg_max_positive_diff_py(
        array: PyReadonlyArray1<'_, i64>,
    ) -> PyResult<Option<(usize, usize)>> {
        arg_max_positive_diff(array.as_slice().unwrap())
    }
    #[allow(clippy::too_many_arguments)]
    #[pyfn(m)]
    #[pyo3(name = "find_meeting")]
    fn find_meeting_py<'py>(
        line1: PyReadonlyArray2<'py, f64>,
        line2: PyReadonlyArray2<'py, f64>,
        alt1: PyReadonlyArray1<'py, i64>,
        alt2: PyReadonlyArray1<'py, i64>,
        time1: PyReadonlyArray1<'py, i64>,
        time2: PyReadonlyArray1<'py, i64>,
        max_dist_degree_squared: f64,
        max_alt_dist: i32,
    ) -> PyResult<(Vec<i64>, f64)> {
        find_meeting(
            line1.as_slice().unwrap(),
            line2.as_slice().unwrap(),
            alt1.as_slice().unwrap(),
            alt2.as_slice().unwrap(),
            time1.as_slice().unwrap(),
            time2.as_slice().unwrap(),
            max_dist_degree_squared,
            max_alt_dist,
        )
    }
    #[pyfn(m)]
    #[pyo3(name = "filter")]
    fn filter_py(
        data: PyReadonlyArray1<'_, f64>,
        allowed_offset: f64,
    ) -> PyResult<(Vec<f64>, usize)> {
        filter(data.as_slice().unwrap(), allowed_offset)
    }
    Ok(())
}
