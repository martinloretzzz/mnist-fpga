import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms
from mnist import BinarizePreprocess
from tqdm import tqdm
import os
import pickle
import re

normal_repr = torch.Tensor.__repr__
torch.Tensor.__repr__ = lambda self: f"{self.shape} {normal_repr(self)}"

"""
class BinaryLayer(nn.Module):
    def __init__(self, weight_path):
        super(BinaryLayer, self).__init__()
        weights = torch.load(weight_path, weights_only=True)
        or_padding_mask = ~torch.all(weights == 0, dim=-1)
        self.register_buffer('or_padding_mask', or_padding_mask)
        self.register_buffer('weights', weights)

    def forward(self, x):
        out_features, or_terms, and_terms = self.weights.shape
        B, F = x.shape
        x = x.bool()
        x_in = torch.cat([torch.ones((B, 1), dtype=torch.bool, device=x.device), x, ~x], dim=1)
        w_flat = self.weights.view(-1)
        x_sel = x_in[:, w_flat]
        x_bin = x_sel.view(B, out_features, or_terms, and_terms)
        x_and = torch.logical_and(torch.all(x_bin, dim=-1), self.or_padding_mask)
        x_or = torch.any(x_and, dim=-1)
        return x_or

class LogicNet(nn.Module):
    def __init__(self):
        super(LogicNet, self).__init__()
        self.l0 = BinaryLayer("./hidden/l0_conn.pth")
        self.l1 = BinaryLayer("./hidden/l1_conn_retrained.pth")

    def forward(self, x):
        x1 = self.l0(x)
        x2 = self.l1(x1)
        return x2, [x, x1, x2]
"""

device = "cpu" # "cuda" if torch.cuda.is_available() else "cpu"
# model = LogicNet().to(device)


class DesitionTreeLayer():
    def __init__(self, layer_path, is_random_forest=False):
        def get_tree_id(filename):
            match = re.match(r'tree_(\d+)\.pkl', filename)
            return int(match.group(1)) if match else float('inf')
        
        self.trees = []
        files = [f for f in os.listdir(layer_path) if os.path.isfile(os.path.join(layer_path, f))]
        files = sorted(files, key=get_tree_id)
        for tree_file in files:
            if tree_file.endswith('.pkl'):
                with open(os.path.join(layer_path, tree_file), 'rb') as file:
                    tree = pickle.load(file)
                self.trees.append(tree)
        self.out_features = len(self.trees)

    def __call__(self, x):
        x_np = x.cpu().numpy()
        result = []
        for i, tree in enumerate(self.trees):
            y_pred = tree.predict(x_np)
            result.append(torch.tensor(y_pred))
        result = torch.stack(result, dim=1)
        return result.bool()

class RandomForestLayer():
    def __init__(self, rf_path):
        with open(rf_path, 'rb') as file:
            self.random_forest = pickle.load(file)

    def __call__(self, x):
        x_np = x.cpu().numpy()
        y_pred = self.random_forest.predict(x_np)
        y_pred = torch.nn.functional.one_hot(torch.tensor(y_pred), num_classes=10)
        return y_pred.bool()


class DesitionTreeNet(nn.Module):
    def __init__(self):
        super(DesitionTreeNet, self).__init__()
        self.l0 = DesitionTreeLayer("./hidden/tree_l0/")
        self.l1 = RandomForestLayer("./hidden/tree_l1_rf_0.pkl")

    def forward(self, x):
        x = x.bool()
        x1 = self.l0(x)
        x2 = self.l1(x1)
        return x2, [x, x1, x2]

model = DesitionTreeNet()

transform = transforms.Compose([transforms.ToTensor(), BinarizePreprocess()])
dataset = datasets.MNIST('../data', train=False, transform=transform)
data_loader = torch.utils.data.DataLoader(dataset, batch_size=128, num_workers=1, shuffle=False)

dataset.data = dataset.data[0:10000]
dataset.targets = dataset.targets[0:10000]

def test(model, device, data_loader):
    model.eval()
    correct = 0
    hidden_outputs = []
    target_outputs = []
    with torch.no_grad():
        for data, target in tqdm(data_loader):
            data, target = data.squeeze(1).to(device), target.to(device)
            output, hidden = model(data)

            pred = output.float().argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()

            hidden_outputs.append(hidden[1])
            target_outputs.append(target)

    accuracy = 100. * correct / len(data_loader.dataset)

    print('\nTest set: Accuracy: {}/{} ({:.0f}%)\n'.format(
        correct, len(data_loader.dataset), accuracy))

    hidden_outputs = torch.cat(hidden_outputs, dim=0)
    target_outputs = F.one_hot(torch.cat(target_outputs, dim=0), num_classes=12).bool()

    # torch.save(hidden_outputs, f"./hidden/mnist_binary_retrain_{1}.pth")
    # torch.save(target_outputs, f"./hidden/mnist_binary_retrain_{2}.pth")
    
test(model, device, data_loader)
