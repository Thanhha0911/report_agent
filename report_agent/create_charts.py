import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Data
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
revenue = [1097271.56, 978493.00, 1150389.34, 1154551.62, 1144762.11, 1020381.90, 1039704.51, 996973.51, 166.46]

categories = ['health_beauty', 'watches_gifts', 'bed_bath_table', 'sports_leisure', 'computers_accessories', 
              'housewares', 'furniture_decor', 'auto', 'baby', 'cool_stuff']
cat_revenue = [772238.15, 708850.94, 538069.26, 532566.49, 505476.31, 399888.10, 386668.59, 347631.15, 256800.70, 240559.20]

# Set style
sns.set_theme(style="whitegrid")

# Create Figure
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))

# Plot 1: Monthly Revenue
ax1.plot(months, revenue, marker='o', color='b', linestyle='-', linewidth=2)
ax1.set_title('Monthly Revenue Trend - 2018', fontsize=14)
ax1.set_ylabel('Revenue (USD)')

# Plot 2: Top Categories
sns.barplot(x=cat_revenue, y=categories, palette='viridis', ax=ax2)
ax2.set_title('Top 10 Product Categories by Revenue - 2018', fontsize=14)
ax2.set_xlabel('Revenue (USD)')

plt.tight_layout()
plt.savefig('D:/src/report_agent/results/report_20260506_165044/revenue_analysis_2018.png')
