import os
import glob
import numpy as np
import cv2
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
import matplotlib.pyplot as plt
from tqdm import tqdm  # 进度条库
import json

class CityscapesDataset(Dataset):
    def __init__(self, image_paths, label_paths, transform=None):
        self.image_paths = image_paths
        self.label_paths = label_paths
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image = cv2.imread(self.image_paths[idx])
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        label = cv2.imread(self.label_paths[idx], cv2.IMREAD_GRAYSCALE)
        
        if self.transform:
            image = self.transform(image)
        
        label = cv2.resize(label, (image.shape[2], image.shape[1]), interpolation=cv2.INTER_NEAREST)
        label = torch.from_numpy(label).long()
        
        # 确保标签在有效范围内
        label[label >= 20] = 19  # 假设19是最高的有效类索引

        return image, label


DATA_DIR = r'dataset'
x_train_dir = os.path.join(DATA_DIR, 'train_images/*.png')
y_train_dir = os.path.join(DATA_DIR, 'train_labels/*.png')
x_valid_dir = os.path.join(DATA_DIR, 'valid_images/*.png')
y_valid_dir = os.path.join(DATA_DIR, 'valid_labels/*.png')


# 获取所有图像和标签的路径
image_paths = sorted(glob.glob(x_train_dir))
label_paths = sorted(glob.glob(y_train_dir))
# 确保路径数量一致
assert len(image_paths) == len(label_paths)

# 数据增强和预处理
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((256, 512)),
    transforms.ToTensor(),
])

dataset = CityscapesDataset(image_paths, label_paths, transform=transform)
dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

# 验证集加载
# val_image_paths = sorted(glob.glob('task3/dataset/leftImg8bit_trainvaltest/leftImg8bit/val/*_leftImg8bit.png'))
# val_label_paths = sorted(glob.glob('task3/dataset/gtFine/val/*_gtFine_labelIds.png'))

val_dataset = CityscapesDataset(val_image_paths, val_label_paths, transform=transform)
val_dataloader = DataLoader(val_dataset, batch_size=4, shuffle=False)

class DoubleConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(DoubleConv, self).__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.double_conv(x)

class UNet(nn.Module):
    def __init__(self, num_classes):
        super(UNet, self).__init__()
        self.enc1 = DoubleConv(3, 64)
        self.enc2 = DoubleConv(64, 128)
        self.enc3 = DoubleConv(128, 256)
        self.enc4 = DoubleConv(256, 512)
        self.enc5 = DoubleConv(512, 1024)

        self.pool = nn.MaxPool2d(2)

        self.up4 = nn.ConvTranspose2d(1024, 512, kernel_size=2, stride=2)
        self.dec4 = DoubleConv(1024, 512)
        self.up3 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.dec3 = DoubleConv(512, 256)
        self.up2 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.dec2 = DoubleConv(256, 128)
        self.up1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.dec1 = DoubleConv(128, 64)

        self.final = nn.Conv2d(64, num_classes, kernel_size=1)

    def forward(self, x):
        enc1 = self.enc1(x)
        enc2 = self.enc2(self.pool(enc1))
        enc3 = self.enc3(self.pool(enc2))
        enc4 = self.enc4(self.pool(enc3))
        enc5 = self.enc5(self.pool(enc4))

        dec4 = self.up4(enc5)
        dec4 = torch.cat((dec4, enc4), dim=1)
        dec4 = self.dec4(dec4)
        dec3 = self.up3(dec4)
        dec3 = torch.cat((dec3, enc3), dim=1)
        dec3 = self.dec3(dec3)
        dec2 = self.up2(dec3)
        dec2 = torch.cat((dec2, enc2), dim=1)
        dec2 = self.dec2(dec2)
        dec1 = self.up1(dec2)
        dec1 = torch.cat((dec1, enc1), dim=1)
        dec1 = self.dec1(dec1)

        return self.final(dec1)

# 实例化模型
model = UNet(num_classes=20)
model = model.cuda()



criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 训练模型
num_epochs = 1
for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    with tqdm(total=len(dataloader), desc=f"Epoch {epoch+1}/{num_epochs}", unit="batch") as pbar:
        for images, labels in dataloader:
            images = images.cuda()
            labels = labels.cuda()

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            pbar.set_postfix(loss=running_loss/(pbar.n + 1))
            pbar.update(1)
    
    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {running_loss/len(dataloader)}")

    # 验证模型
    model.eval()
    val_loss = 0.0
    with torch.no_grad():
        for images, labels in val_dataloader:
            images = images.cuda()
            labels = labels.cuda()
            
            outputs = model(images)
            loss = criterion(outputs, labels)
            val_loss += loss.item()
    
    print(f"Validation Loss: {val_loss/len(val_dataloader)}")


# 选择一些测试图像进行预测
test_images, test_labels = next(iter(val_dataloader))
test_images = test_images.cuda()
test_labels = test_labels.cuda()

# 进行预测
model.eval()
with torch.no_grad():
    predictions = model(test_images)
predictions = torch.argmax(predictions, dim=1).cpu().numpy()



# 获取轮廓（多边形）并保存预测结果为JSON文件
def save_predictions_as_json(image_paths, predictions, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for i, image_path in enumerate(image_paths):
        filename = os.path.basename(image_path).replace('_leftImg8bit.png', '_prediction.json')
        output_path = os.path.join(output_dir, filename)
        
        # 将预测结果转换为列表格式
        prediction_list = predictions[i].tolist()
        
        objects = []
        for label in np.unique(predictions[i]):
            if label == 19:
                continue  # 忽略背景
            mask = (predictions[i] == label).astype(np.uint8)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                polygon = contour.squeeze().tolist()
                if len(polygon) < 3:
                    continue  # 忽略非多边形
                objects.append({
                    "label": str(label),
                    "polygon": polygon
                })
        
        json_data = {
            "imgHeight": predictions[i].shape[0],
            "imgWidth": predictions[i].shape[1],
            "objects": objects
        }
        
        with open(output_path, 'w') as json_file:
            json.dump(json_data, json_file,indent=4)

# 示例：将预测结果保存为JSON文件
test_image_paths = val_image_paths[:4]  # 获取批量中的图像路径
output_dir = 'task3/dataset/predictions'
save_predictions_as_json(test_image_paths, predictions, output_dir)



# 将预测结果转换为类别标签并可视化
for i in range(4):  # 批量大小为4
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.title('Original Image')
    plt.imshow(test_images[i].permute(1, 2, 0).cpu().numpy())
    
    plt.subplot(1, 3, 2)
    plt.title('Ground Truth')
    plt.imshow(test_labels[i].cpu().numpy(), cmap='gray')
    
    plt.subplot(1, 3, 3)
    plt.title('Prediction')
    plt.imshow(predictions[i], cmap='gray')
    
    plt.show()


