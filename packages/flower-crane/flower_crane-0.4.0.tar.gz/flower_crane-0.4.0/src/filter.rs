use pyo3::prelude::*;

/// Filter an array by computing a rolling averages. If an item further away from
/// the rolling avg then `allowed_offset`, it is replaced by the previous value.
pub fn filter(data: &[i64], allowed_offset: i64) -> PyResult<(Vec<i64>, usize)> {
    if data.is_empty() {
        return Ok((vec![], 0));
    }

    // prepare the result vector
    let mut filtered = vec![0; data.len()];
    filtered[0] = data[0];

    // runnning sum is the sum of the previous SIZE elements
    const SIZE: usize = 10;
    let mut running_sum = data[0] * SIZE as i64;
    let mut filter_count = 0;

    for i in 1..data.len() {
        let expected = running_sum / SIZE as i64;
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
        let bad_data = vec![1, 2, 3, 1000, 5, 1000];

        let allowed = 500;
        let result = filter(&bad_data, allowed).unwrap();

        let clean_data: Vec<i64> = vec![1, 2, 3, 3, 5, 5];
        assert_eq!(result.0, clean_data);
        assert_eq!(result.1, 2);
    }

    #[test]
    fn filter_replaces_negative_outliers() {
        // Given corrupted data
        let bad_data = vec![2001, 2002, 2003, 1000, 2005, 2000];

        let allowed = 500;
        let result = filter(&bad_data, allowed).unwrap();

        let clean_data: Vec<i64> = vec![2001, 2002, 2003, 2003, 2005, 2000];
        assert_eq!(result.0, clean_data);
        assert_eq!(result.1, 1);
    }
}
