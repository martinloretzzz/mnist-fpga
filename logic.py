import numpy as np
import torch
import torch.nn as nn
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import export_text
from tqdm import tqdm

normal_repr = torch.Tensor.__repr__
torch.Tensor.__repr__ = lambda self: f"{self.shape} {normal_repr(self)}"

hid0 = torch.load("./hidden/mnist_hidden_0.pth", weights_only=True)
hid1 = torch.load("./hidden/mnist_hidden_1.pth", weights_only=True)
hid2 = torch.load("./hidden/mnist_hidden_2.pth", weights_only=True)
hid1 = (hid1 >= 0).float()

# Connections are indexed in the following way:
# 0: Not connected, value always 1
# 1..n+1: Positive feature
# n+1..2n+1: Negative feature


def get_logic_connections_for_layer(hid_in, hid_out, max_depth):
    in_feature_count = hid_in.shape[1]
    out_feature_count = hid_out.shape[1]

    conns = []
    total_and = 0
    total_or = 0
    for feature_id in tqdm(range(out_feature_count)):
        X = np.array(hid_in.long().cpu().numpy())
        y = np.array(hid_out[:,feature_id].long().cpu().numpy())

        # Train decision tree
        clf = DecisionTreeClassifier(criterion='gini', max_depth=max_depth, random_state=42)
        clf.fit(X, y)

        logic_terms = [f"A{i}" for i in range(X.shape[1])]

        # Extract tree structure as text
        # tree_rules = export_text(clf, feature_names=[f"A{i}" for i in range(X.shape[1])])
        # print("Decision Tree Rules:\n", tree_rules)

        # Convert tree to Boolean expression
        def tree_to_logic(tree, feature_names):
            tree_ = tree.tree_
            def recurse(node, conditions):
                if tree_.feature[node] == -2:  # Leaf node
                    if tree_.value[node][0][1] > tree_.value[node][0][0]:  # Predict 1
                        return [conditions]
                    return []
                
                feature = feature_names[tree_.feature[node]]
                threshold = tree_.threshold[node]
                # For Boolean features, threshold is typically 0.5
                left_conditions = conditions + [f"~{feature}" if threshold >= 0.5 else f"{feature}"]
                right_conditions = conditions + [f"{feature}" if threshold >= 0.5 else f"~{feature}"]
                
                left_paths = recurse(tree_.children_left[node], left_conditions)
                right_paths = recurse(tree_.children_right[node], right_conditions)
                return left_paths + right_paths

            paths = recurse(0, [])

            conn = torch.zeros((len(paths), max_depth), dtype=torch.long)
            for ip, path in enumerate(paths):
                for it, term in enumerate(path):
                    if term.startswith("~"):
                        conn[ip, it] = 1 + in_feature_count + int(term.replace("~A", ""))
                    else:
                        conn[ip, it] = 1 + int(term.replace("A", ""))

            # Combine paths for output = 1
            if not paths:
                return "0"
            and_count = sum([len(path) - 1 for path in paths])
            or_count = len(paths) - 1
            minterms = ["(" + (" & ".join(path)) + ")" for path in paths]
            return " | ".join(minterms), conn, and_count, or_count


        print("=============================================")
        print(f"Decision Tree for feature {feature_id}")
        print("=============================================")

        # Get Boolean expression
        logic_expr, conn, and_count, or_count = tree_to_logic(clf, [f"A{i}" for i in range(X.shape[1])])
        # print("Boolean Expression:", logic_expr)
        print(f"And gates: {and_count}")
        print(f"Or gates: {or_count}")
        total_and += and_count
        total_or += or_count
        conns.append(conn)

        print(f"Total nodes: {clf.tree_.node_count}")
        print(f"Internal nodes: {clf.tree_.node_count - clf.tree_.n_leaves}")
        print(f"Leaf nodes: {clf.tree_.n_leaves}")

        # Evaluate accuracy
        y_pred = clf.predict(X)
        correct = np.sum(y_pred == y)
        print(f"Correct rows: {correct}/{len(y)}")
        print(f"Accuracy: {correct / len(y) * 100:.2f}%")
        print(f"Error: {(len(y) - correct) / len(y) * 100:.2f}%")

    print("=============================================")
    print(f"Total And gates: {total_and}")
    print(f"Total Or gates: {total_or}")

    longest_con = max([c.shape[0] for c in conns])
    for i in range(len(conns)):
        if conns[i].shape[0] < longest_con:
            conns[i] = torch.cat([conns[i], torch.zeros((longest_con - conns[i].shape[0], conns[i].shape[1]), dtype=torch.long)], dim=0)
    all_conn = torch.stack(conns, dim=0)
    print(f"All connections shape: {all_conn.shape}")
    return all_conn

layer1_conn = get_logic_connections_for_layer(hid1, hid2, max_depth=20)
torch.save(layer1_conn, "./hidden/l1_conn.pth")

layer0_conn = get_logic_connections_for_layer(hid0, hid1, max_depth=20)
torch.save(layer0_conn, "./hidden/l0_conn.pth")
