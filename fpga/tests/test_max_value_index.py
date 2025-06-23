import cocotb
from util import wait_clock, set_vector


@cocotb.test()
async def test_max_on_pos_with_one_score(dut):
    set_vector(dut.score, [0, 0, 1, 0, 0, 0, 0, 0, 0, 0])
    await wait_clock(dut, 4)

    assert dut.digit.value == 2


@cocotb.test()
async def test_max_on_pos_with_other_scores(dut):
    set_vector(dut.score, [1, 4, 0, 1, 16, 0, 2, 0, 0, 0])
    await wait_clock(dut, 4)

    assert dut.digit.value == 4


@cocotb.test()
async def test_max_on_pos_with_two_equal(dut):
    set_vector(dut.score, [0, 0, 0, 8, 0, 0, 0, 0, 8, 0])
    await wait_clock(dut, 4)

    assert dut.digit.value == 3


@cocotb.test()
async def test_max_on_pos_with_max_9(dut):
    set_vector(dut.score, [0, 0, 0, 0, 0, 0, 0, 0, 0, 4])
    await wait_clock(dut, 4)

    assert dut.digit.value == 9
