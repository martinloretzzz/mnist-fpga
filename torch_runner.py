import json
import torch
import torchvision
from tqdm import tqdm

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

    leaf_paths = []
    leaf_values = []
    leaf_classifier_ids = []
    for tree_id, tree in enumerate(trees):
        for leaf_nodes, value in tree:
            leaf_classifier_ids.append(tree_id % num_classes)
            leaf_values.append(value)
            leaf_feature_nodes = []
            for i in range(max_depth):
                feature_id = one_feature_offset
                if i < len(leaf_nodes):
                    if leaf_nodes[i].startswith("p"):
                        feature_id = int(leaf_nodes[i].replace("p", ""))
                    if leaf_nodes[i].startswith("n"):
                        feature_id = negative_feature_start + int(leaf_nodes[i].replace("n", ""))
                leaf_feature_nodes.append(feature_id)
            leaf_paths.append(leaf_feature_nodes)
    return leaf_paths, leaf_values, leaf_classifier_ids


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

leaf_paths, leaf_values, leaf_classifier_ids = trees_to_feature_arrays(trees, max_depth=4, positive_feature_count=28*28)

# TODO: Move verilog stuff to seperate file
def trees_to_sv(trees, num_classes=10):
    def leaf_to_logic(leaf):
        return " && ".join([f"{"!" if term.startswith("n") else ""}f[{term[1:]}]" for term in leaf])
    
    leaf_id = 0
    statements = []
    for tree_id, tree in enumerate(trees):
        statements.append(f"// Tree {tree_id}, Classifier {tree_id % num_classes}, Iteration: {tree_id // num_classes}")
        for leaf, value in tree:
            statements.append(f"assign leaf[{leaf_id}] = {leaf_to_logic(leaf)};")
            leaf_id += 1
        statements.append("")
    
    return f"""module decision_tree_leaves(input logic [0:{28*28-1}] f, output logic [0:{leaf_id-1}] leaf);
{"\n\t".join(statements)}
endmodule"""

tree_leaves_sv = trees_to_sv(trees)
print(tree_leaves_sv)

with open("./fpga/hdl/decision_tree_leaves.sv", "w") as f:
    f.write(tree_leaves_sv)

leaf_paths = torch.tensor(leaf_paths, dtype=torch.long)
leaf_values = torch.tensor(leaf_values, dtype=torch.float)
leaf_classifier_ids = torch.tensor(leaf_classifier_ids, dtype=torch.long)

x_features = image_full_feature_space(x_test)


def run_model(x_features, use_fast_torch_adder=False):
    batch_size = x_features.size(0)

    active_nodes = x_features[torch.arange(batch_size).unsqueeze(1), leaf_paths.view(-1)]
    active_nodes = active_nodes.view(batch_size, -1, 4)
    active_leaves = torch.all(active_nodes, dim=-1)

    class_scores = []
    if use_fast_torch_adder:
        for i in range(10):
            classifier_mask = leaf_classifier_ids == i
            active_leave_values = leaf_values * active_leaves.float() * classifier_mask.float()
            tree_score = active_leave_values.sum(-1)
            class_scores.append(tree_score)
    
    if not use_fast_torch_adder:
        unique_leaf_values, _ = torch.sort(leaf_values.unique())
        for i in tqdm(range(10)):
            classifier_mask = leaf_classifier_ids == i
            count_map = {}
            for value in list(unique_leaf_values):
                leaf_value_mask = leaf_values == value
                active_leaf_values = leaf_value_mask & active_leaves & classifier_mask
                active_leaf_count = active_leaf_values.sum(-1)
                count_map[value.item()] = active_leaf_count.to(torch.int8)

            negative_score = count_map[-0.015625]
            negative_score = (negative_score >> 1) + count_map[-0.03125]
            negative_score = (negative_score >> 1) + count_map[-0.0625]
            negative_score = (negative_score >> 1) + count_map[-0.125]
            negative_score = (negative_score >> 1) + count_map[-0.25]

            positive_score = count_map[0.015625]
            positive_score = (positive_score >> 1) + count_map[0.03125]
            positive_score = (positive_score >> 1) + count_map[0.0625]
            positive_score = (positive_score >> 1) + count_map[0.125]
            positive_score = (positive_score >> 1) + count_map[0.25]
            positive_score = positive_score + (count_map[0.5] << 0)
            positive_score = positive_score + (count_map[1.0] << 1)
            positive_score = positive_score + (count_map[2.0] << 2)

            # print(torch.max(negative_score, dim=-1)[0], torch.max(positive_score, dim=-1)[0])

            # both scores are in base 0.25
            tree_score = -negative_score + positive_score
            class_scores.append(tree_score)

    class_scores = torch.stack(class_scores, dim=-1)
    return class_scores

class_scores = run_model(x_features)
y_pred = class_scores.argmax(-1)
accuracy = (y_pred == y_test).sum().item() / y_test.numel()

print(f"Accuracy: {accuracy}")
print(y_pred[0:4])
print(y_test[0:4])