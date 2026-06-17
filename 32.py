# # import numpy as np
# # import matplotlib.pyplot as plt
# # from sklearn.datasets import make_regression
# # from sklearn.preprocessing import StandardScaler
# # from sklearn.cluster import KMeans
# # from sklearn.metrics import silhouette_score
# # plt.rcParams['font.sans-serif']=['SimHei']
# # plt.rcParams['axes.unicode_minus']=False

# # # 1. 生成手机数据（同前）
# # X, y = make_regression(n_samples=100, n_features=3, noise=5, random_state=2)

# # X[:, 0] = np.interp(X[:, 0], (X[:, 0].min(), X[:, 0].max()), (50, 200))   # 手机价格
# # X[:, 1] = np.interp(X[:, 1], (X[:, 1].min(), X[:, 1].max()), (50, 100))   # 成本价格
# # X[:, 2] = np.interp(X[:, 2], (X[:, 2].min(), X[:, 2].max()), (1, 50))     # 营销成本
# # # 利润 y 不用于无监督学习，仅保留供后续分析（这里忽略）

# # print("特征矩阵形状:", X.shape)
# # print("前3个样本:\n", X[:3])

# # # 2. 标准化（所有聚类算法都依赖距离度量）
# # scaler = StandardScaler()
# # X_scaled = scaler.fit_transform(X)

# # # 3. 确定最佳聚类数（肘部法则 + 轮廓系数）
# # inertias = []
# # sil_scores = []
# # K_range = range(2, 8)

# # for k in K_range:
# #     kmeans = KMeans(n_clusters=k, random_state=2, n_init=10)
# #     labels = kmeans.fit_predict(X_scaled)
# #     inertias.append(kmeans.inertia_)
# #     sil_scores.append(silhouette_score(X_scaled, labels))

# # # 绘制肘部图和轮廓系数图
# # fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
# # ax1.plot(K_range, inertias, 'bo-')
# # ax1.set_xlabel('聚类数 k')
# # ax1.set_ylabel('簇内平方和 (惯性)')
# # ax1.set_title('肘部法则')

# # ax2.plot(K_range, sil_scores, 'ro-')
# # ax2.set_xlabel('聚类数 k')
# # ax2.set_ylabel('轮廓系数')
# # ax2.set_title('轮廓系数法')
# # plt.tight_layout()
# # plt.show()

# # # 根据图形选择 k=3（示例，也可自动选择最大轮廓系数对应的 k）
# # best_k = K_range[np.argmax(sil_scores)]
# # print(f"\n建议最佳聚类数: {best_k} (轮廓系数最大)")

# # # 4. 使用选定 k 进行最终聚类（这里以 k=3 为例，你也可以改成 best_k）
# # k = 3
# # kmeans = KMeans(n_clusters=k, random_state=2, n_init=10)
# # y_pred = kmeans.fit_predict(X_scaled)

# # # 5. 输出聚类结果
# # print("\n=== 无监督模型输出 ===")
# # print(f"聚类数: {k}")
# # print("聚类中心点（标准化空间）:\n", kmeans.cluster_centers_)
# # print("各簇样本数量:")
# # unique, counts = np.unique(y_pred, return_counts=True)
# # for cluster, count in zip(unique, counts):
# #     print(f"  簇 {cluster}: {count} 个样本")

# # # 6. 内部评估（轮廓系数）
# # sil_avg = silhouette_score(X_scaled, y_pred)
# # print(f"\n轮廓系数 (整体): {sil_avg:.4f} （越接近1表示聚类越好）")

# # # 7. 可视化（选择两个主特征：价格 vs 成本）
# # plt.figure(figsize=(8, 6))
# # scatter = plt.scatter(X_scaled[:, 0], X_scaled[:, 1], c=y_pred, cmap='viridis', s=50, alpha=0.7)
# # centroids = kmeans.cluster_centers_
# # plt.scatter(centroids[:, 0], centroids[:, 1], c='red', marker='X', s=200, label='聚类中心')
# # plt.xlabel('手机价格 (标准化后)')
# # plt.ylabel('成本价格 (标准化后)')
# # plt.title(f'KMeans 无监督聚类结果 (k={k})')
# # plt.colorbar(scatter, label='簇标签')
# # plt.legend()
# # plt.show()

# # # 可选：三维可视化（三个特征）
# # from mpl_toolkits.mplot3d import Axes3D
# # fig = plt.figure(figsize=(10, 7))
# # ax = fig.add_subplot(111, projection='3d')
# # ax.scatter(X_scaled[:, 0], X_scaled[:, 1], X_scaled[:, 2], c=y_pred, cmap='viridis', s=50, alpha=0.7)
# # ax.scatter(centroids[:, 0], centroids[:, 1], centroids[:, 2], c='red', marker='X', s=200)
# # ax.set_xlabel('价格 ')
# # ax.set_ylabel('成本 ')
# # ax.set_zlabel('营销成本 ')
# # ax.set_title('三维聚类结果')


# # plt.show()
# import jieba
# import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.naive_bayes import MultinomialNB
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
# text="我爱自然语言处理" 
# data_list = [
#     # 正面
#     ("味道超棒，服务好", 1),
#     ("电影太好看了，强烈推荐", 1),
#     ("商品质量不错，物流很快", 1),
#     ("环境优雅，性价比很高", 1),
#     ("非常满意，下次还来", 1),
#     ("味道好，干净卫生", 1),
#     ("超出预期，体验极佳", 1),
#     ("客服态度好，问题解决快", 1),
#     ("产品做工精细，细节到位", 1),
#     ("价格实惠，物超所值", 1),
#     ("服务周到，让人舒服", 1),
#     ("效果远超预期，非常满意", 1),
#     ("物流快，包装好", 1),
#     ("口味正宗，分量十足", 1),
#     ("质量上乘，值得购买", 1),
#     ("体验感满分，强烈安利", 1),
#     ("环境干净整洁，体验很好", 1),
#     ("态度热情，全程很愉快", 1),
#     ("效果很好，会回购的", 1),
#     ("各方面都很满意，好评", 1),
#     # 负面
#     ("太难吃了，再也不会来这家店", 0),
#     ("电影剧情无聊，浪费时间", 0),
#     ("商品质量差，发货很慢", 0),
#     ("价格贵，体验很差", 0),
#     ("非常失望，不推荐购买", 0),
#     ("卡顿严重，体验极差", 0),
#     ("做工粗糙，不值这个价", 0),
#     ("客服态度差，解决不了问题", 0),
#     ("物流太慢了，等了半个月", 0),
#     ("味道难吃，完全踩雷", 0),
#     ("质量堪忧，用了两天就坏了", 0),
#     ("价格虚高，完全不值", 0),
#     ("服务态度恶劣，再也不来", 0),
#     ("效果很差，完全没用", 0),
#     ("体验糟糕，差评", 0),
#     ("环境脏乱差，太失望了", 0),
#     ("态度冷漠，全程很糟心", 0),
#     ("发货错误，售后也不管", 0),
#     ("质量问题严重，不建议买", 0),
#     ("完全不符合预期，避雷", 0)
# ]
# seg_list=jieba.cut(text,cut_all=False)
# print("分词结果：" + "/".join(seg_list))
# stopwords={'的','了','在'}
# filtered = [w for w in ["我","爱","自然语言处理"]if w not  in stopwords]
# print(filtered)                                                                                             
# import jieba
# text = "我爱自然语言处理"
# seg_list = jieba.cut(text,cut_all = False)
# # print(list(seg_list))

# print("分词结果:"+"|".join(seg_list))
# stopwords = {'的','了','在'}
# filtered = [w for w in['我','爱','自然语言处理'] if w not in stopwords]
# import jieba
# import pandas as pd
# import nltk
# from nltk.corpus import stopwords
# # 下载NLTK中文停用词（首次运行需要下载）
# nltk.download('stopwords')
# from sklearn.feature_extraction.text import TfidfVectorizer
# # 导入TF-IDF文本特征提取工具，把文本转换成数字向量
# from sklearn.naive_bayes import MultinomialNB
# # 多项式朴素贝叶斯分类器，专门用于文本分类的经典机器学习算法
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score

# # 1 从CSV文件加载数据集
# df = pd.read_csv(r'c:\Users\33083\Desktop\实训\sxun\waimai_10k.csv')
# # 确保列名正确（CSV文件包含 label 和 review 两列）
# df.columns = ['label', 'text']
# # 只保留需要的列，并确保label是整数类型
# df['label'] = df['label'].astype(int)
# print(f"数据集加载完成，共 {len(df)} 条数据")
# print(f"正面评价: {len(df[df['label']==1])} 条")
# print(f"负面评价: {len(df[df['label']==0])} 条")
# print("\n前5条数据:")
# print(df.head())
# # print(df.head())

# # 2 使用NLTK中文停用词
# stop_words = set(stopwords.words('chinese'))

# # 3 分词 + 过滤停用词
# def cut_and_filter(text):
#     words = jieba.lcut(text)
#     words = [w for w in words if w not in stop_words]
#     return " ".join(words)

# df["cut_text"] = df["text"].apply(cut_and_filter)
# X = df["cut_text"]
# # print(X)
# y = df["label"]

# # 4 TF-IDF 调参
# tfidf = TfidfVectorizer(ngram_range=(1,2)) # 增加二元语法，捕获短语
# # ngram_range=(1,2) 表示同时提取一元词（单个词）和二元词（两个连续的词）
# # 比如句子“味道超棒”，会拆分出“味道”“超棒”“味道 超棒”
# X_tfidf = tfidf.fit_transform(X)
# # 把文本数据转换成 TF-IDF 特征矩阵

# # 5 划分数据集
# X_train, X_test, y_train, y_test = train_test_split(
#     X_tfidf, y, test_size=0.2, random_state=66, stratify=y
# )

# # 6 训练模型
# clf = MultinomialNB(alpha=0.8) # 平滑系数微调
# clf.fit(X_train, y_train)

# # 评估
# y_pred = clf.predict(X_test)
# print(f"测试集准确率：{accuracy_score(y_test, y_pred):.4f}")

# #预测函数
# def pred_sent(text):
#     txt = cut_and_filter(text)
#     vec = tfidf.transform([txt])

#     # 获取 正面/负面 概率
#     proba = clf.predict_proba(vec)[0]# [负面概率, 正面概率]
#     print(proba)
#     neg_prob = proba[0]  # 负面判断率
#     pos_prob = proba[1]  # 正面判断率

#     res = clf.predict(vec)[0]
#     result = "正面" if res == 1 else "负面"

#     # 输出结果
#     print(f"\n输入：{text}")
#     print(f"分词：{txt}")
#     print(f"模型判断：{result}")
#     print(f"负面概率：{neg_prob:.4f}")
#     print(f"正面概率：{pos_prob:.4f}")
#     return result

# print("\n测试预测")
# print(pred_sent("味道超棒，服务好"))
# print(pred_sent("太难吃了，再也不会来这家店"))
# print(pred_sent("味道还行，就是还好吃"))
import jieba
import pandas as pd
import nltk
from nltk.corpus import stopwords
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, GlobalAveragePooling1D
from sklearn.model_selection import train_test_split

# 1 从CSV文件加载数据集
df = pd.read_csv(r'c:\Users\33083\Desktop\实训\sxun\waimai_10k.csv')
# 确保列名正确（CSV文件包含 label 和 review 两列）
df.columns = ['label', 'text']
# 只保留需要的列，并确保label是整数类型
df['label'] = df['label'].astype(int)
print(f"数据集加载完成，共 {len(df)} 条数据")
print(f"正面评价: {len(df[df['label']==1])} 条")
print(f"负面评价: {len(df[df['label']==0])} 条")

# 2 使用NLTK中文停用词
stop_words = set(stopwords.words('chinese'))

# 3 分词 + 过滤停用词
def cut_and_filter(text):
    words = jieba.lcut(text)
    words = [w for w in words if w not in stop_words]
    return " ".join(words)

df["cut_text"] = df["text"].apply(cut_and_filter)
X = df["cut_text"]
# print(X)
y = df["label"]

Vocabulary_size = 10000
Max_len = 100
Tokenizer = Tokenizer(num_words=Vocabulary_size)
Tokenizer.fit_on_texts(X)
X_Seq = Tokenizer.texts_to_sequences(X)
X_Seq = pad_sequences(X_Seq, maxlen=Max_len)
print(X_Seq)
print(X_Seq.shape)
X_train, X_test, y_train, y_test = train_test_split(
    X_Seq, y, test_size=0.2, random_state=424, stratify=y
)

model = Sequential(
    [
        Embedding(Vocabulary_size, 128, input_length=Max_len),
        LSTM(64),
        Dense(1, activation='sigmoid')
    ]
)
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=5, batch_size=256, validation_data=(X_test, y_test))

loss,acc = model.evaluate(X_test, y_test)
print(f"测试集准确率：{acc:.4f}")

def pred_sent(text):
    txt = cut_and_filter(text)
    # 使用Tokenizer转换文se'qseq
    seq = Tokenizer.texts_to_sequences([txt])
    vec = pad_sequences(seq, maxlen=Max_len)

    # 获取正面概率（sigmoid输出）
    pos_prob = model.predict(vec)[0][0]
    neg_prob = 1 - pos_prob
    print(f"[负面概率, 正面概率]: [{neg_prob:.4f}, {pos_prob:.4f}]")

    result = "正面" if pos_prob > 0.6 else "负面" if pos_prob < 0.4 else "中性"

    # 输出结果
    print(f"\n输入：{text}")
    print(f"分词：{txt}")
    print(f"模型判断：{result}")
    print(f"负面概率：{neg_prob:.4f}")
    print(f"正面概率：{pos_prob:.4f}")
    return result

print("\n测试预测")
print(pred_sent("味道超棒，服务好"))
print(pred_sent("太难吃了，再也不会来这家店"))
print(pred_sent("吃的还行"))
print(pred_sent("不好吃"))