# import tensorflow as tf
# from tensorflow.keras import layers, models
# import matplotlib
# matplotlib.use('Agg')  # 使用非交互式后端
# import matplotlib.pyplot as plt

# # 加载 CIFAR-10
# (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()

# # 归一化到 [0,1]
# x_train, x_test = x_train / 255.0, x_test / 255.0

# # 将标签从 (N,1) 压平为 (N,)
# y_train = y_train.flatten()
# y_test = y_test.flatten()

# # 构建 CNN 模型（输入形状为 32,32,3）
# model = models.Sequential([
#     layers.Conv2D(32, (3,3), activation='relu', input_shape=(32,32,3)),
#     layers.MaxPooling2D((2,2)),
#     layers.Conv2D(64, (3,3), activation='relu'),
#     layers.MaxPooling2D((2,2)),
#     layers.Conv2D(64, (3,3), activation='relu'),
#     layers.Flatten(),
#     layers.Dense(64, activation='relu'),
#     layers.Dropout(0.5),
#     layers.Dense(10, activation='softmax')
# ])

# model.compile(optimizer='adam',
#               loss='sparse_categorical_crossentropy',
#               metrics=['accuracy'])

# model.summary()

# # 训练
# history = model.fit(x_train, y_train,
#                     epochs=10,
#                     batch_size=64,
#                     validation_split=0.2,
#                     verbose=1)

# # 评估
# test_loss, test_acc = model.evaluate(x_test, y_test, verbose=2)
# print(f"Test accuracy: {test_acc:.4f}")

# # 绘制训练曲线并保存
# plt.plot(history.history['accuracy'], label='train_acc')
# plt.plot(history.history['val_accuracy'], label='val_acc')
# plt.legend()
# plt.title('Training and Validation Accuracy')
# plt.xlabel('Epoch')
# plt.ylabel('Accuracy')
# plt.savefig('cifar10_accuracy.png')
# plt.close()
# print("Saved: cifar10_accuracy.png")
import pandas as pd

# student_data={
#     "姓名":["张三","李四","王五"],
#     "科目":["数学","英语","物理"],
#     "成绩":["90","85","90"]
# }
# student_grades=pd.DataFrame(student_data)
# student_grades.to_csv('student_scores.csv',index=False,encoding='utf-8-sig')
student_grades = pd.read_csv(r'c:\Users\33083\Desktop\实训\sxun\student_scores.csv')
# print(student_grades)
# print(student_grades.head())
# print(student_grades.shape[0])
# print(student_grades.info())
# print(student_grades.describe())
# print(student_grades[student_grades['科目']=='数学'])
# print(student_grades[student_grades['成绩']>='90'])
# print(student_grades['科目'])
# print(student_grades[['科目','成绩']])
# print(student_grades.loc[[1,2]])
# print(student_grades.iloc[1])
# print(student_grades.loc[1,2])
print(student_grades.isnull().sum())
print(student_grades.dropna())
print(student_grades.fillna({'成绩':student_grades['成绩'].mean()},inplace=True))
print(student_grades.isnull().sum())
# df = pd.read_csv(r'c:\Users\330083\Desktop\实训\sxun\student_scores.csv')
