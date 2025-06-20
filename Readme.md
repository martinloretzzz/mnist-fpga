## Install dependencies:

`pip install torch torchvision scikit-learn matplotlib`

## Build xgboost from source:

https://xgboost.readthedocs.io/en/stable/build.html

`cmake -B build -S . -DCMAKE_BUILD_TYPE=RelWithDebInfo -GNinja -DCMAKE_BUILD_WITH_INSTALL_RPATH=O -DUSE_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=75 -DCMAKE_INSTALL_PREFIX=/opt/conda`
`cd build && ninja`
`cd python-package && pip install .`

Update tmux config in vm: `echo "set -g mouse on" >> ~/.tmux.conf && tmux source-file ~/.tmux.conf`
