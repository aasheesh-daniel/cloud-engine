import pandas as pd
import numpy as np
import json

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Simulate historical telemetry data (CPU utilization %)
np.random.seed(42)
timestamps = pd.date_range(start="2026-10-01", periods=100, freq="min")
cpu_usage = np.random.normal(loc=45, scale=5, size=100) + np.linspace(0, 20, 100)  #: Creates 100 random data points centered around 45% CPU usage (loc=45), with natural ups and downs of roughly ±5% (scale=5). This represents normal, noisy server activity.

df = pd.DataFrame({"timestamp": timestamps, "cpu_usage": cpu_usage})

#  Compute rolling window feature for prediction
df["rolling_avg"] = df["cpu_usage"].rolling(window=5).mean()    #Raw server metrics jump up and down erratically second-by-second. Calculating a rolling window smooths out brief random spikes so our forecasting model can detect genuine upward traffic trends

print("Telemetry Data Sample:")
print(df.tail(5))
print("\nPython forecasting environment is ready!")


#  Create target variable: next minute's CPU usage
df["target"] = df["cpu_usage"].shift(-1)

# Clean up rows with NaN values resulting from the shift
df_ml = df.dropna().copy()   #deletes rows with missing values (the first 4 rows from the 5-minute rolling average, plus the last row from the shift). because ml algo fails if we feed them empty data 

# Define features (X) and target (y)
X = df_ml[["cpu_usage", "rolling_avg"]]  #What the model gets to look at—the current CPU and the 5-minute rolling trend.
y = df_ml["target"]    #What the model is trying to predict—the upcoming CPU.

# Chronological split for time-series data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)   #shuffle=False: Crucial for time-series data. In regular ML, you shuffle cards, but with server traffic, you cannot look into the future to predict the past. The data must stay in chronological order.

# Train the model
model = RandomForestRegressor(n_estimators=100, random_state=42)  #An algorithm made of 100 decision trees that work together like a panel of judges to predict numbers.random_state=42: That same seed rule—it locks the internal math so the forest builds the exact same trees every time you run it. 
model.fit(X_train, y_train)

# Predict the next minute
latest_data = df[["cpu_usage", "rolling_avg"]].tail(1)
predicted_cpu = model.predict(latest_data)

print("\nML Model Trained Successfully!")
print(f"Current CPU Usage: {latest_data['cpu_usage'].values[0]:.2f}%")
print(f"Predicted CPU Usage for Next Minute: {predicted_cpu[0]:.2f}%")




# Scaling Decision Logic & Terraform Trigger

CPU_HIGH_THRESHOLD = 70.0
CPU_LOW_THRESHOLD = 30.0

next_cpu = predicted_cpu[0]
action = "HOLD"
target_capacity = 2  # Baseline capacity

if next_cpu > CPU_HIGH_THRESHOLD:
    action = "SCALE_OUT"
    target_capacity = 5
elif next_cpu < CPU_LOW_THRESHOLD:
    action = "SCALE_IN"
    target_capacity = 1

decision_payload = {
    "action": action,
    "predicted_cpu": round(float(next_cpu), 2),   #Scikit-learn outputs a NumPy float data type (numpy.float64), which Python's standard json.dump() cannot read and will crash on and that round um (Trims endless decimals (like 55.1548921...%) down to just two clean decimal places (55.15%) for clean, readable JSON.)
    "desired_capacity": target_capacity
}

# Write decision to an output file that Terraform / Orchestrator can ingest
with open("scaling_decision.json", "w") as f:   
    json.dump(decision_payload, f, indent=4)  #Dump this JSON data directly into f and indent = 4 means to format the JSON text with 4 spaces of indentation to make it pretty and human-readable.

print("\n--- Scaling Decision Engine ---")
print(f"Action: {action}")
print(f"Target Capacity: {target_capacity} instances")
print("Saved decision to 'scaling_decision.json' successfully!")