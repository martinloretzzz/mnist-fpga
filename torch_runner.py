import json
from collections import Counter
import matplotlib.pyplot as plt
import torch
import torchvision

def extract_tree_to_logic(node, parents=None):
    if parents is None: 
        parents = []
    assert isinstance(node, dict)
    if "leaf" in node:
        return [(parents, node["leaf"])]
    if "children" in node:
        left_parents = [*parents, node["split"].replace("f", "n")]
        right_parents = [*parents, node["split"].replace("f", "p")]
        return [*extract_tree_to_logic(node["children"][0], left_parents),
                *extract_tree_to_logic(node["children"][1], right_parents)]


def trees_to_feature_arrays(trees, max_depth, positive_feature_count, num_classes = 10):
    one_feature_offset = 2 * positive_feature_count
    negative_feature_start = positive_feature_count

    leave_paths = []
    leave_values = []
    leave_classifier_ids = []
    for tree_id, tree in enumerate(trees):
        for leaf_nodes, value in tree:
            leave_classifier_ids.append(tree_id % num_classes)
            leave_values.append(value)
            leaf_feature_nodes = []
            for i in range(max_depth):
                feature_id = one_feature_offset
                if i < len(leaf_nodes):
                    if leaf_nodes[i].startswith("p"):
                        feature_id = int(leaf_nodes[i].replace("p", ""))
                    if leaf_nodes[i].startswith("n"):
                        feature_id = negative_feature_start + int(leaf_nodes[i].replace("n", ""))
                leaf_feature_nodes.append(feature_id)
            leave_paths.append(leaf_feature_nodes)
    return leave_paths, leave_values, leave_classifier_ids


def binarize(x):
    x = x.flatten(1)
    return torch.where(x > 0.3, torch.tensor(1.0), torch.tensor(0.0))

def convert_to_numpy(dataset, to_numpy=True):
    data = []
    labels = []
    for img, label in dataset:
        data.append(img)
        labels.append(label)
    data = binarize(torch.cat(data, dim=0))
    labels = torch.tensor(labels)
    if to_numpy:
        data, labels = data.numpy(), labels.numpy()
    return data, labels

def image_full_feature_space(data):
    data = data.bool()
    negative_data = ~data
    ones_data = torch.ones((data.shape[0], 1), dtype=torch.bool, device=data.device)
    return torch.cat((data, negative_data, ones_data),  dim=-1)


train_dataset = torchvision.datasets.MNIST(root='./data', train=True, download=True, transform=torchvision.transforms.ToTensor())
test_dataset = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=torchvision.transforms.ToTensor())

# X_train, y_train = convert_to_numpy(train_dataset, to_numpy=False)
x_test, y_test = convert_to_numpy(test_dataset, to_numpy=False)

file_path = "model.json"
data = json.load(open(file_path, 'r'))

trees = [extract_tree_to_logic(tree) for tree in data]

leave_paths, leave_values, leave_classifier_ids = trees_to_feature_arrays(trees, max_depth=4, positive_feature_count=28*28)
leave_paths = torch.tensor(leave_paths, dtype=torch.long)
leave_values = torch.tensor(leave_values, dtype=torch.float)
leave_classifier_ids = torch.tensor(leave_classifier_ids, dtype=torch.long)

x_features = image_full_feature_space(x_test)

def run_model(x_features):
    batch_size = x_features.size(0)

    active_nodes = x_features[torch.arange(batch_size).unsqueeze(1), leave_paths.view(-1)]
    active_nodes = active_nodes.view(batch_size, -1, 4)
    active_leaves = torch.all(active_nodes, dim=-1)

    class_scores = []
    for i in range(10):
        classifier_mask = leave_classifier_ids == i
        active_leave_values = leave_values * active_leaves.float() * classifier_mask.float()
        tree_score = active_leave_values.sum(-1)
        class_scores.append(tree_score)

    class_scores = torch.stack(class_scores, dim=-1)
    return class_scores

class_scores = run_model(x_features)
y_pred = class_scores.argmax(-1)
accuracy = (y_pred == y_test).sum().item() / y_test.numel()

print(f"Accuracy: {accuracy}")
print(y_pred[0:4])
print(y_test[0:4])