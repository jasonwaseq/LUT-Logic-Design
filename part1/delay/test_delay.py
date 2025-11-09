import git
import os
import sys
import git
import numpy as np
from itertools import accumulate
# I don't like this, but it's convenient.
_REPO_ROOT = git.Repo(search_parent_directories=True).working_tree_dir
assert (os.path.exists(_REPO_ROOT)), "REPO_ROOT path must exist"
sys.path.append(os.path.join(_REPO_ROOT, "util"))
from utilities import runner, lint, assert_resolvable, clock_start_sequence, reset_sequence
tbpath = os.path.dirname(os.path.realpath(__file__))

import pytest

import cocotb

from cocotb.clock import Clock
from cocotb.regression import TestFactory
from cocotb.utils import get_sim_time
from cocotb.triggers import Timer, ClockCycles, RisingEdge, FallingEdge, with_timeout
from cocotb.types import LogicArray, Range

from cocotb_test.simulator import run

from cocotbext.axi import AxiLiteBus, AxiLiteMaster, AxiStreamSink, AxiStreamMonitor, AxiStreamBus

from pytest_utils.decorators import max_score, visibility, tags
   
import random
random.seed(42)
   
timescale = "1ps/1ps"

tests = ['free_run_test_001']

@pytest.mark.parametrize("delay_p", [2, 5, 9])
@pytest.mark.parametrize("test_name", tests)
@pytest.mark.parametrize("simulator", ["verilator", "icarus"])
@max_score(0)
def test_each(test_name, simulator, delay_p):
    # This line must be first
    parameters = dict(locals())
    del parameters['test_name']
    del parameters['simulator']
    runner(simulator, timescale, tbpath, parameters, testname=test_name)

@pytest.mark.parametrize("delay_p", [2, 5, 9])
@pytest.mark.parametrize("simulator", ["verilator", "icarus"])
@max_score(.5)
def test_all(simulator, delay_p):
    # This line must be first
    parameters = dict(locals())
    del parameters['simulator']
    runner(simulator, timescale, tbpath, parameters)

@pytest.mark.parametrize("delay_p", [2, 5, 9])
@pytest.mark.parametrize("simulator", ["verilator"])
@max_score(0)
def test_lint(simulator, delay_p):
    # This line must be first
    parameters = dict(locals())
    del parameters['simulator']
    lint(simulator, timescale, tbpath, parameters)

@pytest.mark.parametrize("delay_p", [2, 5, 9])
@pytest.mark.parametrize("simulator", ["verilator"])
@max_score(0)
def test_style(simulator, delay_p):
    # This line must be first
    parameters = dict(locals())
    del parameters['simulator']
    lint(simulator, timescale, tbpath, parameters, compile_args=["--lint-only", "-Wwarn-style", "-Wno-lint"])

async def free_run_test(dut, l):
    """Test l cycles of the delay module"""

    clk_i = dut.clk_i
    reset_i = dut.reset_i
    en_i = dut.en_i
    d_i = dut.d_i
    d_o = dut.d_o

    en_i.value = LogicArray(['x'])

    await clock_start_sequence(clk_i)

    model = DelayModel(dut.delay_p, clk_i, reset_i, en_i, d_i, d_o)
    model.start()

    d_i.value = 0
    en_i.value = 0

    await reset_sequence(clk_i, reset_i, 10)

    await FallingEdge(clk_i)

    ens = [random.randint(0, 1) for i in range(l)]
    sens = accumulate(ens)
    ds  = [random.randint(0, 1) for i in range(l)]
    seq = zip(ens, ds, [i for i in range(l)], sens)
    for (en, d, i, sens) in seq:

        await FallingEdge(clk_i)
        en_i.value = (en == 1)
        d_i.value = d

        await RisingEdge(clk_i)
        if(sens > dut.delay_p.value):
            assert_resolvable(d_o)
            assert d_o.value == model._d_o, f"Incorrect Result: d_o != . Got: {d_o.value} at Time {get_sim_time(units='ns')}ns."

           
tf = TestFactory(test_function=free_run_test)
tf.add_option(name='l', optionlist=[100])
tf.generate_tests()

class DelayModel():
    def __init__(self, delay_p, clk_i, reset_i, en_i, d_i, d_o):
                 
        self._delay_p = int(delay_p.value)
        self._clk_i = clk_i
        self._reset_i = reset_i
        self._en_i = en_i
        self._d_i = d_i
        self._coro_run = None
        self._nstate = [0] * self._delay_p
        self._d_o = 0

    def start(self):
        """Start model"""
        if self._coro_run is not None:
            raise RuntimeError("Model already started")
        self._coro_run = cocotb.start_soon(self._run())

    async def _run(self):
        mask = (1 << self._delay_p) -1

        while True:
            await RisingEdge(self._clk_i)
            if(self._reset_i.value.is_resolvable and (self._reset_i.value == 1)):
                pass
            elif(self._en_i.value.is_resolvable and (self._en_i.value == 1)):
                self._nstate = np.roll(self._nstate, 1)
                self._nstate[0] = int(self._d_i.value)

            await FallingEdge(self._clk_i)
            self._d_o = int(self._nstate[-1])

    def stop(self) -> None:
        """Stop monitor"""
        if self._coro_run is None:
            raise RuntimeError("Monitor never started")
