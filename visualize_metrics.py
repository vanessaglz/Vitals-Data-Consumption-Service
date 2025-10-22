import json
import matplotlib.pyplot as plt

with open('integrated_metrics_report.json') as f:
    data = json.load(f)

algo = data["algorithm_summary"]
user = data["user_metrics"]["summary"]

labels = ['Algorithm avg exec time', 'User avg response time']
values = [algo["avg_execution_time"], user["average_response_time"]]

plt.figure(figsize=(7,4))
plt.bar(labels, values, color=['#4CAF50', '#2196F3'])
plt.ylabel("Seconds")
plt.title("Performance Comparison: Algorithm vs User Endpoints")
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()