import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA, NMF
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
import tensorflow as tf
import csv

data = {"date": [], "time": [], "humidity": [], "temperature": []}

with open('temp_hum_training_data.csv', newline='') as csvfile:
    temp_hum_reader = csv.reader(csvfile, delimiter=' ')
    for i, row in enumerate(temp_hum_reader):

        if i == 0:
            continue

        result = row[0].split(",")
        date_time = result[0].split(" ")

        #print(i)
        #print(date_time[0])
        #print(date_time[1])
        #print(int(result[1].replace("\"", "")))
        #print(int(result[2].replace("\"", "")))

        data["date"] = date_time[0]
        data["time"] = date_time[1]
        data["temperature"].append(int(result[1].replace("\"", "")))
        data["humidity"].append(int(result[2].replace("\"", "")))


# Example synthetic data structure
# Replace this with real data collected from the Raspberry Pi Pico

"""data = {
    "humidity": np.random.uniform(20, 80, 1000),
    "temperature": np.random.uniform(10, 40, 1000),
}"""

df = pd.DataFrame(data)
df = df[["humidity", "temperature"]]

print(df.columns)

# Convert all columns to numeric, coerce errors to null values
for c in df.columns:
    df[c] = pd.to_numeric(df[c], errors='coerce')

# Preprocessing pipeline
num_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="mean")),
    ("scaler", StandardScaler()),
])

# KMeans Clustering with Grid Search
pipeline = Pipeline([
    ("preprocessing", num_pipeline),
    ("kmeans", KMeans()),
])

param_grid = {
    "kmeans__n_clusters": [2, 3, 4, 5, 6],
    "kmeans__init": ["k-means++", "random"],
    "kmeans__n_init": [10, 20],
    "kmeans__max_iter": [300, 500],
}

grid_search = GridSearchCV(estimator=pipeline, param_grid=param_grid, cv=5, verbose=1)
grid_search.fit(df)

best_model = grid_search.best_estimator_
cluster_labels = best_model.predict(df)

# Visualize clusters with pairwise plots
features = df.columns
for i, feature1 in enumerate(features):
    for j, feature2 in enumerate(features):
        if i < j:
            plt.scatter(df[feature1], df[feature2], c=cluster_labels, cmap="viridis", alpha=0.6)
            plt.title(f"Clusters: {feature1.capitalize()} vs {feature2.capitalize()}")
            plt.xlabel(feature1.capitalize())
            plt.ylabel(feature2.capitalize())
            plt.colorbar(label="Cluster")
            plt.show()

# Isolation Forest for Anomaly Detection
isolation_forest = IsolationForest(random_state=42)
anomaly_labels = isolation_forest.fit_predict(df)

# Visualize anomalies with pairwise plots
for i, feature1 in enumerate(features):
    for j, feature2 in enumerate(features):
        if i < j:
            plt.scatter(df[feature1], df[feature2], c=anomaly_labels, cmap="coolwarm", alpha=0.6)
            plt.title(f"Anomalies: {feature1.capitalize()} vs {feature2.capitalize()}")
            plt.xlabel(feature1.capitalize())
            plt.ylabel(feature2.capitalize())
            plt.colorbar(label="Anomaly")
            plt.show()

# Linear Regression for Forecasting
X = df.drop("temperature", axis=1)
y = df["temperature"]
x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

reg_pipeline = Pipeline([
    ("preprocessing", num_pipeline),
    ("regressor", LinearRegression()),
])

reg_pipeline.fit(x_train, y_train)
predictions = reg_pipeline.predict(x_test)

# Visualize regression predictions
plt.scatter(y_test, predictions, alpha=0.6, label="Predicted vs True")
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], color="red", linestyle="--", label="Ideal Fit")
plt.title("Linear Regression Predictions")
plt.xlabel("True Temperature")
plt.ylabel("Predicted Temperature")
plt.legend()
plt.show()

print("Linear Regression R^2 score:", reg_pipeline.score(x_test, y_test))

# Tiny Neural Network for Outlier Detection
anomaly_labels_binary = (anomaly_labels == -1).astype(int)

model = Sequential([
    Dense(16, activation='relu', input_dim=len(features)),
    Dense(8, activation='relu'),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

X_train_nn, X_test_nn, y_train_nn, y_test_nn = train_test_split(df, anomaly_labels_binary, test_size=0.2, random_state=42)

history = model.fit(X_train_nn, y_train_nn, epochs=50, batch_size=32, validation_split=0.2, verbose=1)

# Evaluate the model
loss, accuracy = model.evaluate(X_test_nn, y_test_nn)
print(f"Tiny Neural Network Accuracy: {accuracy * 100:.2f}%")

# Visualize training process
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

# Quantization and TensorFlow Lite Conversion
#converter = tf.lite.TFLiteConverter.from_keras_model(model)
#converter.optimizations = [tf.lite.Optimize.DEFAULT]
#tflite_model = converter.convert()

# Save the TensorFlow Lite model
#with open("tiny_nn_model.tflite", "wb") as f:
#    f.write(tflite_model)

#print("Tiny Neural Network model converted to TensorFlow Lite format and saved.")