import torch
import torch.nn as nn

normal_repr = torch.Tensor.__repr__
torch.Tensor.__repr__ = lambda self: f"{self.shape} {normal_repr(self)}"

hid1 = torch.load("./hidden/mnist_hidden_1.pth", weights_only=True)
hid2 = torch.load("./hidden/mnist_hidden_2.pth", weights_only=True)
hid1 = (hid1 >= 0).float()


class BinaryLayer(nn.Module):
    def __init__(self, weight_path, device):
        super(BinaryLayer, self).__init__()
        self.weights = torch.load(weight_path, weights_only=True).to(device)
        self.or_padding_mask = ~torch.all(self.weights == 0, dim=-1).to(device)


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

bin_layer = BinaryLayer("./hidden/l1_conn.pth", device=hid1.device)

test_batch_size = 10000
out = bin_layer(hid1[0:test_batch_size])
y_pred = torch.argmax(out.float(), dim=1)
y_true = torch.argmax(hid2[0:test_batch_size], dim=1)

print(f"Correct predictions: {torch.sum(y_pred == y_true)}/{len(y_true)}")
