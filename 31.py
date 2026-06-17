import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split, learning_curve
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# 1. 生成模拟数据
X, y = make_regression(n_samples=100, n_features=3, noise=5, random_state=1)

# 映射特征到实际业务范围
X[:, 0] = np.interp(X[:, 0], (X[:, 0].min(), X[:, 0].max()), (50, 200))   # 手机价格
X[:, 1] = np.interp(X[:, 1], (X[:, 1].min(), X[:, 1].max()), (50, 100))   # 成本价格
X[:, 2] = np.interp(X[:, 2], (X[:, 2].min(), X[:, 2].max()), (1, 50))     # 营销成本
y = np.interp(y, (y.min(), y.max()), (0, 100))                            # 利润
y = np.round(y, 2).astype(int)

print("特征矩阵形状:", X.shape)
print("目标向量形状:", y.shape)
print("前3个样本:\n", X[:3])
print("前3个利润:", y[:3])

# 2. 划分数据集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

# 3. 标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 4. 训练模型
model = LinearRegression()
model.fit(X_train_scaled, y_train)

# 5. 预测
y_train_pred = model.predict(X_train_scaled)
y_test_pred = model.predict(X_test_scaled)

# 6. 评估指标
train_mse = mean_squared_error(y_train, y_train_pred)
test_mse = mean_squared_error(y_test, y_test_pred)
train_r2 = r2_score(y_train, y_train_pred)
test_r2 = r2_score(y_test, y_test_pred)

print("\n=== 模型评估 ===")
print(f"训练集 MSE: {train_mse:.2f}, R²: {train_r2:.4f}")
print(f"测试集 MSE: {test_mse:.2f}, R²: {test_r2:.4f}")
print(f"模型系数: {model.coef_}")
print(f"模型截距: {model.intercept_:.2f}")

# ==================== 可视化 ====================
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 图1：真实 vs 预测
plt.figure(figsize=(6,5))
plt.scatter(y_test, y_test_pred, alpha=0.7)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2)
plt.xlabel("真实利润")
plt.ylabel("预测利润")
plt.title("线性回归预测效果 (测试集)")
plt.show()

# 图2：残差图
residuals = y_test - y_test_pred
plt.figure(figsize=(6,5))
plt.scatter(y_test_pred, residuals, alpha=0.7)
plt.axhline(y=0, color='r', linestyle='--', lw=2)
plt.xlabel("预测利润")
plt.ylabel("残差")
plt.title("残差图 (测试集)")
plt.show()

# 图3：残差直方图 + Q-Q图
plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
plt.hist(residuals, bins=15, edgecolor='black', alpha=0.7)
plt.xlabel("残差")
plt.ylabel("频数")
plt.title("残差分布直方图")
plt.subplot(1,2,2)
try:
    import scipy.stats as stats
    stats.probplot(residuals, dist="norm", plot=plt)
    plt.title("Q-Q 图")
except ImportError:
    plt.text(0.5, 0.5, "需安装 scipy", ha='center', va='center')
    plt.title("Q-Q 图 (未安装)")
plt.tight_layout()
plt.show()

# 图4：系数条形图
features = ['手机价格', '成本价格', '营销成本']
coeffs = model.coef_
plt.figure(figsize=(6,4))
plt.bar(features, coeffs, color=['blue', 'green', 'orange'])
plt.axhline(y=0, color='black', linewidth=0.5)
plt.ylabel("系数值")
plt.title("线性回归系数")
for i, v in enumerate(coeffs):
    plt.text(i, v + (0.1 if v>=0 else -0.3), f"{v:.2f}", ha='center')
plt.show()

# 图5：R²对比
plt.figure(figsize=(5,4))
plt.bar(['训练集', '测试集'], [train_r2, test_r2], color=['blue', 'orange'])
plt.ylim(0, 1)
plt.ylabel("R²")
plt.title("模型在训练集和测试集上的表现")
for i, v in enumerate([train_r2, test_r2]):
    plt.text(i, v + 0.02, f"{v:.4f}", ha='center')
plt.show()

# 图6：每个特征与利润的关系
plt.figure(figsize=(12,4))
for i, feat_name in enumerate(features):
    plt.subplot(1,3,i+1)
    plt.scatter(X[:, i], y, alpha=0.6)
    plt.xlabel(feat_name)
    plt.ylabel("利润")
    plt.title(f"{feat_name} vs 利润")
plt.tight_layout()
plt.show()

# 图7：绝对误差箱线图
train_abs_err = np.abs(y_train - y_train_pred)
test_abs_err = np.abs(y_test - y_test_pred)
plt.figure(figsize=(5,4))
plt.boxplot([train_abs_err, test_abs_err], labels=['训练集', '测试集'])
plt.ylabel("绝对误差")
plt.title("预测绝对误差分布")
plt.show()

# 图8：学习曲线
train_sizes, train_scores, test_scores = learning_curve(
    LinearRegression(), X_train_scaled, y_train, train_sizes=np.linspace(0.1, 1.0, 10),
    cv=5, scoring='r2', random_state=1
)
train_mean = np.mean(train_scores, axis=1)
test_mean = np.mean(test_scores, axis=1)
plt.figure(figsize=(6,5))
plt.plot(train_sizes, train_mean, 'o-', label='训练集 R²')
plt.plot(train_sizes, test_mean, 'o-', label='交叉验证 R²')
plt.xlabel("训练样本数")
plt.ylabel("R²")
plt.title("学习曲线")
plt.legend()
plt.grid(True)
plt.show()