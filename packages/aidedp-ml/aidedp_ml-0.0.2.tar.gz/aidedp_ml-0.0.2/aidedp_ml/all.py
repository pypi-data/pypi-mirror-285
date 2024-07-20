# 安装sklearn、seaborn
# pip install scikit-learn
# pip install seaborn

# 生成 requirements.txt
# pip freeze > requirements.txt

import os
print(os.getcwd())

''''''
'''' 1 查看数据集 '''
''''''
import pandas as pd
# (1)读取数据
data = pd.read_csv(r'F:\works\aidedp_ml\maotai.csv')
data = pd.read_excel('data.xlsx')

# 读取json
import json
with open('data.json','r',encoding='utf-8') as f:
    data = json.load(f)

# 转为Dataframe
data = pd.DataFrame(data)

# (2) 查看数据大小
data.head(2)
data.tail(4)
data.shape
data.describe()
data.info()
data.isna().sum()
data.columns
data.index()
data.dtypes   # 查看列属性
data['lieming'].unique()  # 查看某一列唯一值

data['lie'].max()  # min mean std-标准差 var-方差 median-中位数

''''''
''' 2 数据可视化 '''
''''''
import matplotlib.pyplot as plt
import seaborn as sns

# 对于dataframe
data['lie1'].plot(kind='line')    # line-线 bar-柱状图 hist-直方图
plt.title("标题")
plt.xlabel('横轴坐标名称') 
plt.ylabel('纵轴坐标名称') 
plt.legend()   # 显示图例
plt.rcParams['font.sans-serif'] = 'simhei'  # 设置中文显示
plt.rcParams['axes.unicode_minus'] = False # 设置显示负号
plt.savefig('tu.png')  # 保存图片

# 热力图
tmp  = data.iloc[:,1:].corr()   # corr-计算相关性系数
sns.heatmap(tmp)
plt.title('猴子那个文')
plt.rcParams['font.sans-serif'] = 'simhei'
plt.savefig(r'F:\1.数字化部\电信\aaa.png')


''' 3 数据预处理 '''
# 填充
pingjunzhi = data['lie'].mean()
data['lie'] = data['lie'].fillna(value=pingjunzhi)
# 去重
data = data.drop_duplicates()
# 大小写转换
data['city']=data['city'].str.lower() # upper capitalize-首字母大写
# 更改数据格式
data['price'] = data['price'].astype('int')       
# 更改列名称
data.rename(columns={'category': 'category-size'}, inplace=True) 
data.columns = ['a','b','c']
# 数据替换
data = data['city'].replace('sh', 'shanghai')
# 删除空行
data.dropna(axis=0) # 0-hang 1-lie


# 标准化
from sklearn.preprocessing import StandardScaler  # 标准差标准化
scaler = StandardScaler().fit(offline_train6[['User_id', 'Merchant_id']])
offline_train7 = offline_train6.copy()
offline_train7[['User_id', 'Merchant_id']] = scaler.transform(offline_train7[['User_id', 'Merchant_id']])
offline_train7

# PCA降维
from sklearn.decomposition import PCA



''''''
''' 4 划分数据集 '''
''''''
# 编码
data = pd.DataFrame([
            ['yellow', 'M', 10.1, 'class1'], 
            ['red', 'L', 13.5, 'class2'], 
            ['blue', 'XL', 15.3, 'class1'],
            ['green', 'XL', 16.3, 'class3']])
 
data.columns = ['颜色', '大小', '价格', '类别标签']
X = data[['颜色', '大小', '价格']]   # 等价于  data.iloc[:,:-1]
y = data['类别标签']                # 等价于  data.iloc[:,-1]

# X = data.iloc[:3,4:]  前三行，第四列以后

# Labelencoder编码 
from sklearn.preprocessing import LabelEncoder
encoder = LabelEncoder()
category = encoder.fit_transform(data['颜色'])
print("颜色编码：",category)                # 颜色编码： [3 2 0 1]
print("编码对应的颜色：",encoder.classes_)   # 编码对应的颜色： ['blue' 'green' 'red' 'yellow']

# One-hot编码
# （1）
data = pd.get_dummies(data, columns=['颜色', '大小']).replace({False:0, True:1})
# (2)
from sklearn.preprocessing import OneHotEncoder
columns = ['颜色','大小','类别标签']
enc = OneHotEncoder()
# 将['颜色','大小','类别标签']这3列进行独热编码
tmp = enc.fit_transform(data[['颜色']]).toarray()
tmpdf = pd.DataFrame(tmp, columns=enc.get_feature_names_out(['颜色']))
data = pd.concat([tmpdf, data], axis=1)
data = data.drop(columns=['颜色'])

# 划分数据集
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.3)   # X-数据，y-标签

''''''
''' 5 模型训练\预测 '''
''''''
# 分类
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier().fit(X_train, y_train)  # 模型训练
model.score(X_test, y_test)  # 准确率

# 回归
from sklearn.ensemble import RandomForestRegressor
model = RandomForestRegressor().fit(X_train, y_train)



''' 6 模型评估 '''
# 分类
#                           f1指数      准确率          召回率        精准率           roc曲线      auc值           混淆矩阵            分类报告
from sklearn.metrics import f1_score, accuracy_score, recall_score, precision_score, roc_curve, roc_auc_score, confusion_matrix, classification_report

y_pre = model.predict(X_test) # 预测值
print(accuracy_score(y_test, y_pre))
print(confusion_matrix(y_test, y_pre))#混淆矩阵
print(recall_score(y_test, y_pre))#查全率
print(precision_score(y_test, y_pre))#查准率
print(f1_score(y_test, y_pre)) # F1值
roc_curve(y_test, y_pre)

# 回归
from sklearn.metrics import mean_absolute_error 
prediction = [2.443532,5.213567,8.168953]
true_value = [2.431354,5.839245,8.123678]
score = mean_absolute_error(true_value, prediction)


''' 7 保存模型 '''
import pickle

# 使用 pickle 保存模型
with open('name.pkl', 'wb') as file:
    pickle.dump(model, file)



# 交叉验证
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
 
# 加载Iris数据集
iris = load_iris()
X = iris.data
y = iris.target
 
# 创建一个随机森林分类器
classifier = RandomForestClassifier()
 
# 使用10折交叉验证
scores = cross_val_score(classifier, X, y, cv=10)
 
# 打印每个fold的得分
print(scores)
 
# 打印平均得分
print("Average score:", scores.mean())
