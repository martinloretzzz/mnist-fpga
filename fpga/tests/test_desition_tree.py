import cocotb
from cocotb.triggers import Timer
from cocotb.binary import BinaryValue

def input_high_at(high_indices):
    bits = ["0"] * (28*28)
    for index in high_indices:
        bits[index] = "1"
    return BinaryValue("".join(bits))

@cocotb.test()
async def my_first_test(dut):
    dut.f.value = input_high_at([])

    await Timer(1, units="ns")

    assert dut.leaf.value[0] == 1, "l0t0 is active"
    assert dut.leaf.value[1] == 0, "l1t0 is inactive"

    dut.f.value = input_high_at([384])
    await Timer(1, units="ns")

    dut.f.value = input_high_at([359])
    await Timer(1, units="ns")

    assert dut.leaf.value[2] == 1, "l2t0 is active"
    assert dut.leaf.value[3] == 0, "l3t0 is inactive"

    # dut._log.info("input is %s", dut.f.value)
    # dut._log.info("output is %s", dut.leaf.value)
