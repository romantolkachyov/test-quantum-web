#!/usr/bin/env python
import scipy.linalg
import numpy as np

def energy_qubo(Q, spins_qubo):
    return spins_qubo @ Q @ spins_qubo

def energy_ising(h, J, spins_ising):
    return h @ spins_ising + spins_ising @ J @ spins_ising

def energy(Q, spins):
    """
    >>> a = [[2, 2], [3, 6]]
    >>> energy(a, [1, 0])
    2
    >>> energy(a, [1, -1])
    2
    """
    s = (1 + np.asarray(spins).astype(int)) // 2
    e = s @ Q @ s
    return e


def ienergy(h, J, spins):
    """Energy for ising problem"""
    s = np.asarray(spins).astype(int)
    s[np.where(s == 0)] = -1
    e = h @ s + s @ J @ s
    return e


def dump(filename, h, J):
    """Dump h and J to filename in our custom format"""
    with open(filename, "w") as fp:
        fp.write(
                "3.0\n"
                "0.1\n"
                "-0.9\n"
                "0.07\n"
                + str(h.size) + "\n"
        )
        s = "\n".join(map(str, h)) + "\n"
        fp.write(s)
        L = []
        for i in range(h.size):
            for j in range(i + 1, h.size):
                if J[i, j]:
                    L.append("{} {} {}\n".format(1 + i, 1 + j, J[i, j]))
        fp.write("".join(L))


def toising(Q):
    """From qubo formulation to ising
    >>> a = toising(np.array([[1, 2], [3, 4]]))
    >>> print(a[0])
    [1.75 3.25]
    >>> print(a[1])
    [[0.   0.5 ]
     [0.75 0.  ]]
    """
    Q = np.asarray(Q)
    h = (Q.sum(axis=1) + Q.sum(axis=0)) / 4
    J = (Q - np.diag(np.diag(Q))) / 4
    return h, J


def fromising(h, J):
    """From ising formulation of problem to qubo
    >>> a = fromising([1.75, 3.25], [[0, 0.5], [0.75, 0]])
    >>> print(a)
    [[1. 2.]
     [3. 4.]]
    """
    h, J = np.asarray(h), np.asarray(J)
    Q = 4 * J + 2 * np.diag(h - J.sum(axis=0) - J.sum(axis=1))
    return Q


def constrain(Q, constraints, n):
    """\
    Append constraints to qubo matrix increasing size of matrix to n * len(constraints)
    >>> Q, const = constrain([[1000, 1000], [1000, 1000]], [([0, 1], 4), ([1, 3], 8)], 2)
    >>> print(Q.astype(int))
    [[ 985 1003    0    0    2    4]
     [1003  954    1    2    6   12]
     [   0    1   -7    2    0    0]
     [   0    2    2  -12    0    0]
     [   2    6    0    0  -28    8]
     [   4   12    0    0    8  -48]]
    >>> const
    80
    """
    base = 2.0 ** np.arange(-n, 0)
    baseM = np.outer(base, base)
    edges = []
    bs = []
    Q = Q.copy()
    for p, b in constraints:
        Q += np.outer(p, p) - 2 * b * np.diag(p)
        edges.append(np.outer(p, b * base))
        bs.append(b)
    size = Q.shape[0] + n * len(edges)
    edge = np.hstack(edges)
    QQ = np.empty((size, size))
    QQ[: Q.shape[0], : Q.shape[0]] = Q
    QQ[: Q.shape[0], Q.shape[0] :] = edge
    QQ[Q.shape[0] :, : Q.shape[0]] = edge.T
    QQ[Q.shape[0] :, Q.shape[0] :] = scipy.linalg.block_diag(
        *((baseM - 2 * np.diag(base)) * b ** 2 for b in bs)
    )
    const = sum(_[1] ** 2 for _ in constraints)
    return QQ, const
