import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Load Boston housing dataset from original source
data_url = "http://lib.stat.cmu.edu/datasets/boston"
raw_df = pd.read_csv(data_url, sep="\s+", skiprows=22, header=None)
data = np.hstack([raw_df.values[::2, :], raw_df.values[1::2, :2]])
target = raw_df.values[1::2, 2]

# Feature names
feature_names = [
    'CRIM', 'ZN', 'INDUS', 'CHAS', 'NOX', 'RM', 
    'AGE', 'DIS', 'RAD', 'TAX', 'PTRATIO', 'B', 'LSTAT'
]

print("=== Boston Housing Dataset ===")
print("Feature names:", feature_names)
print(f"Data shape: features={data.shape}, target={target.shape}")

# Create DataFrame
df = pd.DataFrame(data, columns=feature_names)
df['PRICE'] = target

# Data exploration
print("\n=== First 5 rows ===")
print(df.head())

print("\n=== Data statistics ===")
print(df.describe())

print("\n=== Correlation with PRICE ===")
corr_matrix = df.corr()
print(corr_matrix['PRICE'].sort_values(ascending=False))

# Visualization - save to files
plt.figure(figsize=(12, 6))

# Price distribution
plt.subplot(1, 2, 1)
sns.histplot(df['PRICE'], bins=30, kde=True)
plt.title('Price Distribution')
plt.xlabel('Price ($1000s)')

# RM vs Price
plt.subplot(1, 2, 2)
sns.scatterplot(x='RM', y='PRICE', data=df)
plt.title('RM vs Price')
plt.xlabel('Average Number of Rooms')
plt.ylabel('Price ($1000s)')

plt.tight_layout()
plt.savefig('boston_price_dist.png')
plt.close()
print("\nSaved: boston_price_dist.png")

# Correlation heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Feature Correlation Heatmap')
plt.savefig('boston_corr_heatmap.png')
plt.close()
print("Saved: boston_corr_heatmap.png")

# Linear Regression Model
X = df.drop('PRICE', axis=1)
y = df['PRICE']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

# Model evaluation
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print("\n=== Model Evaluation ===")
print(f"Mean Squared Error (MSE): {mse:.2f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
print(f"R-squared Score: {r2:.4f}")

# Feature importance
feature_importance = pd.DataFrame({
    'Feature': feature_names,
    'Coefficient': model.coef_
})
feature_importance = feature_importance.sort_values(by='Coefficient', ascending=False)

print("\n=== Feature Importance ===")
print(feature_importance)

# Prediction visualization
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
plt.title('Actual vs Predicted Prices')
plt.xlabel('Actual Price')
plt.ylabel('Predicted Price')
plt.savefig('boston_predictions.png')
plt.close()
print("\nSaved: boston_predictions.png")
print("\n=== Done ===")