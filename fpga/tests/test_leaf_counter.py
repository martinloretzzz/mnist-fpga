import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_leaf_counter(dut):
    assert 1 == 1