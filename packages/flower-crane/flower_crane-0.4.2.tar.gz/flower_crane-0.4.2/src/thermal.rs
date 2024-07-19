use pyo3::prelude::*;
// Go through the fixes and find the thermals.
// Every point not in a thermal is put into a glide. If we get to end of
// the fixes and there is still an open glide (i.e. flight not finishing
pub fn compute_thermals(
    scoring_windows: Vec<[usize; 2]>,
    circling: &[bool],
    raw_time: &[i64],
    bearing_change_rate: &[f64],
    abs_bearing_change_rate: &[f64],
    min_time_for_thermal: i64,
    min_time_for_glide: i64,
    min_bearing_change_thermal: f64,
    min_abs_bearing_change_thermal: f64,
) -> PyResult<(Vec<[usize; 2]>, Vec<[usize; 2]>)> {
    let mut thermals: Vec<[usize; 2]> = vec![];
    let mut glides: Vec<[usize; 2]> = vec![];

    for window in scoring_windows {
        let [start, stop] = window;
        let mut circling_now = false;
        let mut gliding_now = false;
        let mut already_glide = false;
        let mut first_circling = start;
        let mut first_glide = start;

        for i in start..stop {
            let c = circling[i];
            if !gliding_now && !circling_now && !c {
                // just started scoring window
                gliding_now = true;
                first_glide = i;
                already_glide = true;
            } else if !circling_now && c {
                // Just started circling
                circling_now = true;
                gliding_now = false;
                first_circling = i;
            } else if circling_now && !c {
                // Just ended circling
                circling_now = false;
                gliding_now = true;
                let time_change = raw_time[i] - raw_time[first_circling];
                let total_bearing_change =
                    (bearing_change_rate[first_circling..i].iter().sum::<f64>()
                        * time_change as f64
                        / (i - first_circling) as f64)
                        .abs();

                let total_abs_bearing_change = abs_bearing_change_rate[first_circling..i]
                    .iter()
                    .sum::<f64>()
                    * time_change as f64
                    / (i - first_circling) as f64;

                if already_glide {
                    if time_change >= min_time_for_thermal
                        && (total_bearing_change > min_bearing_change_thermal
                            || total_abs_bearing_change > min_abs_bearing_change_thermal)
                    {
                        let time_change_glide = raw_time[first_circling] - raw_time[first_glide];
                        if time_change_glide >= min_time_for_glide {
                            thermals.push([first_circling, i]);
                            glides.push([first_glide, first_circling]);
                        } else {
                            // glide is too short, extend last thermal
                            // check if there already is a thermal in this scoring window
                            if thermals.last().map(|l| l[0] >= start).unwrap_or(false) {
                                thermals.last_mut().unwrap()[1] = i;
                            } else {
                                thermals.push([first_glide, i])
                            }
                        }
                        first_glide = i;
                    }
                } else {
                    already_glide = true;
                    if time_change >= min_time_for_thermal {
                        thermals.push([first_circling, i]);
                        first_glide = i;
                    } else {
                        first_glide = first_circling;
                    }
                }
            }
        }

        if gliding_now {
            glides.push([first_glide, stop]);
        } else if circling_now {
            let time_change = raw_time[stop] - raw_time[first_circling];
            if time_change >= min_time_for_thermal {
                thermals.push([first_circling, stop]);
                glides.push([first_glide, first_circling]);
            } else {
                glides.push([first_glide, stop]);
            }
        }
    }
    Ok((glides, thermals))
}

#[cfg(test)]
mod tests {
    #[test]
    fn test_compute_thermals() {
        let scoring_windows = vec![[0, 10]];
        let circling = vec![
            false, false, false, true, true, true, false, false, false, false,
        ];
        let raw_time = vec![0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
        let bearing_change_rate = vec![0.0, 90.0, 180.0, 270.0, 0.0, 270.0, 0.0, 0.0, 0.0, 0.0];
        let abs_bearing_change_rate = vec![0.0, 90.0, 180.0, 270.0, 0.0, 270.0, 0.0, 0.0, 0.0, 0.0];
        let min_time_for_thermal = 1;
        let min_time_for_glide = 1;
        let min_bearing_change_thermal = 90.0;
        let min_abs_bearing_change_thermal = 90.0;
        let result = super::compute_thermals(
            scoring_windows,
            &circling,
            &raw_time,
            &bearing_change_rate,
            &abs_bearing_change_rate,
            min_time_for_thermal,
            min_time_for_glide,
            min_bearing_change_thermal,
            min_abs_bearing_change_thermal,
        )
        .unwrap();
        assert_eq!(result, (vec![[0, 3], [6, 10]], vec![[3, 6]]));
    }
}
