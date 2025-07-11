import os
import argparse
from cocotb.runner import get_runner


sim = os.getenv("SIM", "icarus")
base_path = os.path.join(os.path.dirname(__file__), '../hdl')


def module_unit_test_runner(toplevel, sources, test_modules):
    sources = [f"{base_path}/{source}" for source in sources]
    runner = get_runner(sim)
    runner.build(sources=sources, hdl_toplevel=toplevel, build_dir=f"sim_build/{toplevel}")
    runner.test(hdl_toplevel=toplevel, test_module=",".join(test_modules))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('test', type=str)
    args = parser.parse_args()

    match args.test:
        case "tree":
            module_unit_test_runner("decision_tree_leaves_0", ["decision_trees.sv"], ["test_desition_tree"])
        case "counter":
            module_unit_test_runner("leaf_counter_0", ["leaf_counters.sv"], ["test_leaf_counter"])
        case "adder":
            module_unit_test_runner("counter_adder", ["counter_adder.sv"], ["test_counter_adder"])
        case "max":
            module_unit_test_runner("max_value_index", ["max_value_index.sv"], ["test_max_value_index"])
        case "classifier":
            sources = ["decision_trees.sv", "leaf_counters.sv", "counter_adder.sv", "max_value_index.sv", "mnist_classifier.sv"]
            module_unit_test_runner("mnist_classifier", sources, ["test_mnist_classifier"])
        case _:
            raise Exception(f"Can't find a runner for {args.test}")

