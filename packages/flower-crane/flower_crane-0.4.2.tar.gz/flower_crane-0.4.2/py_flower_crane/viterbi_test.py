import numpy as np

import flower_crane


def test_viterbi_decode():
    init_probs = [0.5, 0.5]
    transition_probs = [[0.9, 0.1], [0.1, 0.9]]
    emissions = np.array([0.1, 0.1, 0.6, 0.3, 0.2, 0.7, 0.8, 0.8, 0.9, 0.2])
    result = flower_crane.viterbi_decode(init_probs, transition_probs, emissions)
    assert result == [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
