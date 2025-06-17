import cocotb
from cocotb.triggers import Timer

discrete_values = [-0.25, -0.125, -0.0625, -0.03125, -0.015625, 0.015625, 0.03125, 0.0625, 0.125, 0.25, 0.5, 1.0, 2.0]
v = {value: i for i, value in enumerate(discrete_values)}

zero_offset = 128

def set_zeros(signal):
    for i in range(len(discrete_values)):
        signal[i].value = 0

def out_val(value):
    return int(128 + 4 * value)

@cocotb.test()
async def test_counter_adder_one(dut):
    set_zeros(dut.val)
    dut.val[v[0.25]].value = 1

    await Timer(1, units="ns")

    assert dut.score.value == zero_offset + 1

@cocotb.test()
async def test_counter_adder_16(dut):
    set_zeros(dut.val)
    dut.val[v[0.25]].value = 16

    await Timer(1, units="ns")

    assert dut.score.value == out_val(4)


@cocotb.test()
async def test_counter_adder_multiple_values(dut):
    set_zeros(dut.val)
    dut.val[v[0.25]].value = 16
    dut.val[v[2.0]].value = 2

    await Timer(1, units="ns")

    assert dut.score.value == out_val(8)


@cocotb.test()
async def test_counter_adder_negative(dut):
    set_zeros(dut.val)
    dut.val[v[0.25]].value = 16
    dut.val[v[2.0]].value = 2
    dut.val[v[-0.25]].value = 2

    await Timer(1, units="ns")

    assert dut.score.value == out_val(7.5)

# TODO: Test what happes on an overflow
