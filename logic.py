import numpy as np
import torch
import torch.nn as nn
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import export_text
from tqdm import tqdm
import concurrent.futures
import pickle
from xgboost import XGBClassifier
import xgboost as xgb
import matplotlib.pyplot as plt

normal_repr = torch.Tensor.__repr__
torch.Tensor.__repr__ = lambda self: f"{self.shape} {normal_repr(self)}"

# Connections are indexed in the following way:
# 0: Not connected, value always 1
# 1..n+1: Positive feature
# n+1..2n+1: Negative feature

def train_xgboost(hid_in, hid_out):
    X = np.array(hid_in.long().cpu().numpy())
    y = np.array(hid_out.long().cpu().numpy())

    print(hid_out.unique())


    """
    model = XGBClassifier(
        n_estimators=75,
        max_depth=6,
        subsample=0.8,
        min_child_weight=3,
        reg_lambda=1.0,  # L2 regularization
        reg_alpha=0.1,   # L1 regularization
        random_state=42
    )
    """

    model = XGBClassifier(
        n_estimators=200,
        max_depth=3,
        subsample=0.8,
        min_child_weight=3,
        reg_lambda=1.0,  # L2 regularization
        reg_alpha=0.1,   # L1 regularization
        random_state=42
    )
    model.fit(X, y)
    booster = model.get_booster()
    booster_dump = booster.get_dump()

    """
    for i in range(model.n_estimators):
        xgb.plot_tree(model, num_trees=i)
        plt.savefig(f'hidden/xgb/tree_{i}.png', dpi=300)  # Save each tree as an image
        plt.close()
    """

    y_pred = model.predict(X)
    correct = np.sum(y_pred == y)
    print(f"Correct rows: {correct}/{len(y)}")
    print(f"Accuracy: {correct / len(y) * 100:.2f}%")
    print(f"Error: {(len(y) - correct) / len(y) * 100:.2f}%")
    return model, y_pred

def get_logic_for_layer(hid_in, hid_out, max_depth=None, save_tree_prefix=None, random_forest=False, random_forest_n_estimators=100, max_workers=None):
    def process_feature(fid):
        return get_logic_for_feature(hid_in, hid_out, fid, max_depth, save_tree_prefix, random_forest, random_forest_n_estimators)
    
    if max_workers is None:
        max_workers = min(32, hid_out.shape[1])
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(tqdm(executor.map(process_feature, range(hid_out.shape[1])), total=hid_out.shape[1]))

    return torch.stack(results, dim=1)

def get_logic_for_feature(hid_in, hid_out, feature_id, max_depth=None, save_tree_prefix=None, random_forest=False, random_forest_n_estimators=100):
    X = np.array(hid_in.long().cpu().numpy())
    y = np.array(hid_out[:,feature_id].long().cpu().numpy())

    # Train decision tree
    if random_forest:
        clf = RandomForestClassifier(n_estimators=random_forest_n_estimators, random_state=42)
        clf.fit(X, y)
    else:
        assert max_depth is not None
        clf = DecisionTreeClassifier(criterion='gini', max_depth=max_depth, random_state=42)
        clf.fit(X, y)

    if save_tree_prefix is not None:
        with open(f'{save_tree_prefix}_{feature_id}.pkl', 'wb') as file:
            pickle.dump(clf, file)

    # tree_rules = export_text(clf, feature_names=[f"A{i}" for i in range(X.shape[1])])
    # print("Decision Tree Rules:\n", tree_rules)

    y_pred = clf.predict(X)
    correct = np.sum(y_pred == y)
    print("=============================================")
    print(f"Decision Tree for feature {feature_id}")
    print("=============================================")
    print(f"Correct rows: {correct}/{len(y)}")
    print(f"Accuracy: {correct / len(y) * 100:.2f}%")
    print(f"Error: {(len(y) - correct) / len(y) * 100:.2f}%")
    return torch.from_numpy(y_pred)


# depth 5 => 32 nodes

# first layer
"""
hid0 = torch.load("./hidden/mnist_hidden_0.pth", weights_only=True)
hid1 = torch.load("./hidden/mnist_hidden_1.pth", weights_only=True)
hid1 = (hid1 >= 0).float()

layer0_all_pred = get_logic_for_layer(hid0, hid1, max_depth=3, save_tree_prefix="./hidden/tree_tmp/tree")
torch.save(layer0_all_pred, "./hidden/l0_pred_2048_d3.pth")
"""

# XGBoost
"""
hid1 = torch.load("./hidden/l0_pred_2048_d3.pth", weights_only=True)
hid_target = torch.load("./hidden/mnist_hidden_target.pth", weights_only=True)
print(f"Invlaid data: {hid_target[hid_target < 0]}")
hid_target[hid_target < 0] = 0


model, output = train_xgboost(hid1, hid_target)
with open("./hidden/l1_pred_xgboost_2048_l0_d3.pth", 'wb') as file: pickle.dump(model, file)
"""

# Random forest
"""
hid1 = torch.load("./hidden/l0_pred.pth", weights_only=True)
hid_target = torch.load("./hidden/mnist_hidden_target.pth", weights_only=True)
hid_target = hid_target.unsqueeze(-1)

layer1_all_pred = get_logic_for_layer(hid1, hid_target, random_forest=True, random_forest_n_estimators=100, save_tree_prefix="./hidden/tree_l1_rf")
torch.save(layer1_all_pred, "./hidden/l1_pred_rf_1024_x.pth")
"""


"""
hid1 = torch.load("./hidden/l0_pred.pth", weights_only=True)
hid_target = torch.load("./hidden/mnist_hidden_target.pth", weights_only=True)
hid_target = torch.nn.functional.one_hot(hid_target, num_classes=10)

layer1_conn, layer1_all_pred = get_logic_connections_for_layer(hid1, hid_target, max_depth=8, save_tree_prefix="./hidden/tree_l1/tree")
torch.save(layer1_all_pred, "./hidden/l1_pred.pth")
# #torch.save(layer1_conn, "./hidden/l1_conn.pth")
"""

# XGBoost Full
"""
hid0 = torch.load("./hidden/mnist_hidden_0.pth", weights_only=True)
hid_target = torch.load("./hidden/mnist_hidden_target.pth", weights_only=True)
print(f"Invlaid data: {hid_target[hid_target < 0]}")
hid_target[hid_target < 0] = 0

model, output = train_xgboost(hid0, hid_target)
with open("./hidden/l1_pred_xgboost_1024_single_layer.pth", 'wb') as file: pickle.dump(model, file)
"""
