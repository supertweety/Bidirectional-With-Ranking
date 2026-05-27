import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns # Used for the KDE (line distribution) plots
import os # Used for creating the output folder

# --- Data Loading Update: Read from CSV ---
# Assumes the data is in a comma-separated format in 'search_results.csv'
try:
    df = pd.read_csv('search_results.csv')
except FileNotFoundError:
    print("Error: 'search_results.csv' not found. Please ensure the file is in the current directory.")
# Clean Column Names and Filter meaningful columns
df.columns = df.columns.str.strip()
columns_to_keep = [col for col in df.columns if col.startswith('Epoch_') or col in ['Algorithm', 'Noise_Type']]
df = df[columns_to_keep]

# Post-process: Revert algorithm names back to their original form
df['Algorithm'] = (
    df['Algorithm']
    .replace('Standard_Bidirectional', 'Standard Bidirectional')
    .replace('Front_to_Front', 'Front-to-Front')
    .replace('A_star', 'A*')
)

# Define epoch columns and calculate Mean_Performance
epoch_cols = [f'Epoch_{i}' for i in range(1, 11)]
df['Mean_Performance'] = df[epoch_cols].mean(axis=1)


# --- 2. Setup: Create Output Folder ---

OUTPUT_FOLDER = 'graph_results'
os.makedirs(OUTPUT_FOLDER, exist_ok=True) # Creates the folder if it doesn't exist


# --- 3. Bar Chart: Additive Noise Comparison (Mean Performance) ---

df_additive_bar = df[df['Noise_Type'] == 'additive'].sort_values(by='Mean_Performance', ascending=False)

plt.figure(figsize=(8, 6))
plt.bar(df_additive_bar['Algorithm'], df_additive_bar['Mean_Performance'], color=['skyblue', 'lightgreen', 'red'])
plt.title('Average Performance of Algorithms with Additive Noise')
plt.xlabel('Algorithm')
plt.ylabel('Average Performance (Mean)')
plt.xticks(rotation=30, ha='right')
plt.grid(axis='y', linestyle='--')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, 'bar_chart_additive_mean.png'))
plt.close()

# --- 4. Bar Chart: Multiplicative Noise Comparison (Mean Performance) ---

df_multiplicative_bar = df[df['Noise_Type'] == 'multiplicative'].sort_values(by='Mean_Performance', ascending=False)

plt.figure(figsize=(8, 6))
plt.bar(df_multiplicative_bar['Algorithm'], df_multiplicative_bar['Mean_Performance'], color=['salmon', 'gold', 'purple'])
plt.title('Average Performance of Algorithms with Multiplicative Noise')
plt.xlabel('Algorithm')
plt.ylabel('Average Performance (Mean)')
plt.xticks(rotation=30, ha='right')
plt.grid(axis='y', linestyle='--')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, 'bar_chart_multiplicative_mean.png'))
plt.close()

# --- 5. Distributions/Line Plots: Prep Melted Data ---

# Melt the DataFrame for distribution analysis
df_melted = df.melt(id_vars=['Algorithm', 'Noise_Type'],
                    value_vars=epoch_cols,
                    var_name='Epoch',
                    value_name='Performance')


# --- 6. KDE Plot (Line Distribution): Additive Noise ---

df_additive_kde = df_melted[df_melted['Noise_Type'] == 'additive']
additive_groups = df_additive_kde['Algorithm'].unique()
additive_colors = ['skyblue', 'lightgreen', 'red']

plt.figure(figsize=(10, 6))
for i, group in enumerate(additive_groups):
    # Use seaborn.kdeplot for the smooth line distribution
    sns.kdeplot(df_additive_kde[df_additive_kde['Algorithm'] == group]['Performance'],
                label=group,
                color=additive_colors[i],
                fill=True, # Fill under the curve for better visibility
                alpha=0.2)

plt.title('Distribution Shape (KDE) of Performance - Additive Noise')
plt.xlabel('Performance Value')
plt.ylabel('Density')
plt.legend(title='Algorithm')
plt.grid(axis='y', linestyle='--')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, 'kde_plot_additive_distribution.png'))
plt.close()

# --- 7. KDE Plot (Line Distribution): Multiplicative Noise ---

df_multiplicative_kde = df_melted[df_melted['Noise_Type'] == 'multiplicative']
multiplicative_groups = df_multiplicative_kde['Algorithm'].unique()
multiplicative_colors = ['salmon', 'gold', 'purple']

plt.figure(figsize=(10, 6))
for i, group in enumerate(multiplicative_groups):
    # Use seaborn.kdeplot for the smooth line distribution
    sns.kdeplot(df_multiplicative_kde[df_multiplicative_kde['Algorithm'] == group]['Performance'],
                label=group,
                color=multiplicative_colors[i],
                fill=True, # Fill under the curve for better visibility
                alpha=0.2)

plt.title('Distribution Shape (KDE) of Performance - Multiplicative Noise')
plt.xlabel('Performance Value')
plt.ylabel('Density')
plt.legend(title='Algorithm')
plt.grid(axis='y', linestyle='--')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, 'kde_plot_multiplicative_distribution.png'))
plt.close()

print(f"The code is updated to save all four plots inside the '{OUTPUT_FOLDER}' folder and uses KDE plots for smooth distribution shapes.")