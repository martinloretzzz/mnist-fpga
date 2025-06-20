import cocotb
from cocotb.triggers import Timer
from util import vector_high_at


@cocotb.test()
async def test_leaf_counter_one(dut):
    vector_high_at(dut.l, [0])
    await Timer(1, units="ns")

    assert dut.val[0].value == 1


@cocotb.test()
async def test_leaf_counter_4(dut):
    vector_high_at(dut.l, [0, 20, 40, 54])
    await Timer(1, units="ns")

    assert dut.val[0].value == 4


@cocotb.test()
async def test_leaf_counter_multiple(dut):
    vector_high_at(dut.l, [0, 20, 40, 54, 28, 134])
    await Timer(1, units="ns")

    assert dut.val[0].value == 4
    assert dut.val[3].value == 2


@cocotb.test()
async def test_leaf_counter_multiple_active_inside_tree(dut):
    vector_high_at(dut.l, [0, 6, 12])
    await Timer(1, units="ns")

    assert dut.val[0].value == 1
