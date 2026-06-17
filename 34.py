# -*- coding: utf-8 -*-
"""
情感分类 - CNN + LSTM 混合模型（方案B）
提升特征提取能力，兼顾局部 n-gram 和长序列依赖
"""

import os
import re
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, roc_curve, auc
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Conv1D, MaxPooling1D, LSTM, Dense, Dropout, Flatten, GlobalMaxPooling1D
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import jieba

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ------------------------------
# 0. 停用词加载（修正：移除否定词）
# ------------------------------
def load_stopwords(filepath=r'c:\Users\33083\Desktop\实训\sxun\chinese_stopwords.txt'):
    stop_words = set()
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                if word:
                    stop_words.add(word)
        print(f"已加载停用词文件：{filepath}，共 {len(stop_words)} 个词")
    else:
        # 内置精简停用词（已移除否定词）
        stop_words = set([
            '的', '了', '是', '在', '和', '有', '也', '都', '这', '那', '一', '个',
            '就', '对', '到', '说', '去', '上', '下', '与', '及', '为', '于', '以', '或',
            '但', '而', '又', '并', '则', '等', '还', '只', '能', '会', '要', '可能',
            '把', '被', '让', '给', '从', '到', '向', '跟', '比', '同', '啊', '哦',
            '嗯', '吧', '吗', '呢', '啦', '呀', '我们', '你们', '他们', '它们', '自己', '大家'
        ])
        print(f"未找到停用词文件，使用内置停用词（已移除否定词），共 {len(stop_words)} 个词")
    return stop_words

stop_words = load_stopwords()

# ------------------------------
# 1. 文本清洗 + 分词 + 去停用词
# ------------------------------
def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'[^\u4e90-\u9fa5a-zA-Z0-9]', ' ', text)
    words = jieba.lcut(text)
    words = [w for w in words if w not in stop_words and len(w) > 1]
    return " ".join(words)

# ------------------------------
# 2. 数据加载（请修改为实际路径）
# ------------------------------
train_df = pd.read_csv(r"C:\Users\33083\Desktop\实训\sxun\train.csv")
test_df = pd.read_csv(r"C:\Users\33083\Desktop\实训\sxun\test.csv")

print(f"原始训练集大小: {len(train_df)}")
print(f"原始测试集大小: {len(test_df)}")

# 丢弃中性样本（3星），避免噪声
train_df = train_df[train_df['star'] != 3].copy()
print(f"丢弃3星后训练集大小: {len(train_df)}")

# 二分类标签：4星及以上为正面（1）
train_df['sentiment'] = train_df['star'].apply(lambda x: 1 if x >= 4 else 0)

# 应用清洗
train_df['clean_review'] = train_df['review'].apply(clean_text)
test_df['clean_review'] = test_df['review'].apply(clean_text)

# 删除清洗后为空的样本
train_df = train_df[train_df['clean_review'].str.strip() != '']
print(f"清洗后训练集大小: {len(train_df)}")

# 类别分布
pos_count = train_df['sentiment'].sum()
neg_count = len(train_df) - pos_count
print(f"正面样本: {pos_count} ({pos_count/len(train_df):.2%})，负面样本: {neg_count} ({neg_count/len(train_df):.2%})")

# ------------------------------
# 3. 划分训练/验证集
# ------------------------------
X = train_df['clean_review']
y = train_df['sentiment']
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"训练集样本数: {len(X_train)}，验证集样本数: {len(X_val)}")

# ------------------------------
# 4. 文本序列化（适当增大词表和序列长度）
# ------------------------------
MAX_NB_WORDS = 8000          # 适当增大词表容量
MAX_SEQUENCE_LENGTH = 120    # 增加序列长度以保留更多信息

tokenizer = Tokenizer(num_words=MAX_NB_WORDS)
tokenizer.fit_on_texts(X_train)

train_sequences = tokenizer.texts_to_sequences(X_train)
val_sequences = tokenizer.texts_to_sequences(X_val)
test_sequences = tokenizer.texts_to_sequences(test_df['clean_review'])

X_train_pad = pad_sequences(train_sequences, maxlen=MAX_SEQUENCE_LENGTH)
X_val_pad = pad_sequences(val_sequences, maxlen=MAX_SEQUENCE_LENGTH)
X_test_pad = pad_sequences(test_sequences, maxlen=MAX_SEQUENCE_LENGTH)

print(f"训练数据形状: {X_train_pad.shape}")
print(f"验证数据形状: {X_val_pad.shape}")
print(f"测试数据形状: {X_test_pad.shape}")

# ------------------------------
# 5. 类别权重（解决不平衡）
# ------------------------------
classes = np.unique(y_train)
class_weights = compute_class_weight('balanced', classes=classes, y=y_train)
class_weight_dict = {0: class_weights[0], 1: class_weights[1]}
print(f"类别权重: {class_weight_dict}")

# ------------------------------
# 6. 构建 CNN + LSTM 混合模型
# ------------------------------
EMBEDDING_DIM = 128          # 嵌入维度
CONV_FILTERS = 128           # 卷积核数量
KERNEL_SIZE = 3              # 卷积窗口大小
LSTM_UNITS = 64              # LSTM 单元数
DROPOUT_RATE = 0.5

model = Sequential([
    Embedding(MAX_NB_WORDS, EMBEDDING_DIM, input_length=MAX_SEQUENCE_LENGTH,
              embeddings_regularizer=l2(1e-4)),
    
    # 第一个卷积层：提取局部 n-gram 特征
    Conv1D(filters=CONV_FILTERS, kernel_size=KERNEL_SIZE, activation='relu'),
    MaxPooling1D(pool_size=2),
    
    # 第二个卷积层：进一步提取更高阶特征
    Conv1D(filters=CONV_FILTERS*2, kernel_size=KERNEL_SIZE, activation='relu'),
    MaxPooling1D(pool_size=2),
    
    # LSTM 层：捕捉序列依赖关系
    LSTM(units=LSTM_UNITS, dropout=DROPOUT_RATE, recurrent_dropout=DROPOUT_RATE,
         kernel_regularizer=l2(1e-4)),
    
    Dropout(DROPOUT_RATE),
    Dense(64, activation='relu', kernel_regularizer=l2(1e-4)),
    Dropout(0.3),
    Dense(1, activation='sigmoid')
])

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()

# ------------------------------
# 7. 回调函数：早停 + 学习率衰减
# ------------------------------
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, min_lr=1e-6)
callbacks = [early_stop, reduce_lr]

# ------------------------------
# 8. 训练
# ------------------------------
history = model.fit(
    X_train_pad, y_train,
    batch_size=64,                # 增大 batch size 稳定梯度
    epochs=30,
    validation_data=(X_val_pad, y_val),
    class_weight=class_weight_dict,
    callbacks=callbacks,
    verbose=2
)

# ------------------------------
# 9. 验证集评估
# ------------------------------
val_loss, val_acc = model.evaluate(X_val_pad, y_val, verbose=0)
print(f"\n验证集准确率: {val_acc:.4f}")

# ------------------------------
# 10. 可视化训练曲线
# ------------------------------
def plot_training_history(history):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    ax1.plot(history.history['loss'], label='训练损失', marker='o')
    ax1.plot(history.history['val_loss'], label='验证损失', marker='s')
    ax1.set_title('训练与验证损失')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.legend()
    ax1.grid(True)
    
    ax2.plot(history.history['accuracy'], label='训练准确率', marker='o')
    ax2.plot(history.history['val_accuracy'], label='验证准确率', marker='s')
    ax2.set_title('训练与验证准确率')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('training_history_cnn_lstm.png', dpi=150)
    plt.show()

plot_training_history(history)

# ------------------------------
# 11. 混淆矩阵 & ROC 曲线
# ------------------------------
y_val_prob = model.predict(X_val_pad).flatten()
y_val_pred = (y_val_prob > 0.5).astype(int)

cm = confusion_matrix(y_val, y_val_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['负面', '正面'])
disp.plot(cmap='Blues')
plt.title('混淆矩阵 (验证集)')
plt.savefig('confusion_matrix_cnn_lstm.png')
plt.show()

fpr, tpr, _ = roc_curve(y_val, y_val_prob)
roc_auc = auc(fpr, tpr)
plt.figure()
plt.plot(fpr, tpr, label=f'AUC = {roc_auc:.3f}')
plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel('假正率')
plt.ylabel('真正率')
plt.title('ROC 曲线')
plt.legend()
plt.savefig('roc_curve_cnn_lstm.png')
plt.show()
print(f"验证集 AUC = {roc_auc:.3f}")

# ------------------------------
# 12. 测试集预测并保存
# ------------------------------
test_pred_prob = model.predict(X_test_pad)
test_pred = (test_pred_prob > 0.5).astype(int).flatten()
test_pred_label = ["正面" if p == 1 else "负面" for p in test_pred]

test_df['predicted_sentiment'] = test_pred
test_df['predicted_prob_positive'] = test_pred_prob
test_df['predicted_label'] = test_pred_label
test_df[['review', 'star', 'predicted_sentiment', 'predicted_prob_positive', 'predicted_label']].to_csv(
    "test_predictions_cnn_lstm.csv", index=False, encoding='utf-8-sig'
)
print("\n测试集预测结果已保存至 test_predictions_cnn_lstm.csv")

# 评估（因为测试集有真实标签）
from sklearn.metrics import accuracy_score, classification_report

y_true = (test_df['star'] >= 4).astype(int)
acc = accuracy_score(y_true, test_pred)
cm_test = confusion_matrix(y_true, test_pred)
report = classification_report(y_true, test_pred, target_names=['负面', '正面'])

print(f"\n测试集准确率: {acc:.4f}")
print("混淆矩阵:\n", cm_test)
print("\n分类报告:\n", report)

with open("test_evaluation_cnn_lstm.txt", "w", encoding='utf-8') as f:
    f.write(f"测试集准确率: {acc:.4f}\n\n")
    f.write("混淆矩阵:\n")
    f.write(np.array2string(cm_test) + "\n\n")
    f.write("分类报告:\n")
    f.write(report)

# ------------------------------
# 13. 保存模型和 tokenizer
# ------------------------------
os.makedirs("models", exist_ok=True)
model.save("models/cnn_lstm_model.h5")
with open("models/tokenizer_cnn_lstm.pkl", "wb") as f:
    pickle.dump(tokenizer, f)
print("模型已保存至 models/ 目录")