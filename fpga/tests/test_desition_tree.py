import cocotb
from cocotb.triggers import Timer
from cocotb.binary import BinaryValue
from util import vector_high_at

@cocotb.test()
async def test_first_decision_tree(dut):
    vector_high_at(dut.f, [])

    await Timer(1, units="ns")

    assert dut.leaf.value[0] == 1, "l0t0 is active"
    assert dut.leaf.value[1] == 0, "l1t0 is inactive"

    vector_high_at(dut.f, [384])
    await Timer(1, units="ns")

    vector_high_at(dut.f, [359])
    await Timer(1, units="ns")

    assert dut.leaf.value[2] == 1, "l2t0 is active"
    assert dut.leaf.value[3] == 0, "l3t0 is inactive"

    # dut._log.info("input is %s", dut.f.value)
    # dut._log.info("output is %s", dut.leaf.value)
