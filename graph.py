import csv

# --- 1. Define the Data ---
# The data is structured as a list of lists.
# Each inner list corresponds to one row in the output file.
# NOTE: Replace this placeholder data with your actual experimental averages (10 values per row).

data_rows = [
    # Header Row
    ['Algorithm', 'Noise_Type', 'Epoch_1', 'Epoch_2', 'Epoch_3', 'Epoch_4', 'Epoch_5', 'Epoch_6', 'Epoch_7', 'Epoch_8', 'Epoch_9', 'Epoch_10'],
    
    # # A* Results
    # ['A*', 'Additive', 102.5, 104.1, 103.8, 105.5, 108.0, 110.2, 111.9, 113.5, 114.0, 115.1],
    # ['A*', 'Multiplicative', 150.3, 152.0, 155.6, 158.1, 160.0, 162.5, 163.0, 164.8, 165.9, 167.0],
    
    # # Bidirectional Search Results
    # ['Bidirectional', 'Additive', 88.1, 89.5, 87.9, 90.1, 91.5, 92.0, 93.1, 94.5, 95.0, 96.1],
    # ['Bidirectional', 'Multiplicative', 130.5, 132.8, 135.0, 137.1, 139.5, 142.0, 144.1, 146.5, 148.8, 150.0],
    
    # # Front-to-Front Search Results
    # ['Front-to-Front', 'Additive', 75.3, 76.0, 77.1, 78.5, 79.0, 80.2, 81.5, 82.9, 84.0, 85.1],
    # ['Front-to-Front', 'Multiplicative', 110.0, 112.5, 114.8, 116.9, 119.0, 121.5, 123.8, 126.0, 128.5, 130.0],
]

# --- 2. Write to File ---
file_name = 'search_results.csv'

try:
    # 'w' mode for writing (overwrites if file exists)
    # newline='' is important to prevent extra blank rows in the file
    with open(file_name, 'w', newline='') as file:
        # Use csv.writer, specifying the tab '\t' as the delimiter
        writer = csv.writer(file, delimiter='\t')
        
        # Write all the rows at once
        writer.writerows(data_rows)
        
    print(f"Successfully initialized and wrote data to '{file_name}'")
    
except IOError as e:
    print(f"Error writing file: {e}")