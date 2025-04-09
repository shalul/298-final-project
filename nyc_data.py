import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Specify the path to your .tsv file
file_path = 'data.tsv'

# Read the TSV file using pandas
try:
    tsv_df = pd.read_csv(file_path, sep='\t')
    
    # Check if provided headers match expectations
    expected_headers = [
        "ZCTA20", "ZCTA_AREA20", "TOT_POP_2020", 
        "COUNT_NTM_STOPS", "STOPS_PER_CAPITA", "STOPS_PER_SQMILE"
    ]
    
    if all(header in tsv_df.columns for header in expected_headers):
        print("File read successfully. Data:")
        print(tsv_df.head())  # print first few lines of the DataFrame
    else:
        print("Headers in the file do not match the expected headers.")

except Exception as e:
    print(f"An error occurred while reading the file: {e}")

# Call the function
#read_tsv(file_path)

#------
# Load the CSV file into a DataFrame
csv_df = pd.read_csv('2024_household_data.csv')

# Check if the DataFrame has at least 25 columns
if len(csv_df.columns) >= 24:
   
    column_24 = csv_df.iloc[:, 24]  # Columns are zero-based
    column_1 = csv_df.iloc[:, 1]  # Columns are zero-based
    print("Col 24", column_24)            # Print or otherwise process the column
    print("Col 1", column_1)
else:
    print("The DataFrame does not have 25 columns.")

if tsv_df is not None and csv_df is not None:
    # Assuming zip_code_column_csv is the column with the "ZCTA5" style entries
    if 'NAME' in csv_df.columns:
        # Extract and assign the formatted ZIP codes to a new column in csv_df
        zip_code_formatted = (
            csv_df['NAME'].str.extract(r'ZCTA5 (\d{5})')[0]
        )
        
        # Fill any NaN values as appropriate, e.g., use '00000' or another placeholder
        zip_code_formatted = zip_code_formatted.fillna('-1')
        #csv_df['NAME'] = zip_code_formatted.astype('int64')

    tsv_df['ZCTA20'] = tsv_df['ZCTA20'].astype(str)
    csv_df['NAME'] = csv_df['NAME'].astype(str)
    # Perform an inner join on the ZIP code
    merged_df = pd.merge(tsv_df, csv_df, left_on='ZCTA20', right_on=zip_code_formatted, how='inner')

    
    #for c in merged_df.columns:
    #    print(c)
    # Specify the necessary columns to print
    columns_to_print = ['NAME', 'S1901_C01_012E', 'STOPS_PER_CAPITA']

    # Assuming 'median_income_column_name' corresponds to your actual median income column in csv_df
    if all(col in merged_df.columns for col in columns_to_print):
        print("Selected Data:")
        print(merged_df[columns_to_print].head().to_string(index=False))
    else:
        missing_cols = [col for col in columns_to_print if col not in merged_df.columns]
        print(f"Missing expected columns in merged DataFrame: {missing_cols}")

    #filtered_df = merged_df[merged_df['S1901_C01_012E'] != 0]
    sorted_df = merged_df.sort_values(by='S1901_C01_012E', ascending=False)


    # Display the first few rows of the merged DataFrame
    #print("Merged Data:")
    #print(merged_df.head())

    # # Setup the plot
    # plt.figure(figsize=(10, 6))

    # # Scatter plot for income vs stops per capita
    # plt.scatter(sorted_df['S1901_C01_012E'].head(10), sorted_df['STOPS_PER_CAPITA'].head(10), alpha=0.6)

    # # Set plot title and labels
    # plt.title('Scatter Plot of Income vs Stops Per Capita')
    # plt.xlabel('Median Income (dollars)')
    # plt.ylabel('Stops Per Capita')

    # # Optionally, set limits for axes if needed
    # # plt.xlim(merged_df[income_column].min(), merged_df[income_column].max())
    # # plt.ylim(merged_df[stops_column].min(), merged_df[stops_column].max())

    # # Show grid
    # plt.grid(True)

    # # Display the plot
    # plt.show()

    # Assuming merged_df is your dataframe with the joined data
    
   # First, convert income and stops per capita to numeric values
   
   # First, convert income and stops per capita to numeric values
    merged_df['S1901_C01_012E'] = pd.to_numeric(merged_df['S1901_C01_012E'], errors='coerce')
    merged_df['STOPS_PER_CAPITA'] = pd.to_numeric(merged_df['STOPS_PER_CAPITA'], errors='coerce')

    # Convert ZCTA20 to numeric (assuming this is your ZIP code column)
    merged_df['ZCTA20'] = pd.to_numeric(merged_df['ZCTA20'], errors='coerce')

    # Filter for ZIP codes within the NYC range (10001 to 11210)
    nyc_df = merged_df[
        (merged_df['ZCTA20'] >= 10001) & 
        (merged_df['ZCTA20'] <= 11210)
    ]

    # Now filter out any NaN or zero values
    filtered_df = nyc_df.dropna(subset=['S1901_C01_012E', 'STOPS_PER_CAPITA'])
    filtered_df = filtered_df[
        (filtered_df['S1901_C01_012E'] > 0) & 
        (filtered_df['STOPS_PER_CAPITA'] > 0)
    ]

    # Print how many ZIP codes we have in our filtered dataset
    print(f"Number of NYC ZIP codes in analysis: {len(filtered_df)}")


    # Create income bins
    num_bins = 10
    min_income = filtered_df['S1901_C01_012E'].min()
    max_income = filtered_df['S1901_C01_012E'].max()
    income_bins = np.linspace(min_income, max_income, num_bins + 1)

    # Assign income bins and create labels
    bin_labels = [f"${int(income_bins[i]):,}-${int(income_bins[i+1]):,}" for i in range(num_bins)]
    filtered_df['income_bin'] = pd.cut(
        filtered_df['S1901_C01_012E'], 
        bins=income_bins,
        labels=bin_labels
    )

    # Group by income bin and calculate mean stops per capita
    grouped_df = filtered_df.groupby('income_bin')['STOPS_PER_CAPITA'].mean().reset_index()

    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [2, 1]})

    # Plot 1: Histogram of income distribution
    ax1.hist(filtered_df['S1901_C01_012E'], bins=income_bins, alpha=0.7, color='skyblue')
    ax1.set_title('Distribution of Median Income by ZIP Code')
    ax1.set_xlabel('Median Income (dollars)')
    ax1.set_ylabel('Count of ZIP Codes')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

    # Plot 2: Bar chart of average stops per capita by income bin
    bar_plot = sns.barplot(
        x='income_bin', 
        y='STOPS_PER_CAPITA', 
        data=grouped_df,
        ax=ax2,
        palette='viridis'
    )

    # Rotate x-axis labels for better readability
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    ax2.set_title('Average Stops Per Capita by Income Range')
    ax2.set_xlabel('Income Range')
    ax2.set_ylabel('Average Stops Per Capita')
    ax2.grid(axis='y', linestyle='--', alpha=0.7)

    # Adjust layout
    plt.tight_layout()
    plt.show()

    # Print some statistics to understand the relationship better
    print("Correlation between income and stops per capita:", 
        filtered_df['S1901_C01_012E'].corr(filtered_df['STOPS_PER_CAPITA']))

    # Show summary of data by income bin
    print("\nSummary statistics by income bin:")
    summary_stats = filtered_df.groupby('income_bin').agg({
        'STOPS_PER_CAPITA': ['mean', 'min', 'max', 'count'],
        'S1901_C01_012E': ['mean', 'min', 'max']
    }).round(4)
    print(summary_stats)

    # Add correlation analysis
    correlation = filtered_df['S1901_C01_012E'].corr(filtered_df['STOPS_PER_CAPITA'])
    print(f"Correlation between income and stops per capita: {correlation:.3f}")

    # Calculate disparity ratios between lowest and highest income brackets
    lowest_income_stops = grouped_df.iloc[0]['STOPS_PER_CAPITA']
    highest_income_stops = grouped_df.iloc[-1]['STOPS_PER_CAPITA']
    disparity_ratio = lowest_income_stops / highest_income_stops
    print(f"Disparity ratio: Low-income communities experience {disparity_ratio:.1f}x more stops per capita")

    # Add regression line to visualize the relationship
    import statsmodels.api as sm
    X = sm.add_constant(filtered_df['S1901_C01_012E'])
    model = sm.OLS(filtered_df['STOPS_PER_CAPITA'], X).fit()
    print(model.summary())


else:
    print("Could not join the files due to errors in reading or header mismatch.")