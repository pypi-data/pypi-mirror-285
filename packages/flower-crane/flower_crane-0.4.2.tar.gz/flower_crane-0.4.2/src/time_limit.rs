use pyo3::prelude::*;
// Input array contains boolean indicating base_state or excited state.
// Only believe array if excited_state is detected for an interval
// bigger than min_time.
// It is assumed, that False is the base_state and True is the
// detection (excited_state) which needs to exceed min_time.

// Returns np.ndarray, regardless of input type
pub fn apply_time_limit(
    array: &[bool],
    raw_time: &[i64],
    min_time: i64,
    base_state: bool,
) -> PyResult<Vec<bool>> {
    let mut result = vec![false; array.len()];

    let mut ignore_next_excitement = false;
    let mut apply_next_excitement = true;
    for (i, state) in array.iter().enumerate() {
        if *state == base_state {
            result[i] = base_state;
            // We're in base state, therefore reset all expectations
            // about what's happening in the next excited state.
            ignore_next_excitement = false;
            apply_next_excitement = false;
        } else if apply_next_excitement || ignore_next_excitement {
            if apply_next_excitement {
                result[i] = !base_state;
            } else {
                result[i] = base_state
            }
        } else {
            // We need to determine whether to apply_next_excitement
            // or to ignore_next_excitement. This requires a scan into
            // upcoming fixes. Find the next fix on which
            // the Viterbi decoder said "base".
            let mut j = i + 1;
            while j < raw_time.len() {
                let upcoming_fix_decoded = array[j];
                if upcoming_fix_decoded == base_state {
                    break;
                }
                j += 1;
            }

            if j == raw_time.len() {
                // No such fix, end of log. Then apply excitement
                apply_next_excitement = true;
                result[i] = !base_state;
            } else {
                // Found next base fix.
                let upcoming_fix_time_ahead = raw_time[j] - raw_time[i];
                // If it's far enough into the future, then assume excitement
                if upcoming_fix_time_ahead >= min_time {
                    apply_next_excitement = true;
                    result[i] = !base_state;
                } else {
                    ignore_next_excitement = true;
                    result[i] = base_state;
                }
            }
        }
    }
    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_apply_time_limit() {
        let array = vec![
            true, false, true, true, false, true, true, true, false, false, true, false, false,
            true, true,
        ];
        let raw_time = vec![0, 1, 2, 3, 4, 5, 6, 7, 8, 13, 14, 15, 16, 17, 18];
        let min_time = 3;
        let base_state = false;
        let result = apply_time_limit(&array, &raw_time, min_time, base_state).unwrap();
        assert_eq!(
            result,
            vec![
                true, false, false, false, false, true, true, true, false, false, false, false,
                false, true, true
            ]
        );

        let base_state = true;
        let result = apply_time_limit(&array, &raw_time, min_time, base_state).unwrap();
        assert_eq!(
            result,
            vec![
                true, true, true, true, true, true, true, true, false, false, true, true, true,
                true, true
            ]
        );
    }
}
