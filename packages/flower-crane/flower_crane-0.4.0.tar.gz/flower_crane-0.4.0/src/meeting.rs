use pyo3::prelude::*;

#[allow(clippy::too_many_arguments)]
pub fn find_meeting(
    line1: &[f64],
    line2: &[f64],
    alt1: &[i64],
    alt2: &[i64],
    time1: &[i64],
    time2: &[i64],
    max_dist_degree_squared: f64,
    max_alt_dist: i32,
) -> PyResult<(Vec<i64>, f64)> {
    assert_eq!(time1.len() * 2, line1.len());
    assert_eq!(time1.len(), alt1.len());
    assert_eq!(time2.len() * 2, line2.len());
    assert_eq!(time2.len(), alt2.len());

    //  very simple theta calculation, but we don't need more for short distances
    let theta = (line1[1] * std::f64::consts::PI / 180.0).cos();

    let mut meeting = vec![];
    let mut started = false;
    let mut i = 0;
    let mut min_distance = 10000.0;
    let mut start_time = 0;
    let mut end_time;
    for j in 0..time2.len() {
        // we always expect time1 to be ahead
        while time1[i] < time2[j] && i < time1.len() - 1 {
            i += 1;
        }
        if i == time1.len() - 1 {
            break;
        }
        let dist = ((line1[2 * i] - line2[2 * j]) * theta).powi(2)
            + (line1[2 * i + 1] - line2[2 * j + 1]).powi(2);
        let alt_dist = (alt1[i] as i32 - alt2[j] as i32).abs();
        let same_chunk = time2[(j + 1).min(time2.len() - 1)] - time2[j] < 20;
        if alt_dist < max_alt_dist && dist < max_dist_degree_squared && same_chunk {
            if dist < min_distance {
                min_distance = dist;
            }
            if !started {
                start_time = time1[i];
                started = true;
            } else {
                continue;
            }
        } else if !started {
            continue;
        } else {
            started = false;
            end_time = time1[i];
            if start_time != end_time {
                if meeting.last().map(|l| l == &start_time).unwrap_or(false) {
                    let n = meeting.len() - 1;
                    meeting[n] = end_time;
                } else {
                    meeting.push(start_time);
                    meeting.push(end_time);
                }
            }
        }
    }
    if started {
        end_time = time1[i];
        meeting.push(start_time);
        meeting.push(end_time);
    }
    Ok((meeting, min_distance))
}
