use pyo3::prelude::*;

// Find indices a, b in array with b > a, so that array[b]-array[a] is maximized and positive.
// Return None if no such a, b exist
pub fn arg_max_positive_diff(array: &[i64]) -> PyResult<Option<(usize, usize)>> {
    if array.len() <= 1 {
        return Ok(None);
    }
    let mut best = (0, 0);
    let mut a = 0;
    let mut max_diff = 0;
    for i in 1..array.len() {
        if array[i] - array[a] > max_diff {
            best = (a, i);
            max_diff = array[best.1] - array[best.0];
        }
        if array[i] < array[a] {
            a = i
        }
    }
    if max_diff <= 0 {
        return Ok(None);
    }
    Ok(Some(best))
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_arg_max_positive_diff() {
        let array = vec![1, 2, 3, 2, 1];
        assert_eq!(arg_max_positive_diff(&array).unwrap(), Some((0, 2)));

        let array = vec![3, 4, 8, 9, 2, 11, 0, 4, 4, 4, 10, 2, 3, 4, 5];
        assert_eq!(arg_max_positive_diff(&array).unwrap(), Some((6, 10)));

        // an empty array should return None
        let array = vec![];
        assert_eq!(arg_max_positive_diff(&array).unwrap(), None);

        // an array with only one element should return None
        let array = vec![1];
        assert_eq!(arg_max_positive_diff(&array).unwrap(), None);

        // an array without a positive difference should return None
        let array = vec![8, 3, 2, 1, 0];
        assert_eq!(arg_max_positive_diff(&array).unwrap(), None);
    }
}
