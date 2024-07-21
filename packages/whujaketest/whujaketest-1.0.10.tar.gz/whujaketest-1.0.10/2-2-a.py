import pandas as pd
from sklearn.model_selection import train_test_split

# 加载数据集
file_path = 'task1/results/1-3-fake_job_postings.csv'
data = pd.read_csv(file_path)

# 将数据集按 7:3 比例划分为训练集和测试集
train_data, test_data = train_test_split(data, test_size=0.3, random_state=42)

# 将数据集保存到新的 CSV 文件中
train_file_path = 'task1/results/train_data.csv'
test_file_path = 'task1/results/test_data.csv'

# 保存训练集数据
train_data.to_csv(train_file_path, index=False)
# 保存测试集数据
test_data.to_csv(test_file_path, index=False)

# 输出文件路径
train_file_path, test_file_path
