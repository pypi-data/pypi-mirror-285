python setup.py sdist upload

python setup.py sdist bdist_wheel

C:\Users\zx\AppData\Roaming\Python\Python38\Scripts\twine.exe 

C:\Users\zx\AppData\Roaming\Python\Python38\Scripts\twine.exe upload --repository-url https://upload.pypi.org/legacy/ dist/*

['Has0_acc_2', 'Has0_F1_score', 'Non0_acc_2', 'Non0_F1_score', 'Mult_acc_5', 'Mult_acc_7', 'MAE', 'Corr', 'LOSS']

ted. Migrate to API Tokens or Trusted Publishers instead. See https://pypi.org/help/#apitoken and https://pypi.org/help/#trusted-publishers


pypi-AgEIcHlwaS5vcmcCJDM4ZWVlYWZjLWUyNTItNDFiOS04ZThhLWY3ZTgxMjY1MGE5OAACKlszLCJiYWQyNDk0NS01YzkzLTQyMGQtYWJjNS1mZTUyYTc1ZDNjODIiXQAABiB0Pi624udpN2f7xbfGJKXKpWvtQ-pJRSs4M-YeayUJAQ


pypi-AgEIcHlwaS5vcmcCJDJjZTU4NzBiLTIwYWEtNGZlMi1iZTU4LWJjMmYzYTQ5MzU2MwACE1sxLFsid2h1amFrZXRlc3QiXV0AAixbMixbImU3MzNlMmYwLTRhNGQtNGYxMi1hNzRmLTUwMDIxNmMyNjA2MSJdXQAABiBCuwC0q4PHXYNTX8lS6OCmneQhIj_xJIqWbfZFuY0eew


pip install opencv-python

python setup.py sdist bdist_wheel

import tarfile
 
def extract_tar_gz(file_path, extract_path):
    with tarfile.open(file_path, 'r:gz') as tar:
        tar.extractall(extract_path)
 
# 调用示例
file_path = '/path/to/file.tar.gz'
extract_path = '/path/to/extract'
extract_tar_gz(file_path, extract_path)

torchvision torchaudio
opencv_python


pip install torch -i https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/

pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

pip3 install torch  --index-url https://download.pytorch.org/whl/cu118


https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/win-64/


import numpy as np
from sklearn.datasets import make_classification_target
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
 
# 生成示例数据
X, y = make_classification_target(n_samples=1000, n_features=50, n_classes=5, n_informative=8, n_redundant=10, random_state=0)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
 
# 创建随机森林分类器实例
random_forest = RandomForestClassifier(n_estimators=100, random_state=42)
 
# 训练模型
random_forest.fit(X_train, y_train)
 
# 进行预测
y_pred = random_forest.predict(X_test)
 
# 计算准确率
accuracy = np.sum(y_pred == y_test) / len(y_test)
print(f"Accuracy: {accuracy}")


from sklearn import metrics
metrics.precision_score(y_true, y_pred, average='micro')  # 微平均，精确率
Out[130]: 0.33333333333333331

metrics.precision_score(y_true, y_pred, average='macro')  # 宏平均，精确率
Out[131]: 0.375

metrics.precision_score(y_true, y_pred, labels=[0, 1, 2, 3], average='macro')  # 指定特定分类标签的精确率
Out[133]: 0.5


metrics.recall_score(y_true, y_pred, average='micro')
Out[134]: 0.33333333333333331

metrics.recall_score(y_true, y_pred, average='macro')
Out[135]: 0.3125



metrics.f1_score(y_true, y_pred, average='weighted')  
Out[136]: 0.37037037037037035


# 分类报告：precision/recall/fi-score/均值/分类个数
 from sklearn.metrics import classification_report
 y_true = [0, 1, 2, 2, 0]
 y_pred = [0, 0, 2, 2, 0]
 target_names = ['class 0', 'class 1', 'class 2']
 print(classification_report(y_true, y_pred, target_names=target_names))
 
 
 import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle

from sklearn import svm, datasets
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier
from scipy import interp

# Import some data to play with
iris = datasets.load_iris()
X = iris.data
y = iris.target

# 画图
all_fpr = np.unique(np.concatenate([fpr[i] for i in range(n_classes)]))

# Then interpolate all ROC curves at this points
mean_tpr = np.zeros_like(all_fpr)
for i in range(n_classes):
    mean_tpr += interp(all_fpr, fpr[i], tpr[i])

# Finally average it and compute AUC
mean_tpr /= n_classes

fpr["macro"] = all_fpr
tpr["macro"] = mean_tpr
roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])

# Plot all ROC curves
plt.figure()
plt.plot(fpr["micro"], tpr["micro"],
         label='micro-average ROC curve (area = {0:0.2f})'
               ''.format(roc_auc["micro"]),
         color='deeppink', linestyle=':', linewidth=4)

plt.plot(fpr["macro"], tpr["macro"],
         label='macro-average ROC curve (area = {0:0.2f})'
               ''.format(roc_auc["macro"]),
         color='navy', linestyle=':', linewidth=4)

colors = cycle(['aqua', 'darkorange', 'cornflowerblue'])
for i, color in zip(range(n_classes), colors):
    plt.plot(fpr[i], tpr[i], color=color, lw=lw,
             label='ROC curve of class {0} (area = {1:0.2f})'
             ''.format(i, roc_auc[i]))

plt.plot([0, 1], [0, 1], 'k--', lw=lw)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Some extension of Receiver operating characteristic to multi-class')
plt.legend(loc="lower right")
plt.show()


.cache\torch\hub\checkpoints


