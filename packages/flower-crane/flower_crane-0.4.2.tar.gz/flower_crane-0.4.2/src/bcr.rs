use pyo3::prelude::*;

// Computing bearing change rate between neighboring fixes proved
// itself to be noisy on tracks recorded with minimum interval (1 second).
// Therefore we compute rates between points that are at least
// min_time_for_bearing_change seconds apart.
pub fn bearing_change_rate(bearing: &[f64], raw_time: &[i64], ratio: i64) -> PyResult<Vec<f64>> {
    let mut bearing_change_rate = vec![0.0; raw_time.len()];
    for cur_fix in 0..raw_time.len() {
        let prev_fix = cur_fix as i64 - ratio;
        if prev_fix >= 0 {
            let mut bearing_change = bearing[prev_fix as usize] - bearing[cur_fix];
            if bearing_change < -180.0 {
                bearing_change += 360.0
            }
            if bearing_change > 180.0 {
                bearing_change -= 360.0
            }
            let time_change = raw_time[prev_fix as usize] - raw_time[cur_fix];
            bearing_change_rate[cur_fix] = bearing_change / time_change as f64;
        }
    }
    Ok(bearing_change_rate)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_bearing_change_rate() {
        let bearing = vec![0.0, 90.0, 180.0, 270.0, 0.0, 270.0, 0.0];
        let raw_time = vec![0, 1, 2, 3, 4, 5, 6];
        let ratio = 1;
        let result = bearing_change_rate(&bearing, &raw_time, ratio).unwrap();
        assert_eq!(result, vec![0.0, 90.0, 90.0, 90.0, 90.0, -90.0, 90.0]);
    }
}
