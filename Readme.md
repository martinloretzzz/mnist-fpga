# MNIST FPGA

This repo contains the code for a high-speed, FPGA-optimized implementation of boosted decision trees for MNIST handwritten digit classification.

This work is submitted to the [Digit Recognition Low Power and Speed Challenge @ ICIP 2025](https://mlunglma.github.io/challenge.html)

## Paper
[Discretized Boosted Decision Trees for High-Speed
FPGA-Optimized Digit Recognition](./docs/paper.pdf)

## Reproduce Reports

Open the quartus/mnist_classifier.qpf project in Quartus Prime.

Compile the design to get the utilization and timing report.
Use the Power Analyzer Tool to get the power report.

The project is based on the SystemVerilog files from /fpga/hdl/. The following custom settings are used:
- Compiler Settings > Advanced Settings > Auto Shift Register Recognition = OFF
- Optimization mode > Balanced (Normal flow)


### Get accuracy on MNIST test set:

Install SystemVerilog simulator: `sudo apt update && sudo apt install iverilog`
Install python dependecies: `pip install torch torchvision matplotlib cocotb pytest`

Run the SystemVerilog mnist_classifier on the full MNIST test set with: `cd fpga/tests/ && python runner.py classifier`

## Generate Verilog Code for a new boosted tree

### Install dependencies:

Run: `pip install torch torchvision matplotlib cocotb pytest`

### Install fork of xgboost:

Clone forked xgboost (with leaf value discretization):
`git clone --recursive https://github.com/martinloretzzz/xgboost`

Build the fork from source and install python package (see the [XGBoost documentation for details](https://xgboost.readthedocs.io/en/stable/build.html)):
`cmake -B build -S . -DCMAKE_BUILD_TYPE=RelWithDebInfo -GNinja   -DCMAKE_BUILD_WITH_INSTALL_RPATH=O`  
`cd build && ninja`  
`cd python-package && pip install .`

### Train boosted tree

Run the following command to train the boosted tree and export the model to `model.json`:
`python train_boosted_tree.py`

### Generate SystemVerilog Code:

Run the following command to generate the boosted tree-specific SystemVerilog files: _decision_trees.sv_, _leaf_counters.sv_, _mnist_classifier.sv_:
`python generate_verilog.py`
