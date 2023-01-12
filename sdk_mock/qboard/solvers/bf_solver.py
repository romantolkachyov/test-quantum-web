import numpy as np
from qboard import qubo
from qboard.constants import *
import time
import itertools

class BFSolver:

    def __init__(self, gparams = {}, mparams = {}):
        self.gparams = gparams.copy()
        self.mparams = mparams.copy()
        self.gparams_mod = self.gparams.copy()

    def solve_ising(self, h, J):
        self.basis = "ising"
        self.h = h
        self.J = J
        Q = qubo.fromising(h, J)
        self.offset = (Q.sum() + Q.trace()) / 4
        self.handle_params()
        spins_qubo, energy_qubo = self.solve(Q)
        spins_ising = [(s * 2 - 1) for s in spins_qubo]
        energy_ising = J.dot(spins_ising).dot(spins_ising) + h.dot(spins_ising)
        return spins_ising, energy_ising

    def solve_qubo(self, Q):
        self.basis = "qubo"
        self.handle_params()
        return self.solve(Q)

    def solve(self, Q):
        time_start = time.time()
        #try:
        size = Q.shape[0]
        spins_qubo = np.zeros(size)
        energy_qubo = Q.dot(spins_qubo).dot(spins_qubo)
        generator = map(np.array, itertools.product((0, 1), repeat=size))
        for s in generator:
            e = Q.dot(s).dot(s)
            if (("target" in self.gparams_mod) and (e <= self.gparams_mod["target"])):
                payload = {"_spins": s, "_energy": e, "cb_type": CB_TYPE_INTERRUPT_TARGET}
                self.gparams_mod["callback"](payload)
                break
            if e <= energy_qubo:
                spins_qubo = s
                energy_qubo = e
                payload = {"_spins": spins_qubo, "_energy": energy_qubo, "cb_type": CB_TYPE_NEW_SOLUTION}
                self.gparams_mod["callback"](payload)
            if (("timeout" in self.gparams) and ((time.time() - time_start) >= self.gparams["timeout"])):
                payload = {"_spins": spins_qubo, "_energy": energy_qubo, "cb_type": CB_TYPE_INTERRUPT_TIMEOUT}
                self.gparams_mod["callback"](payload)
                break
        #except:
        #    pass

        return spins_qubo, energy_qubo

    # Convert all basis-related parameters
    def handle_params(self):
        if (("target" in self.gparams) and (self.basis == "ising")):
            self.gparams_mod["target"] = self.gparams["target"] + self.offset

        def callback(payload):
            payload = self.modify_payload(payload)
                
            if self.gparams["callback"] != None:
                self.gparams["callback"](payload)

        self.gparams_mod["callback"] = callback

    # Convert all basis-related payload
    def modify_payload(self, payload):
        payload = payload.copy()

        if self.basis == "qubo":
            payload["spins"] = payload["_spins"]
            payload["energy"] = payload["_energy"]
        elif self.basis == "ising":
            spins_ising = [(s * 2 - 1) for s in payload["_spins"]]
            energy_ising = payload["_energy"] - self.offset
            payload["spins"] = spins_ising
            payload["energy"] = energy_ising

        return payload
