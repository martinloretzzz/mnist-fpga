import os
import argparse

sim = os.getenv("SIM", "icarus")
base_path = os.path.join(os.path.dirname(__file__), '../hdl')

def decision_tree_runner():
    from cocotb.runner import get_runner
    sources = [f"{base_path}/decision_trees.sv"]
    toplevel = "decision_tree_leaves_0"

    runner = get_runner(sim)
    runner.build(sources=sources, hdl_toplevel=toplevel)
    runner.test(hdl_toplevel=toplevel, test_module="test_desition_tree,")

def adder_runner():
    from cocotb.runner import get_runner
    sources = [f"{base_path}/counter_adder.sv"]
    toplevel = "counter_adder"

    runner = get_runner(sim)
    runner.build(sources=sources, hdl_toplevel=toplevel)
    runner.test(hdl_toplevel=toplevel, test_module="test_counter_adder,")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('test', type=str)
    args = parser.parse_args()

    match args.test:
        case "tree":
            decision_tree_runner()
        case "adder":
            adder_runner()
        case _:
            raise Exception(f"Can't find a runner for {args.test}")

