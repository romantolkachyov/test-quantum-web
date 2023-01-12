## Python SDK mock

Repository contains SDK mock for QBoard platform

### Install (Python 3)
```
pip install . --user
```

### Sample usage

```python
import qboard
import numpy as np

Q = np.random.rand(30,30) - 0.5

solver = qboard.solver(mode="bf")

def cb(dic):
    if dic["cb_type"] == qboard.constants.CB_TYPE_NEW_SOLUTION:
        energy = dic["energy"]
        spins = dic["spins"]
        print("New solution found, energy %f, result vector %s" % (energy, spins))
    if dic["cb_type"] == qboard.constants.CB_TYPE_INTERRUPT_TIMEOUT:
        print("Solver interrupted by timeout")
    if dic["cb_type"] == qboard.constants.CB_TYPE_INTERRUPT_TARGET:
        print("Solver interrupted by target")
spins, energy = solver.solve_qubo(Q,  callback = cb, timeout = 5, verbosity = 0)
```
