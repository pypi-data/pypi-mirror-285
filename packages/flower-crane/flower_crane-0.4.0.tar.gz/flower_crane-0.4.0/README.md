# Flower Crane

Flower Crane provides some utility functions for working with NumPy arrays.

1. `viterbi_decode` - find the most likely path along a sequence of observations.
2. `compute_thermals`
3. `apply_time_limit` - apply a time limit to decide on base or excited state
4. `bearing_change_rate` - calculate the change rate of the bearing
5. `arg_max_positive_diff` - find two indices `a, b` with `b > a` which maximize `arr[b] - arr[a]`
6. `find_meeting` - find indices in which four dimensional lines are close to each other
7. `filter` - find and replace outliers in array by comparing with running avg

## Develop

First, create a new virtual env and activate it

```bash
python -m venv .env
source .env/bin/activate
```

You can install the module locally with

```bash
maturin develop
```

Make sure to update the python type stub in `flower_crane.pyi` if you change the signature of a function. 
After you have placed your PyPi API-Token in your `.pypirc` file, you can publish your module with

```bash
maturin publish -r test
```

or 

```bash
maturin publish -r pypi
```

## Tests

```bash
python -m pytest
cargo test
```

## Benches

To compare the performances of the different implementations, run

```bash
maturin build --release
pip install .
python -m py_flower_crane.benchratio
```
