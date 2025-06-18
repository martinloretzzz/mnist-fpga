import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_leaf_counter_one(dut):
    dut.l = 0
    dut.l[0].value = 1

    await Timer(1, units="ns")

    assert dut.val[0].value == 1

@cocotb.test()
async def test_leaf_counter_4(dut):
    dut.l = 0
    dut.l[0].value = 1
    dut.l[20].value = 1
    dut.l[35].value = 1
    dut.l[39].value = 1

    await Timer(1, units="ns")

    assert dut.val[0].value == 4


@cocotb.test()
async def test_leaf_counter_multiple(dut):
    dut.l = 0
    dut.l[0].value = 1
    dut.l[20].value = 1
    dut.l[35].value = 1
    dut.l[39].value = 1

    dut.l[28].value = 1
    dut.l[90].value = 1

    await Timer(1, units="ns")

    assert dut.val[0].value == 4
    assert dut.val[3].value == 2
