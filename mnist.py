# pip install matplotlib wandb scikit-learn

from types import SimpleNamespace
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import StepLR, CosineAnnealingLR, LinearLR, SequentialLR
import wandb

# Conv Accuracy: 99.19% (14 epochs)
# Linear Accuracy: 98.10% (10 epochs)
# Binarized Input: 97.49 (10 epochs, 100k params)
# Binarized Input: 98.05 (10 epochs, 100k params, batchnorm)
# Binarized Input: 97.94 (10 epochs, 100k params, batchnorm, dropout)
# Binarized Input: 97.88 (10 epochs, 100k params, batchnorm, no bias)
# Remove unused pixels: 97.95 (10 epochs, 84k params, from 98.05)
# Smaller network: 97.55 (10 epochs, 40k params, from 97.95)
# Single Layer Network: 92.05 (10 epochs)

unused_pixel_mask = ~torch.load("mnist_unused_mask.pth", weights_only=True).view(-1)

class BinaryActivation(torch.autograd.Function):
    @staticmethod
    def forward(ctx, input):
        return 0.25 * ((input > 0.0).float())

    @staticmethod
    def backward(ctx, grad_output):
        return F.hardtanh(grad_output)
    
class BinActive(torch.autograd.Function):
    @staticmethod
    def forward(ctx, input):
        ctx.save_for_backward(input)
        input = 0.25 * input.sign()
        return input 

    @staticmethod
    def backward(ctx, grad_output):
        input, = ctx.saved_tensors
        grad_input = grad_output.clone()
        grad_input[input.ge(1)] = 0
        grad_input[input.le(-1)] = 0
        return grad_input

class BinaryActivationLayer(nn.Module):
    def __init__(self):
        super(BinaryActivationLayer, self).__init__()

    def forward(self, x):
        return BinActive.apply(x)

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        in_feature_count = unused_pixel_mask.sum().item()
        self.ln1 = nn.Linear(in_feature_count, 1024)
        self.ln2 = nn.Linear(1024, 10)
        self.binary_act1 = BinaryActivationLayer()

    def forward(self, x):
        x = x.flatten(1)
        hid0 = x
        x = self.ln1(x)
        x = self.binary_act1(x)
        hid1 = x
        x = self.ln2(x)
        output = F.log_softmax(x, dim=1)
        hid2 = F.one_hot(torch.argmax(output, dim=1), num_classes=output.shape[-1])
        return output, [hid0, hid1, hid2]

def train(args, model, device, train_loader, optimizer, epoch):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output, hidden = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % args.log_interval == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item()))
            wandb.log({"epoch": epoch, "train_loss": loss.item(), "lr": optimizer.param_groups[0]['lr']})
            if args.dry_run:
                break

def test(model, device, test_loader, epoch):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output, hidden = model(data)
            test_loss += F.nll_loss(output, target, reduction='sum').item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)
    accuracy = 100. * correct / len(test_loader.dataset)

    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset), accuracy))
    wandb.log({"test_loss": test_loss, "test_accuracy": accuracy, "epoch": epoch})

def collect_hidden(model, device, data_loader):
    model.eval()
    hiddens = []
    with torch.no_grad():
        for data, target in data_loader:
            data, target = data.to(device), target.to(device)
            output, hidden = model(data)
            hiddens.append([*hidden, target])

    hiddens = [torch.cat([h[i] for h in hiddens], dim=0) for i in range(len(hiddens[0]))]
    for i, hidden in enumerate(hiddens):
        name = i if i <= 2 else "target"
        torch.save(hidden, f"./hidden/mnist_hidden_{name}.pth")


class BinarizePreprocess(object):
    def __call__(self, x):
        x = x.flatten(1)
        x = x[:, unused_pixel_mask]
        return torch.where(x > 0.5, torch.tensor(1.0), torch.tensor(0.0))

def main():
    args = SimpleNamespace(
        batch_size=64,
        test_batch_size=1000,
        epochs=8,
        lr=0.004,
        no_accel=False,
        dry_run=False,
        seed=42,
        log_interval=200,
        save_model=False
    )

    wandb.init(project="mnist-fpga", config=vars(args))
    wandb.config.update({"model": "BinaryActivationNet", "optimizer": "AdamW"})  # Updated optimizer name

    use_accel = not args.no_accel and torch.cuda.is_available()
    torch.manual_seed(args.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    train_kwargs = {'batch_size': args.batch_size}
    test_kwargs = {'batch_size': args.test_batch_size}
    if use_accel:
        accel_kwargs = {'num_workers': 1, 'pin_memory': True, 'shuffle': True}
        train_kwargs.update(accel_kwargs)
        test_kwargs.update(accel_kwargs)

    transform = transforms.Compose([
        transforms.ToTensor(),
        BinarizePreprocess()
    ])
    dataset1 = datasets.MNIST('../data', train=True, download=True, transform=transform)
    dataset2 = datasets.MNIST('../data', train=False, transform=transform)
    train_loader = torch.utils.data.DataLoader(dataset1, **train_kwargs)
    test_loader = torch.utils.data.DataLoader(dataset2, **test_kwargs)

    model = Net().to(device)
    optimizer = optim.AdamW(model.parameters(), betas=(0.9, 0.999), lr=args.lr, weight_decay=0.0005)
    param_count = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Parameter Count: {param_count}")
    wandb.config.update({"parameter_count": param_count})

    scheduler = CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-6)
    for epoch in range(1, args.epochs + 1):
        train(args, model, device, train_loader, optimizer, epoch)
        test(model, device, test_loader, epoch)
        scheduler.step()
    collect_hidden(model, device, train_loader)

    if args.save_model:
        torch.save(model.state_dict(), "./mnist_model.pt")
        wandb.save("./mnist_model.pt")

if __name__ == '__main__':
    main()