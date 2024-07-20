# 导入所需库
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import GridSearchCV

# 读取数据
data = pd.read_csv('credit.csv')

# 填充空值
data = data.fillna(data.mean())

# 性别用【0、1】替换
le = LabelEncoder()
data['gender'] = le.fit_transform(data['gender'])

# 省份用 one-hot 编码替换
ohe = OneHotEncoder()
province = ohe.fit_transform(data['province'].values.reshape(-1, 1)).toarray()
data = data.drop(['province'], axis=1)
data = pd.concat([data, pd.DataFrame(province)], axis=1)

# 处理异常值（这里假设异常值为超过平均值3个标准差的值）
for column in data.columns:
    if np.issubdtype(data[column].dtype, np.number):
        data[column] = data[column][np.abs(data[column] - data[column].mean()) <= (3 * data[column].std())]

# 画图反映不同特征条件下的违约情况
plt.figure(figsize=(12, 6))
for column in data.columns:
    if np.issubdtype(data[column].dtype, np.number):
        plt.subplot(len(data.columns), 2, data.columns.get_loc(column)*2+1)
        plt.boxplot([data[data['default'] == 0][column], data[data['default'] == 1][column]])
        plt.title(column)
plt.show()

# 切分训练集和测试集
X = data.drop(['default'], axis=1)
y = data['default']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 建立用户违约风险模型
clf = RandomForestClassifier()
param_grid = {'n_estimators': [50, 100, 200], 'max_depth': [None, 10, 20, 30], 'min_samples_split': [2, 5, 10]}
grid_search = GridSearchCV(clf, param_grid, cv=5)
grid_search.fit(X_train, y_train)
best_clf = grid_search.best_estimator_

# 提交预测模型
result = pd.read_csv('results.csv')
result = result.fillna(result.mean())
result['gender'] = le.transform(result['gender'])
result = result.drop(['province'], axis=1)
result = pd.concat([result, pd.DataFrame(ohe.transform(result['province'].values.reshape(-1, 1)).toarray())], axis=1)
for column in result.columns:
    if np.issubdtype(result[column].dtype, np.number):
        result[column] = result[column][np.abs(result[column] - result[column].mean()) <= (3 * result[column].std())]
X_new = result.drop(['default'], axis=1)
y_pred = best_clf.predict(X_new)
print('预测准确率f1值为：', f1_score(result['default'], y_pred))


import json

# 将预测结果存储在字典中
result_dict = {'predictions': y_pred.tolist()}

# 将字典转换为json格式并输出
result_json = json.dumps(result_dict)
print(result_json)

# 导出到JSON文件
with open('data.json', 'w') as f:
    json.dump(result_json, f)



# 七步模型

#(1) 导入数据集合
from sklearn.datasets import load_wine
wine = load_wine()

#(2) 拆分特征和标签
X = wine.data
y = wine.target

#(3)拆分训练集合和测试集合
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y)

#(4) 导入多层感知模型
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
mpl = RandomForestClassifier(n_estimators=200, max_depth=5)

#（5）数据训练，模拟拟合
mpl.fit(X_train, y_train)

#(6)预测
pre = mpl.predict(X_test)

#(7) 模型评价
from sklearn.metrics import accuracy_score

score = accuracy_score(y_test, pre)

print("模型分数{0:.2f}%".format(score * 100))


