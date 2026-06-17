# from tensorflow.keras.models import load_model
# import numpy as np
# from PIL import Image

# # 加载训练好的模型
# model = load_model('mnist_cnn.h5')

# # 读取自己的图片
# img = Image.open(r'sxun/tup/ca0af828fbf60d51507a592ee7eab3c1.png').convert('L')   # 转为灰度图
# img = img.resize((28, 28))                     # 缩放到 28x28

# # 转为 numpy 数组，并归一化
# img_array = np.array(img) / 255.0

# # 如果是黑底白字，通常需要反转颜色（因为 MNIST 是白底黑字）
# # 判断是否需要反转：如果图片大部分像素 > 0.5，可能是白底黑字，不需要反转；
# # 如果大部分 < 0.5，可能是黑底白字，需要反转。简单做法：取反 1 - img_array
# # 你可以手动尝试
# img_array = 1 - img_array   # 如果你写的数字是黑底白字，就取消注释这行

# # 增加 batch 和 channel 维度
# img_array = img_array.reshape(1, 28, 28, 1)

# # 预测
# pred = model.predict(img_array)
# digit = np.argmax(pred)
# print(f"预测的数字是: {digit}")
# list_1d=[1,2,3,4,5]
# arr_1d=np.array(list_1d)
# 1print(arr_1d)
# a=np.array([[1,2,3],[4,5,6],[7,8,9]])
# b=np.array([[1,2,3],[4,5,6],[7,8,9]])

# print(a+b)
# print(a-b)
# print(a*2)
# arr_2d=np.array(list_2d)
# print(arr_2d)
# list_3d=[[1,2,3],[4,5,6],[7,8,9]]
# arr_3d=np.array(list_3d)
# print("维度(ndim):",arr_2d.ndim)
# print("形状:(shape)",arr_2d.shape)
# print("元素总数(size):",arr_2d.size)
# print("元素类型(dtype):",arr_2d.dtype)
# print(np.zeros((2,3)))
# print(np.ones((3,2)))
# print(np.full((2,2),7))
# print(np.eye(9))
# print(np.arange(0,10,2))
# print(np.linspace(0,1,5))
# print(np.random.rand(2,3))
# arr=np.arange(12)
# b=arr.reshape(4,3)
# print(b)
# # print(arr.reshape(2,-1))
# print(b.mean(axis=None))
# print(b.max(axis=1))
# print(b.mean(axis=1))
# print(b.mean(axis=None))
# b=np.random.randint(0,101,size=(2,5,3))
# print(b)
# print(b[0])
# print(b[:,2])
# print(b[1,3:,:2])
# # print(b[:,:,2:])
# a=b[0]
# mask=a>=85
# print(a[mask])
# mask=b<60
# print(b[:,])
# print(np.where(b>90,'优秀',np.where(b<60,'不合格','合格')))
# print()


# print(b.mean(axis=(1,2)))
# # print(b.max(axis=1))
# print(b.min(axis=(1)))
# print(b[1])
# print(b[1,1])
# print(b[2,1])
# print(b[:2,2])
# print(b[:2,1:])
# sort_indices = np.argsort(c)[::-1]   
# sorted_ids = ids[sort_indices]
# sorted_scores = c[sort_indices]
# print("\n按总分排序（学号, 总分）:")
# for sid, score in zip(sorted_ids, sorted_scores):
#     print(f"  学号 {sid:2d} : {score:3d} 分")

# b=a[:,1:]
# print(b)
# print("平均分：",b.mean(axis=0))
# print("最高分:",b.max(axis=0))
# print("最低分:",b.min(axis=0))
# print("总分:",b.sum(axis=1))
# print("个人平均分:",b.mean(axis=1))
# c=b.sum(axis=1)
# d=a[c.argmax()]
# print("最高分名字",d[0])
# fail_mask = np.any(b < 60, axis=1)
# fail_ids = ids[fail_mask]
# print("\n不及格学生学号（至少一科<60）:", fail_ids)                                                 


# sort_indices = np.argsort(c)[::-1]   
# sorted_ids = ids[sort_indices]
# sorted_scores = c[sort_indices]
# print("\n按总分排序（学号, 总分）:")
# for sid, score in zip(sorted_ids, sorted_scores):
#     print(f"  学号 {sid:2d} : {score:3d} 分")


# q = (eng > 90) & (math > 85)
# fail_ids = ids[q]
# print("\n英语优秀且数学优秀的学生学号:", fail_ids)        

# w=np.clip(math+5,0,100)
# e=np.column_stack((ids,w,eng,chi))
# print(e)

# sort_indices = np.argsort(c)[::-1]   
# sorted_ids = ids[sort_indices]
# sorted_scores = c[sort_indices]
# print("\n按总分排序（学号, 总分）:")
# for sid, score in zip(sorted_ids, sorted_scores):
#     print(f"  学号 {sid:2d} : {score:3d} 分")

# import matplotlib.pyplot as plt
# import numpy as np

# plt.rcParams['font.sans-serif'] = ['SimHei']
# plt.rcParams['axes.unicode_minus'] = False

# x = np.linspace(-2*np.pi, 2*np.pi, 200)
# y1 = np.sin(x)
# y2 = np.cos(x)
# y3 = np.power(x, 2)
# y4 = np.exp(x)
# plt.figure(figsize=(12, 6), dpi=100)

# plt.plot(x, y1, label='sin(x)', color='blue', linestyle=':', linewidth=2)
# plt.plot(x, y2, label='cos(x)', color='red', linestyle='--', linewidth=2)
# plt.plot(x, y3, label='x**2', color='green', linestyle='-', linewidth=2)
# plt.plot(x, y4, label='e**x', color='orange', linestyle='-.', linewidth=2)

# # 为了让负数区域的细节更明显，可以限制 y 轴范围（视情况取消注释）
# plt.ylim(-5, 30)

# plt.title('函数图像 (负数区域完整显示)', fontsize=30, loc='left', pad=9.0)
# plt.xlabel('x轴', fontsize=20)
# plt.ylabel('y轴', fontsize=20)
# plt.legend(fontsize=10, loc='upper left')
# plt.grid(True, color='gray', linestyle=':', linewidth=0.5)

# # 显示负数刻度标签
# plt.xticks(np.arange(-6, 7, 2))

# plt.show() # 线宽0.1太细，0.5更清晰

# plt.show()
# import numpy as np
# plt.rcParams['font.sans-serif']=['SimHei']
# plt.rcParams['axes.unicode_minus']=False
# x=np.linspace(-2*np.pi,2*np.pi,200)
# y1=np.sin(x)
# y2=np.cos(x)
# y3=np.power(x,2)
# y4=np.exp(x)
# plt.figure(figsize=(100,6),dpi=100)
# plt.plot(x,y1,label='sin(x)',color='blue',linestyle=':')
# plt.plot(x,y2,label='cos(x)',color='red',linestyle='--')
# plt.plot(x,y3,label='x**2',color='green',linestyle='*')
# plt.plot(x,y4,label='e**x',color='orange',linestyle='')
# # x=[1,2,3,4,5]
# # y=[1,4,9,16,25]
# # plt.plot(x,y,color='red',linestyle=':',linewidth=1,alpha=0.7)
# plt.title('图',fontsize=30,fontweight='normal',color='red',loc='left',pad=9.0)
# plt.xlabel('x轴',fontsize=20,fontweight='normal',color='red')
# plt.ylabel('y轴',fontsize=20,fontweight='normal',color='red')
# plt.legend(fontsize=10,loc='upper left')
# plt.grid(True,color='gray',linestyle=':',linewidth=0.1)
# plt.show()

# from sklearn.datasets import load_iris
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
# from sklearn.linear_model import LogisticRegression
# from sklearn.pipeline import make_pipeline
# from sklearn.metrics import accuracy_score
# import matplotlib.pyplot as plt

# # 2. 加载数据
# iris = load_iris(); X = iris.data; y = iris.target

# # 新增：数据可视化 - 萼片长度 vs 花瓣长度散点图
# plt.figure(figsize=(10, 6)); colors = ['red', 'green', 'blue']
# for i, c in enumerate(colors): plt.scatter(X[y==i,0], X[y==i,2], c=c, label=iris.target_names[i], edgecolor='k', s=50)
# plt.xlabel('Sepal Length'); plt.ylabel('Petal Length'); plt.title('Iris Dataset'); plt.legend(); plt.show()

# # 3. 划分训练集/测试集; 4. 构建并训练Pipeline模型
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
# pipe = make_pipeline(StandardScaler(), LogisticRegression()); pipe.fit(X_train, y_train)

# # 5. 预测与评估
# y_pred = pipe.predict(X_test); accuracy = accuracy_score(y_test, y_pred)
# print(f"模型在测试集上的准确率: {accuracy:.4f}")
# from unittest import SkipTest


# from sklearn.linear_model import LogisticRegression
# from sklearn.metrics import accuracy_score
# iris = load_iris(); X = iris.data; y = iris.target
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.datasets import make_regression
from sklearn.metrics import mean_squared_error, r2_score
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False


X,y=make_regression(n_samples=100,n_features=3,noise=5,random_state=1)


X[:,0]=np.interp(X[:,0],(X[:,0].min(),X[:,0].max()),(50,200))  #手机价格
X[:,1]=np.interp(X[:,1],(X[:,1].min(),X[:,1].max()),(50,100))    #成本价格
X[:,2]=np.interp(X[:,2],(X[:,2].min(),X[:,2].max()),(1,50))     #营销成本
y=np.interp(y,(y.min(),y.max()),(0,100))  #利润
y=np.round(y,2).astype(int)
print("X shape:",X.shape)
print("y shape:",y.shape)
print("\n前五行:\n",X[:5])
print("\n前五个价格:\n",y[:5])
scaler=StandardScaler()
X_scaled=scaler.fit_transform(X)
kmeans=KMeans(n_clusters=3,random_state=1)
K=3
kmeans.fit(X_scaled)
y_pred=kmeans.fit_predict(X_scaled)
print("聚类中心点:",kmeans.cluster_centers_)
plt.figure(figsize=(10,6))
plt.scatter(X_scaled[:,0],X_scaled[:,1],c=y_pred)
centroids=kmeans.cluster_centers_
plt.scatter(centroids[:,0],centroids[:,1],c='red',marker='x',s=100,label='聚类中心')
plt.xlabel('手机价格')
plt.ylabel('成本价格')
plt.title('手机价格与成本价格的聚类结果')
plt.legend()
plt.show()

# model=RandomForestRegressor(n_estimators=100,random_state=1)
# model.fit(X_train,y_train)
# y_pred=model.predict(X_test)
# mse=mean_squared_error(y_test,y_pred)
# print(f"模型在测试集上的MSE: {mse:.4f}")
# print(f"模型在测试集上的决定系数: {model.score(X_test,y_test):.4f}")

# plt.figure(figsize=(10,6))
# titles=["手机价格","成本价格","营销成本"]
# for i in range(3):
#     plt.subplot(1,3,i+1)
#     plt.hist(X[:,i],bins=10,color='blue',edgecolor='k')
#     plt.title(titles[i])
#     plt.grid(True,color='gray',linestyle=':',linewidth=0.1)
# plt.tight_layout()
# plt.show()
# # # 特征vs利润散点图
# plt.figure(figsize=(10,6))
# for i in range(3):
#     plt.subplot(1,3,i+1)
#     plt.scatter(X[:,i],y)
#     plt.xlabel(titles[i])
#     plt.ylabel('利润')
#     plt.title(f'{titles[i]}与利润的关系')
#     plt.grid(True,color='gray',linestyle=':',linewidth=0.1)
# plt.tight_layout()
# plt.show()
# # 实际vs预测利润散点图
# plt.figure(figsize=(10,6))
# plt.scatter(y_test,y_pred)
# plt.xlabel('实际利润')
# plt.ylabel('预测利润')
# plt.title('实际利润vs预测利润')
# plt.grid(True,color='gray',linestyle=':',linewidth=0.1)
# plt.show()
# # 特征重要性
# plt.figure(figsize=(10,6))
# plt.barh(range(3),model.feature_importances_)
# plt.yticks(range(3),titles)
# plt.xlabel('特征重要性')
# plt.title('特征重要性')
# plt.grid(True,color='gray',linestyle=':',linewidth=0.1)
# plt.show()
# #残值分布
# plt.figure(figsize=(10,6))
# plt.hist(y_pred-y_test,bins=10,color='blue',edgecolor='k')
# plt.xlabel('残值')
# plt.ylabel('数量')
# plt.title('残值分布')
# plt.grid(True,color='gray',linestyle=':',linewidth=0.1)
# plt.show()


# np.random.seed(42)
# area=np.random.randint(50,150,size=100);
# price=1.2*area+10+np.random.normal(0,5,size=100);
# X=area.reshape(-1,1)
# y=price
# print(X.shape)
# print(y.shape)
# plt.figure(figsize=(10,6))
# plt.scatter(X,y)
# plt.xlabel('面积')
# plt.ylabel('价格')
# plt.title('面积与价格的关系')

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# print(f"训练集大小{X_train.shape[0]}")
# print(f"测试集大小{X_test.shape[0]}")
# model=LinearRegression()
# model.fit(X_train,y_train)
# print(f"模型在测试集上的系数: {model.coef_[0]:.4f}")
# print(f"模型在测试集上的截距: {model.intercept_:.4f}")
# y_pred=model.predict(X_test)
# plt.plot(X_test,y_pred,color='red',linestyle='--',linewidth=0.5)
# y_test_pred=model.predict(X_test)
# mse=mean_squared_error(y_test,y_test_pred)
# print(f"模型在测试集上的MSE: {mse:.4f}")
# print(f"模型在测试集上的决定系数: {model.score(X_test,y_test):.4f}")
# rf=RandomForestRegressor(n_estimators=100,random_state=42)
# rf_model=rf.fit(X_train,y_train)
# y_pred_pred=rf_model.predict(X_test)
# plt.plot(X_test,y_pred_pred,color='green',linestyle='--',linewidth=0.5)
# plt.show()

# iris=load_iris()
# X=iris.data
# scaler=StandardScaler()
# X_scaled=scaler.fit_transform(X)
# kmeans=KMeans(n_clusters=5,random_state=1)
# kmeans.fit(X_scaled)
# y_pred=kmeans.fit_predict(X_scaled)
# print("聚类中心点:",kmeans.cluster_centers_)
# plt.scatter(X_scaled[:,0],X_scaled[:,1],c=y_pred)
# centroids=kmeans.cluster_centers_
# plt.scatter(centroids[:,0],centroids[:,1],c='red',marker='x',s=100,label='聚类中心')
# plt.title('KMeans 无监督聚类结果')
# plt.legend()
# plt.show()
