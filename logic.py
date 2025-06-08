import numpy as np
import torch
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import export_text

hid1 = torch.load("./hidden/mnist_hidden_1.pth", weights_only=True)
hid2 = torch.load("./hidden/mnist_hidden_2.pth", weights_only=True)

hid1 = (hid1 >= 0).float()

total_and = 0
total_or = 0
for label in range(10):
    X = np.array(hid1.cpu().numpy())
    y = np.array(hid2[:,label].cpu().numpy())

    # Train decision tree
    clf = DecisionTreeClassifier(criterion='gini', max_depth=12, random_state=42)
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
            left_conditions = conditions + [f"~{feature}" if threshold > 0.5 else f"{feature}"]
            right_conditions = conditions + [f"{feature}" if threshold > 0.5 else f"~{feature}"]
            
            left_paths = recurse(tree_.children_left[node], left_conditions)
            right_paths = recurse(tree_.children_right[node], right_conditions)
            return left_paths + right_paths

        paths = recurse(0, [])
        # Combine paths for output = 1
        if not paths:
            return "0"
        and_count = sum([len(path) - 1 for path in paths])
        or_count = len(paths) - 1
        minterms = ["(" + (" & ".join(path)) + ")" for path in paths]
        return " | ".join(minterms), and_count, or_count


    print("=============================================")
    print(f"Decision Tree for label {label}")
    print("=============================================")

    # Get Boolean expression
    logic_expr, and_count, or_count = tree_to_logic(clf, [f"A{i}" for i in range(X.shape[1])])
    # print("Boolean Expression:", logic_expr)
    print(f"And gates: {and_count}")
    print(f"Or gates: {or_count}")
    total_and += and_count
    total_or += or_count

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
