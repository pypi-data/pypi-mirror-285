use pyo3::prelude::*;

// Viterbi decoder implementation in Numpy.

// Anomaly is that emissions is an array containing probabilities and not a signal
// from {0, 1}. This allows to express that our confidence in array values might be
// different at different points.

// For example, we could scale the variometer input signal to a [0, 1] range to
// indicate our confidence of being on tow. A normal viterbi decoder would only
// allow us to express emission_logs which are the same for every input signal.

// Args:
//     init_probs (np.ndarray): State initialization probabilities
//     transition_probs (np.ndarray): Probabilities of transitioning to other state
//     emissions (np.ndarray): Certainty of being in state 1 for emission array

// Returns:
//     np.ndarray: Most likely sequence of events
pub fn viterbi_decode(
    init_probs: [f64; 2],
    transition_probs: [[f64; 2]; 2],
    emissions: &[f64],
) -> PyResult<Vec<usize>> {
    if emissions.is_empty() {
        return Ok(vec![]);
    }

    assert_eq!(init_probs.len(), 2);
    assert_eq!(transition_probs.len(), 2);
    for p in emissions {
        assert!(0.0 < *p && *p <= 1.0)
    }

    let _init_log = [init_probs[0].ln(), init_probs[1].ln()];
    let _transition_log = [
        [transition_probs[0][0].ln(), transition_probs[0][1].ln()],
        [transition_probs[1][0].ln(), transition_probs[1][1].ln()],
    ];

    let _emission_log = emissions
        .iter()
        .map(|x| [(1.0 - x).ln(), x.ln()])
        .collect::<Vec<[f64; 2]>>();

    let n = emissions.len();
    let mut state_log = vec![[0.0, 0.0]; n];
    let mut backtrack_info = vec![[0, 0]; n];

    // Forward pass, calculate the probabilities of states and the
    // back-tracking information.

    // The initial state probability estimates are treated separately
    // because these come from the initial distribution.
    state_log[0][0] += _init_log[0] + _emission_log[0][0];
    state_log[0][1] += _init_log[1] + _emission_log[0][1];

    // Successive state probability estimates are calculated using
    // the log-probabilities in the transition matrix.
    let mut from_0: f64;
    let mut from_1: f64;
    for i in 1..n {
        for target in 0..2 {
            from_0 = state_log[i - 1][0] + _transition_log[0][target];
            from_1 = state_log[i - 1][1] + _transition_log[1][target];
            if from_0 > from_1 {
                backtrack_info[i][target] = 0;
                state_log[i][target] = from_0 + _emission_log[i][target];
            } else {
                backtrack_info[i][target] = 1;
                state_log[i][target] = from_1 + _emission_log[i][target];
            }
        }
    }

    let mut state = if state_log[n - 1][0] > state_log[n - 1][1] {
        0
    } else {
        1
    };

    let mut states = vec![0; n];
    let last = states.last_mut().unwrap();
    *last = state;

    for i in (1..n).rev() {
        state = backtrack_info[i][state];
        states[i - 1] = state;
    }
    Ok(states)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_viterbi_decode() {
        let init_probs = [0.5, 0.5];
        let transition_probs = [[0.9, 0.1], [0.1, 0.9]];
        let emissions = [0.1, 0.1, 0.6, 0.3, 0.2, 0.7, 0.8, 0.8, 0.9, 0.2];
        let result = viterbi_decode(init_probs, transition_probs, &emissions).unwrap();
        assert_eq!(result, vec![0, 0, 0, 0, 0, 1, 1, 1, 1, 1]);
    }
}
