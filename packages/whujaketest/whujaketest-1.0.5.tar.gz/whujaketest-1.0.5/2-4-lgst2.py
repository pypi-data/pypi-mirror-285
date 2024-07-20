import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# 加载数据集
file_path = 'task1/dataset/fake_job_postings.csv'
data = pd.read_csv(file_path)

# 选择特征列和目标列
features = ['telecommuting', 'has_company_logo', 'has_questions', 'employment_type', 'required_experience', 'required_education', 'industry']
data = data[features + ['fraudulent']]

# 填充缺失值
data.fillna(value={'employment_type': 'unknown', 'required_experience': 'unknown', 'required_education': 'unknown', 'industry': 'unknown'}, inplace=True)

# 将分类变量转换为数值变量
data = pd.get_dummies(data, columns=['employment_type', 'required_experience', 'required_education', 'industry'])

X = data.drop('fraudulent', axis=1)
y = data['fraudulent'].values

# 将数据分为训练集和验证集
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# 定义和训练逻辑回归模型
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# 评估模型
y_pred = model.predict(X_val)
print(classification_report(y_val, y_pred))

# 保存模型
import joblib
model_save_path = 'task1/model/logistic_model.pkl'
joblib.dump(model, model_save_path)
print(f"Model saved to {model_save_path}")
