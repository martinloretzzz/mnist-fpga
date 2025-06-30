import cocotb
from util import wait_clock, set_zeros

discrete_values = [-0.25, -0.125, -0.0625, -0.03125, -0.015625, 0.015625, 0.03125, 0.0625, 0.125, 0.25, 0.5, 1.0, 2.0]
v = {value: i for i, value in enumerate(discrete_values)}

zero_offset = 128

def out_val(value):
    return int(128 + 4 * value)

@cocotb.test()
async def test_counter_adder_one(dut):
    set_zeros(dut.val)
    dut.val[v[0.25]].value = 1

    await wait_clock(dut, 3)

    assert dut.score.value == zero_offset + 1

@cocotb.test()
async def test_counter_adder_16(dut):
    set_zeros(dut.val)
    dut.val[v[0.25]].value = 16

    await wait_clock(dut, 3)

    assert dut.score.value == out_val(4)


@cocotb.test()
async def test_counter_adder_multiple_values(dut):
    set_zeros(dut.val)
    dut.val[v[0.25]].value = 16
    dut.val[v[2.0]].value = 2

    await wait_clock(dut, 3)

    assert dut.score.value == out_val(8)


@cocotb.test()
async def test_counter_adder_negative(dut):
    set_zeros(dut.val)
    dut.val[v[0.25]].value = 16
    dut.val[v[2.0]].value = 2
    dut.val[v[-0.25]].value = 2

    await wait_clock(dut, 3)

    assert dut.score.value == out_val(7.5)
