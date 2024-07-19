use pyo3::prelude::*;

/// Filter an array by computing a rolling averages. If an item further away from
/// the rolling avg then `allowed_offset`, it is replaced by the previous value.
pub fn filter(data: &[f64], allowed_offset: f64) -> PyResult<(Vec<f64>, usize)> {
    if data.is_empty() {
        return Ok((vec![], 0));
    }

    // prepare the result vector
    let mut filtered = vec![0.0; data.len()];
    filtered[0] = data[0];

    // runnning sum is the sum of the previous SIZE elements
    const SIZE: usize = 10;
    let mut running_sum = data[0] * SIZE as f64;
    let mut filter_count = 0;

    for i in 1..data.len() {
        let expected = running_sum / SIZE as f64;
        if (data[i] - expected).abs() > allowed_offset {
            filter_count += 1;
            filtered[i] = filtered[i - 1];
        } else {
            filtered[i] = data[i];
        }

        running_sum += data[i];
        running_sum -= data[i.max(SIZE) - SIZE];
    }
    Ok((filtered, filter_count))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn filter_replaces_positive_outliers() {
        // Given corrupted data
        let bad_data = vec![1.0, 2.0, 3.0, 1000.0, 5.0, 1000.0];

        let allowed = 500.0;
        let result = filter(&bad_data, allowed).unwrap();

        let clean_data: Vec<f64> = vec![1.0, 2.0, 3.0, 3.0, 5.0, 5.0];
        assert_eq!(result.0, clean_data);
        assert_eq!(result.1, 2);
    }

    #[test]
    fn filter_replaces_negative_outliers() {
        // Given corrupted data
        let bad_data = vec![2001.0, 2002.0, 2003.0, 1000.0, 2005.0, 2000.0];

        let allowed = 500.0;
        let result = filter(&bad_data, allowed).unwrap();

        let clean_data: Vec<f64> = vec![2001.0, 2002.0, 2003.0, 2003.0, 2005.0, 2000.0];
        assert_eq!(result.0, clean_data);
        assert_eq!(result.1, 1);
    }
}
