import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import numpy as np
import time
import matplotlib

matplotlib.rcParams['font.sans-serif'] = ['PingFang SC']  # macOS 推荐
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号

# 检查是否可用 MPS (M1 GPU 加速)
device = (
    "mps"
    if torch.backends.mps.is_available()
    else "cuda"
    if torch.cuda.is_available()
    else "cpu"
)
print(f"使用设备: {device}")

# 设置随机种子以确保结果可复现
torch.manual_seed(42)

# 数据预处理和加载
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))  # MNIST 数据集的均值和标准差
])

# 加载 MNIST 数据集
train_dataset = datasets.MNIST(
    'assets/data', train=True, download=True, transform=transform)
test_dataset = datasets.MNIST(
    'assets/data', train=False, download=True,transform=transform)

# 创建数据加载器
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=1000)

print(f"训练集大小: {len(train_dataset)}")
print(f"测试集大小: {len(test_dataset)}")

# 定义 CNN 模型
class MNISTModel(nn.Module):
    def __init__(self):
        super(MNISTModel, self).__init__()
        # 第一个卷积层
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
        self.pool1 = nn.MaxPool2d(kernel_size=2)

        # 第二个卷积层
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.pool2 = nn.MaxPool2d(kernel_size=2)

        # 全连接层
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        # 第一个卷积块
        x = self.pool1(F.relu(self.conv1(x)))

        # 第二个卷积块
        x = self.pool2(F.relu(self.conv2(x)))

        # 展平
        x = x.view(-1, 64 * 7 * 7)

        # 全连接层
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)

        return x


# 实例化模型并移至设备
model = MNISTModel().to(device)
print(model)

# 定义损失函数和优化器
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 训练函数
def train(model, device, train_loader, optimizer, epoch, log_interval=100):
    model.train()
    train_loss = 0
    correct = 0
    total = 0

    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)

        # 梯度清零
        optimizer.zero_grad()

        # 前向传播
        output = model(data)

        # 计算损失
        loss = criterion(output, target)

        # 反向传播
        loss.backward()

        # 优化参数
        optimizer.step()

        # 累计损失
        train_loss += loss.item()

        # 计算准确率
        _, predicted = output.max(1)
        total += target.size(0)
        correct += predicted.eq(target).sum().item()

        # 打印训练进度
        if batch_idx % log_interval == 0:
            print(f'训练轮次: {epoch} [{batch_idx * len(data)}/{len(train_loader.dataset)} '
                  f'({100. * batch_idx / len(train_loader):.0f}%)]\t'
                  f'损失: {loss.item():.6f}\t'
                  f'准确率: {100. * correct / total:.2f}%')

    return train_loss / len(train_loader), 100. * correct / total

# 测试函数
def test(model, device, test_loader):
    model.eval()
    test_loss = 0
    correct = 0

    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += criterion(output, target).item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader)
    accuracy = 100. * correct / len(test_loader.dataset)

    print(
        f'\n测试集: 平均损失: {test_loss:.4f}, 准确率: {correct}/{len(test_loader.dataset)} ({accuracy:.2f}%)\n')

    return test_loss, accuracy


# 训练模型
epochs = 10
train_losses = []
train_accuracies = []
test_losses = []
test_accuracies = []

start_time = time.time()

for epoch in range(1, epochs + 1):
    train_loss, train_acc = train(
        model, device, train_loader, optimizer, epoch)
    test_loss, test_acc = test(model, device, test_loader)

    train_losses.append(train_loss)
    train_accuracies.append(train_acc)
    test_losses.append(test_loss)
    test_accuracies.append(test_acc)

training_time = time.time() - start_time
print(f"训练用时: {training_time:.2f} 秒")

# 保存模型
torch.save(model.state_dict(), "assets/models/mnist_pytorch_model.pth")
print("模型已保存为 mnist_pytorch_model.pth")

# 可视化训练过程
plt.figure(figsize=(12, 5))

# 准确率曲线
plt.subplot(1, 2, 1)
plt.plot(train_accuracies, label='训练准确率')
plt.plot(test_accuracies, label='测试准确率')
plt.title('模型准确率')
plt.xlabel('轮次')
plt.ylabel('准确率 (%)')
plt.legend()

# 损失函数曲线
plt.subplot(1, 2, 2)
plt.plot(train_losses, label='训练损失')
plt.plot(test_losses, label='测试损失')
plt.title('模型损失')
plt.xlabel('轮次')
plt.ylabel('损失')
plt.legend()

plt.tight_layout()
plt.savefig('assets/images/machine_learning/pytorch_training_history.png')
plt.show()

# 测试几个样本并可视化
def visualize_predictions(model, device, test_loader, num_samples=5):
    model.eval()

    # 获取一批数据
    dataiter = iter(test_loader)
    images, labels = next(dataiter)

    # 选择前 num_samples 个样本
    images = images[:num_samples].to(device)
    labels = labels[:num_samples]

    # 预测
    with torch.no_grad():
        outputs = model(images)
        _, predicted = torch.max(outputs, 1)

    # 将图像转回 CPU 以便显示
    images = images.cpu().numpy()

    # 显示图像和预测结果
    plt.figure(figsize=(15, 3))
    for i in range(num_samples):
        plt.subplot(1, num_samples, i + 1)
        plt.imshow(images[i][0], cmap='gray')
        color = 'green' if predicted[i] == labels[i] else 'red'
        plt.title(f"真实: {labels[i]}\n预测: {predicted[i]}", color=color)
        plt.axis('off')

    plt.tight_layout()
    plt.savefig('assets/images/machine_learning/pytorch_sample_predictions.png')
    plt.show()


# 创建一个小的测试加载器用于可视化
test_loader_vis = DataLoader(test_dataset, batch_size=5, shuffle=True)
visualize_predictions(model, device, test_loader_vis)

# 在整个测试集上进行最终评估
final_test_loss, final_test_acc = test(model, device, test_loader)
print(f"最终测试准确率: {final_test_acc:.2f}%")
