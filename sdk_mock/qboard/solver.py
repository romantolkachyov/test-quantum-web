#!/usr/bin/env python
import numpy as np
import sys
import logging
from qboard import qubo
import qboard.utils
from qboard.utils import Logger
from qboard.constants import *

class solver:

    supported_modes = {"bf"}

    def __init__(self, mode, enable_cache=True, verbosity=1, params={}, log_logger = None):
        self.logger = Logger(verbosity = verbosity, log_logger = log_logger)
        self.gparams = {"enable_cache": enable_cache, "verbosity": verbosity, "logger": self.logger}
        self.mparams = params.copy()
        self.mode = mode
        if ((self.mode not in self.supported_modes) and (self.mode[:6] != "remote")):
            raise ValueError("Mode {} not supported. Available modes are {}".format(self.mode, self.supported_modes))
        self.handle_params()

    def handle_params(self):
        def callback_handler(payload):
            if payload["cb_type"] == CB_TYPE_NEW_SOLUTION:
                self.logger.log("Found solution %f" % payload["energy"], 1)
            elif payload["cb_type"] == CB_TYPE_INTERRUPT_TIMEOUT:
                self.logger.log("Solver interrupted by timeout. Best solution is %f" % payload["energy"], 1)
            if "callback" in self.gparams:
                self.gparams["callback"](payload)

        self.gparams_mod = self.gparams.copy()
        self.gparams_mod["callback"] = callback_handler
        self.gparams_mod["logger"] = self.logger

    def _solve(self, Q=None, h=None, J=None, gparams = {}, mparams = {}):
        if self.basis == "qubo":
            h, J = qubo.toising(Q)
            Q = np.asarray(Q)
        else:
            Q = qubo.fromising(h, J)
        shift = (Q.sum() + Q.trace()) / 4

        self.logger.log("Solver %s started" % self.mode, 1)

        if self.mode == "simcim":
            from qboard.solvers.simcim_adapter import SimCIMAdapter
            adapter = SimCIMAdapter(gparams = gparams, mparams = mparams)
            if self.basis == "qubo":
                spins, energy = adapter.solve_qubo(Q)
            else:
                spins, energy = adapter.solve_ising(h, J)
            return spins, energy
        elif self.mode == "bf":
            from qboard.solvers.bf_solver import BFSolver
            solver = BFSolver(gparams = gparams, mparams = mparams)
            if self.basis == "qubo":
                spins, energy = solver.solve_qubo(Q)
            else:
                spins, energy = solver.solve_ising(h, J)
            return spins, energy
        elif self.mode == "dwave":
            from qboard.solvers.dwave_adapter import DWaveAdapter
            solver = DWaveAdapter(gparams = gparams, mparams = mparams)
            if self.basis == "qubo":
                spins, energy = solver.solve_qubo(Q)
            else:
                spins, energy = solver.solve_ising(h, J)
            return spins, energy
        elif self.mode[:6] == "remote":
            from qboard.solvers.remote_adapter import RemoteAdapter
            solver = RemoteAdapter(self.mode.split(":")[1], gparams = gparams, mparams = mparams)
            if self.basis == "qubo":
                spins, energy = solver.solve_qubo(Q)
            else:
                spins, energy = solver.solve_ising(h, J)
            return spins, energy

    def solve_qubo(self, Q, timeout=None, target=None, callback=None, enable_cache=None, verbosity=None, params={}):
        gparams_current = self.gparams_mod.copy()
        gparams_current.update(qboard.utils.filter_params({"target": target, "timeout": timeout, "enable_cache": enable_cache, "verbosity": verbosity}))
        v = self.logger.verbosity
        if verbosity != None:
            self.logger.verbosity = verbosity
        if callback != None:
            self.gparams["callback"] = callback
        else:
            self.gparams.pop("callback", None)
        mparams_current = self.mparams.copy()
        mparams_current.update(params)
        self.basis = "qubo"
        result = self._solve(Q=Q, gparams = gparams_current, mparams = mparams_current)
        self.logger.verbosity = v
        return result

    def solve_ising(self, h, J, timeout=None, target=None, callback=None, enable_cache=None, verbosity=None, params={}):
        gparams_current = self.gparams_mod.copy()
        gparams_current.update(qboard.utils.filter_params({"target": target, "timeout": timeout, "enable_cache": enable_cache, "verbosity": verbosity}))
        v = self.logger.verbosity
        if verbosity != None:
            self.logger.verbosity = verbosity
        if callback != None:
            self.gparams["callback"] = callback
        else:
            self.gparams.pop("callback", None)
        mparams_current = self.mparams.copy()
        mparams_current.update(params)
        self.basis = "ising"
        result = self._solve(h=h, J=J, gparams = gparams_current, mparams = mparams_current)
        self.logger.verbosity = v
        return result
