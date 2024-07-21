import re
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# 加载数据集
file_path = 'task1/dataset/fake_job_postings.csv'
data = pd.read_csv(file_path)

# 合并相关文本列进行分析
data['text'] = data['title'].fillna('') + " " + data['company_profile'].fillna('') + " " + data['description'] + " " + data['requirements'].fillna('') + " " + data['benefits'].fillna('')

# 清理文本数据
def clean_text(text):
    if pd.isna(text):
        return ' '
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text, re.I|re.A)
    text = text.lower()
    text = text.strip()
    return text

data['text'] = data['text'].apply(clean_text)

# 对文本数据进行TF-IDF向量化
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(data['text'])

# 提取目标变量
y = data['fraudulent'].values

# 将数据分为训练集和验证集
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# 定义和训练逻辑回归模型
model = LogisticRegression()
model.fit(X_train, y_train)

# 评估模型
y_pred = model.predict(X_val)
print(classification_report(y_val, y_pred))

# 保存模型
import joblib
model_save_path = 'task1/model/logistic_model.pkl'
joblib.dump(model, model_save_path)
print(f"Model saved to {model_save_path}")
