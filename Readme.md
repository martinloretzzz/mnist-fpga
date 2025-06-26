



## Reproduce Results

### Install dependencies:

`pip install torch torchvision scikit-learn matplotlib cocotb pytest tqdm`

### Install fork of xgboost:

Clone forked xgboost: `git clone --recursive https://github.com/martinloretzzz/xgboost`

Build the fork from source and install python package: [Docs](https://xgboost.readthedocs.io/en/stable/build.html)

Run:
`cmake -B build -S . -DCMAKE_BUILD_TYPE=RelWithDebInfo -GNinja -DCMAKE_BUILD_WITH_INSTALL_RPATH=O`
`cd build && ninja`
`cd python-package && pip install .`


### Train boosted tree
Run `python boosted_tree.py` to export the trees to `model.json`.

### Generate SystemVerilog Code:
Run `python generate_verilog.py` to generate all boosted tree specific verilog files: _decision_trees.sv_, _leaf_counters.sv_, _mnist_classifier.sv_

### Synthesize Verilog Design using Quartus Prime
Create a new project and import all SysgtemVerilog files from /fpga/hdl/. The following custom settings are used:
- Compiler Settings > Advanced Settings > Auto Shift Register Recognition = OFF
- Optimization mode > Performance (Aggressive - increases runtime and area)

This generates all the utilitzaiton, timing and power reports

### Get accuracy on MNIST testset:

Install verilog simulator: `sudo apt update && sudo apt install iverilog`

`cd fpga/tests/ && python runner.py classifier` (set skip=False on test_classifier_on_testset test in fpga/tests/test_mnist_classifier.py)
