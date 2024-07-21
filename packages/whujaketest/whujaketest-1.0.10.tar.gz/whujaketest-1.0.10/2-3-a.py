import pandas as pd

# 加载CSV文件
file_path = 'task1/results/1-3-fake_job_postings.csv'
data = pd.read_csv(file_path)

# 显示数据的前几行以了解其结构
data.head()

import matplotlib.pyplot as plt
import seaborn as sns

# 处理位置数据，提取国家或城市
data['country'] = data['location'].apply(lambda x: x.split(', ')[-1])

# 可视化职位地点的分布
location_counts = data['country'].value_counts().head(10)  # 显示前10个位置

plt.figure(figsize=(12, 8))
sns.barplot(x=location_counts.values, y=location_counts.index, palette='viridis')
plt.title('职位地点分布（前10）')
plt.xlabel('职位数量')
plt.ylabel('地点')
plt.show()

# 分析远程工作与职位职能的相关性
# 首先，我们需要清理并处理职位职能的数据

# 去除空值
function_telecommuting = data[['function', 'telecommuting']].dropna()

# 计算每个职位职能中远程工作的比例
telecommuting_ratio = function_telecommuting.groupby('function')['telecommuting'].mean().sort_values(ascending=False)

# 可视化远程工作与职位职能的相关性
plt.figure(figsize=(12, 8))
sns.barplot(x=telecommuting_ratio.values, y=telecommuting_ratio.index, palette='coolwarm')
plt.title('远程工作与职位职能的相关性')
plt.xlabel('远程工作比例')
plt.ylabel('职位职能')
plt.show()
