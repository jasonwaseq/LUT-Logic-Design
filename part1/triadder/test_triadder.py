import git
import os
import sys
import git

# I don't like this, but it's convenient.
_REPO_ROOT = git.Repo(search_parent_directories=True).working_tree_dir
assert (os.path.exists(_REPO_ROOT)), "REPO_ROOT path must exist"
sys.path.append(os.path.join(_REPO_ROOT, "util"))
from utilities import runner, lint, assert_resolvable
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
timescale = "1ps/1ps"

tests = ['width_in',
         'width_out',
         'init_test',
         *[f'zeroone_add_test_{i:03}' for i in range(1,8)],
         *[f'random_add_test_{i:03}' for i in range(1,27)],
         *[f'limits_add_test_{i:03}' for i in range(1,27)],
         ]

@pytest.mark.parametrize("width_p", [1, 2, 7])
@pytest.mark.parametrize("test_name", tests)
@pytest.mark.parametrize("simulator", ["verilator", "icarus"])
@max_score(0)
def test_each(test_name, simulator, width_p):
    # This line must be first
    parameters = dict(locals())
    del parameters['test_name']
    del parameters['simulator']
    runner(simulator, timescale, tbpath, parameters, testname=test_name)

# Opposite above, run all the tests in one simulation but reset
# between tests to ensure that reset is clearing all state.
@pytest.mark.parametrize("width_p", [1, 2, 7])
@pytest.mark.parametrize("simulator", ["verilator", "icarus"])
@max_score(2)
def test_all(simulator, width_p):
    # This line must be first
    parameters = dict(locals())
    del parameters['simulator']
    runner(simulator, timescale, tbpath, parameters)

@pytest.mark.parametrize("width_p", [1, 2, 7])
@pytest.mark.parametrize("simulator", ["verilator"])
@max_score(0)
def test_lint(simulator, width_p):
    # This line must be first
    parameters = dict(locals())
    del parameters['simulator']
    lint(simulator, timescale, tbpath, parameters)

@pytest.mark.parametrize("width_p", [1, 2, 7])
@pytest.mark.parametrize("simulator", ["verilator"])
@max_score(0)
def test_style(simulator, width_p):
    # This line must be first
    parameters = dict(locals())
    del parameters['simulator']
    lint(simulator, timescale, tbpath, parameters, compile_args=["--lint-only", "-Wwarn-style", "-Wno-lint"])


### Begin Tests ###

@cocotb.test()
async def width_out(dut):
    """The width of sum_o should be equal to width_p + 1"""
    assert len(dut.sum_o) == (dut.width_p.value + 2)

@cocotb.test()
async def width_in(dut):
    """The width of sum_o should be equal to width_p, and a_i, b_i should be equal to width_p -1"""
    assert len(dut.a_i) == (dut.width_p.value)
    assert len(dut.b_i) == (dut.width_p.value)
    assert len(dut.c_i) == (dut.width_p.value)

@cocotb.test()
async def init_test(dut):
    """Test for Basic Connectivity"""

    A = 0
    B = 0

    dut.a_i.value = 0
    dut.b_i.value = 0
    dut.c_i.value = 0

    await Timer(1, units="ns")

    assert_resolvable(dut.sum_o)

async def add_test(dut, a, b, c):
    """Test for adding three numbers"""

    # I would like to test numbers that depend on the parameters to
    # the DUT (e.g. width_p), but the parameters are not available
    # until test runtime, so we occasionally have to pass in strings
    # that reference the DUT. Hence, these if/else statements (until I
    # find a better way).

    if(isinstance(a, int)):
        A = a
    else:
        A = eval(a)

    if(isinstance(b, int)):
        B = b
    else:
        B = eval(b)

    if(isinstance(c, int)):
        C = c
    else:
        C = eval(c)

    dut.a_i.value = A
    dut.b_i.value = B
    dut.c_i.value = C

    await Timer(1, units="ns")

    assert_resolvable(dut.sum_o)
    assert dut.sum_o.value == (A + B + C) , f"Incorrect Result: {dut.a_i.value} + {dut.b_i.value} + {dut.c_i.value} != {dut.a_i.value + dut.b_i.value + dut.b_i.value}. Got: {dut.sum_o.value} at Time {get_sim_time(units='ns')}ns."

tf = TestFactory(test_function=add_test)

#for a,b,c in product([0,1], [0,1], [0,1]):
tf.add_option(name='a', optionlist=[0,1])
tf.add_option(name='b', optionlist=[0,1])
tf.add_option(name='c', optionlist=[0,1])
tf.generate_tests(prefix=f"zeroone_")
#    tf.generate_tests()

#for a,b,c in product([0, 1,"(1 << len(dut.a_i)) - 1"], [0, 1,"(1 << len(dut.a_i)) - 1"], [0, 1,"(1 << len(dut.a_i)) - 1"]):
tf.add_option(name='a', optionlist=[0, 1,"(1 << len(dut.a_i)) - 1"])
tf.add_option(name='b', optionlist=[0, 1,"(1 << len(dut.a_i)) - 1"])
tf.add_option(name='c', optionlist=[0, 1,"(1 << len(dut.a_i)) - 1"])
tf.generate_tests(prefix=f"limits_")
#    tf.generate_tests(prefix=f"limits_{a}_{b}_{c}")
#    tf.generate_tests()

tf.add_option(name='a', optionlist=3*["random.randint(0, (1 << len(dut.a_i)) - 1)"])
tf.add_option(name='b', optionlist=3*["random.randint(0, (1 << len(dut.b_i)) - 1)"])
tf.add_option(name='c', optionlist=3*["random.randint(0, (1 << len(dut.b_i)) - 1)"])
tf.generate_tests(prefix="random_")
#tf.generate_tests()

