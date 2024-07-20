import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score
from sklearn.feature_extraction.text import TfidfVectorizer
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import classification_report

# 1. 读取数据
file_path = 'task1/dataset/fake_job_postings.csv'
data = pd.read_csv(file_path)

# 2. 数据预处理
# 合并文本特征
data['text'] = (data['title'].fillna('') + ' ' + data['company_profile'].fillna('') + ' ' +
                data['description'].fillna('') + ' ' + data['requirements'].fillna('') + ' ' +
                data['benefits'].fillna(''))

# 选择特征和标签
features = data['text']
labels = data['fraudulent']

# 文本向量化
vectorizer = TfidfVectorizer(max_features=5000)
features_vectorized = vectorizer.fit_transform(features).toarray()

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(features_vectorized, labels, test_size=0.3, random_state=42)

# 将数据转换为 PyTorch 张量
X_train = torch.tensor(X_train, dtype=torch.float32).unsqueeze(1)  # [samples, timesteps, features]
X_test = torch.tensor(X_test, dtype=torch.float32).unsqueeze(1)    # [samples, timesteps, features]
y_train = torch.tensor(y_train.values, dtype=torch.float32)
y_test = torch.tensor(y_test.values, dtype=torch.float32)

# 创建 DataLoader
train_dataset = TensorDataset(X_train, y_train)
test_dataset = TensorDataset(X_test, y_test)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

# 3. 构建LSTM模型
class LSTMClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(LSTMClassifier, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        h_0 = torch.zeros(1, x.size(0), 50)
        c_0 = torch.zeros(1, x.size(0), 50)
        lstm_out, _ = self.lstm(x, (h_0, c_0))
        out = self.fc(lstm_out[:, -1, :])
        out = self.sigmoid(out)
        return out

# 模型参数
input_dim = X_train.shape[2]
hidden_dim = 50
output_dim = 1

# 初始化模型
model = LSTMClassifier(input_dim, hidden_dim, output_dim)

# 定义损失函数和优化器
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 4. 训练模型
num_epochs = 10
for epoch in range(num_epochs):
    model.train()
    for X_batch, y_batch in train_loader:
        optimizer.zero_grad()
        outputs = model(X_batch).squeeze()
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()
    print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

# 5. 评估模型
model.eval()
all_preds = []
with torch.no_grad():
    for X_batch, y_batch in test_loader:
        outputs = model(X_batch).squeeze()
        preds = (outputs > 0.5).float()
        all_preds.append(preds)

all_preds = torch.cat(all_preds).cpu().numpy()
f1 = f1_score(y_test, all_preds)
print('F1 Score:', f1)

print(classification_report(y_test, all_preds))
