import pandas as pd
import matplotlib.pyplot as plt
import os

# 1. Ask for the file number
file_num = input("Enter the log file number to graph (e.g., 1): ")

# 2. Construct the relative path
relative_path = f"./loss_logs/{file_num}.csv"

# 3. Check if file exists and load it
if os.path.exists(relative_path):
    df = pd.read_csv(relative_path)
    
    # 4. Create the plot
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Left Axis: Costs
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Cost Value', color='tab:blue')
    ax1.plot(df['epoch'], df['optimal_cost'], label='Optimal Cost', color='tab:green', marker='o', linestyle='--')
    ax1.plot(df['epoch'], df['nn_cost'], label='NN Cost', color='tab:blue', marker='x')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.grid(True, alpha=0.3)

    # Right Axis: Loss
    ax2 = ax1.twinx()
    ax2.set_ylabel('Loss (MSE)', color='tab:red')
    ax2.plot(df['epoch'], df['loss'], label='Loss', color='tab:red', linewidth=2)
    ax2.tick_params(axis='y', labelcolor='tab:red')

    # Final Styling
    plt.title(f'Training Progress (File: {file_num}.csv)')
    fig.tight_layout()

    # Combine legends
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper left')

    plt.show()
else:
    print(f"Error: The file {relative_path} does not exist.")