import tensorflow as tf
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt

# 加载数据
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.fashion_mnist.load_data()

# 归一化
x_train, x_test = x_train / 255.0, x_test / 255.0

# 构建模型
model = models.Sequential([
    layers.Reshape((28, 28, 1), input_shape=(28, 28)),
    layers.Conv2D(32, (5, 5), activation='relu'),
    layers.MaxPooling2D(2, 2),
    layers.Conv2D(64, (5, 5), activation='relu'),
    layers.MaxPooling2D(2, 2),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(10, activation='softmax')
])

# 编译模型
model.compile(optimizer='rmsprop',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# 训练模型
history = model.fit(
    x_train, y_train,
    epochs=10,
    batch_size=32,
    validation_split=0.2,
    shuffle=True,
    verbose=1
)
# 训练后评估
test_loss, test_acc = model.evaluate(x_test, y_test, verbose=2)
print(f"Test accuracy: {test_acc:.4f}")

# 预测前5个样本并展示结果
predictions = model.predict(x_test[:5])
pred_labels = tf.argmax(predictions, axis=1).numpy()
class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

print("预测标签:", [class_names[i] for i in pred_labels])
print("真实标签:", [class_names[i] for i in y_test[:5]])

plt.figure(figsize=(12,4))
plt.subplot(1,2,1)
plt.plot(history.history['accuracy'], label='train_acc')
plt.plot(history.history['val_accuracy'], label='val_acc')
plt.legend()
plt.title('Accuracy')

plt.subplot(1,2,2)
plt.plot(history.history['loss'], label='train_loss')
plt.plot(history.history['val_loss'], label='val_loss')
plt.legend()
plt.title('Loss')
plt.show()

# 查看模型结构
model.summary()