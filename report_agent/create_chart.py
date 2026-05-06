import matplotlib.pyplot as plt
import pandas as pd
import os

# Data
categories = ['Computers', 'Telephony']
revenue = [166871.75, 55904.30]
orders = [153, 257]

# Create figure
fig, ax1 = plt.subplots(figsize=(10, 6))

# Bar chart for Revenue
color = 'tab:blue'
ax1.set_xlabel('Product Category')
ax1.set_ylabel('Total Revenue', color=color)
ax1.bar(categories, revenue, color=color, alpha=0.6, label='Revenue')
ax1.tick_params(axis='y', labelcolor=color)

# Line chart for Orders
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Order Count', color=color)
ax2.plot(categories, orders, color=color, marker='o', linewidth=2, label='Orders')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('Revenue vs. Order Volume by Category')
plt.tight_layout()

# Save
output_dir = 'D:/src/report_agent/results/report_20260506_171712'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
plt.savefig(os.path.join(output_dir, 'category_performance.png'))
