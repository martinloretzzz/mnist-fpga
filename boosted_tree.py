# pip install torch torchvision scikit-learn matplotlib

# cmake -B build -S . -DCMAKE_BUILD_TYPE=RelWithDebInfo -GNinja -DCMAKE_BUILD_WITH_INSTALL_RPATH=O -DUSE_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=75 -DCMAKE_INSTALL_PREFIX=/opt/conda
# https://xgboost.readthedocs.io/en/stable/build.html

# echo "set -g mouse on" >> ~/.tmux.conf && tmux source-file ~/.tmux.conf

import xgboost as xgb
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report
import torch
import torchvision
import torchvision.transforms as transforms
import joblib
import os

XGBOOST = True
#MODEL_PATH = "model.joblib"
#LOAD_MODEL = False
DUMP = True

np.random.seed(42)
torch.manual_seed(42)
torch.set_printoptions(linewidth=200)

train_dataset = torchvision.datasets.MNIST(root='./data', train=True, download=True, transform=transforms.ToTensor())
test_dataset = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transforms.ToTensor())

def binarize(x):
    x = x.flatten(1)
    return torch.where(x > 0.3, torch.tensor(1.0), torch.tensor(0.0))

def convert_to_numpy(dataset):
    data = []
    labels = []
    for img, label in dataset:
        data.append(img)
        labels.append(label)
    data = binarize(torch.cat(data, dim=0)).numpy()
    return np.array(data), np.array(labels)

X_train, y_train = convert_to_numpy(train_dataset)
X_test, y_test = convert_to_numpy(test_dataset)

model = xgb.XGBClassifier(
    learning_rate=0.5,
    n_estimators=100,
    tree_method="hist",
    objective="multi:softmax",
    num_class=10,
    max_depth=4,
    subsample=0.8,
    min_child_weight=3,
    reg_lambda=1.0,  # L2 regularization
    reg_alpha=0.1,   # L1 regularization
    random_state=42
)

"""
if MODEL_PATH is not None:
    if LOAD_MODEL and os.path.exists(MODEL_PATH):
        print(f"Loading pre-trained model from {MODEL_PATH}")
        model = joblib.load(MODEL_PATH)
    else:
        print("Training new model...")
        model.fit(X_train, y_train)
        print(f"Saving model to {MODEL_PATH}")
        joblib.dump(model, MODEL_PATH)
"""

model.fit(X_train, y_train)
y_pred = model.predict(X_test)


accuracy = accuracy_score(y_test, y_pred)
print(f"\nTest Accuracy: {accuracy:.4f}")
# print("\nClassification Report:")
# print(classification_report(y_test, y_pred))

if DUMP:
    booster = model.get_booster()
    booster_dump = booster.get_dump()
    params = model.get_params()
    print(booster_dump[0])
    booster.dump_model("model.json", dump_format="json")
