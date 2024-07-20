import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 加载数据集
file_path = 'task1/results/1-3-fake_job_postings.csv'
data = pd.read_csv(file_path)

# 显示数据集的前几行以了解其结构
print(data.head())

# 将 'fraudulent' 列转换为有意义的标签
data['fraudulent'] = data['fraudulent'].map({0: 'Non-Fraudulent', 1: 'Fraudulent'})

# 设置 matplotlib 图形
plt.figure(figsize=(16, 10))

# 图2：基于部门的欺诈与非欺诈情况
plt.subplot(2, 2, 1)  # 调整为 (2, 2, 1) 以正确放置
sns.countplot(data=data, x='department', hue='fraudulent', palette='coolwarm')
plt.title('Fraudulent vs Non-Fraudulent by Department')
plt.xticks(rotation=90)

# 图3：基于就业类型的欺诈与非欺诈情况
plt.subplot(2, 2, 2)  # 调整为 (2, 2, 2) 以正确放置
sns.countplot(data=data, x='employment_type', hue='fraudulent', palette='coolwarm')
plt.title('Fraudulent vs Non-Fraudulent by Employment Type')
plt.xticks(rotation=45)

# 图4：基于要求经验的欺诈与非欺诈情况
plt.subplot(2, 2, 3)  # 调整为 (2, 2, 3) 以正确放置
sns.countplot(data=data, x='required_experience', hue='fraudulent', palette='coolwarm')
plt.title('Fraudulent vs Non-Fraudulent by Required Experience')
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
