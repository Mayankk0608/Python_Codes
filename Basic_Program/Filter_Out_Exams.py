import pandas as pd

# Read the Excel file
file_name = "Exam_Schedule.xlsx"

try:
    # Load the Excel file
    df = pd.read_excel(file_name)
    
    # Display all columns to understand the structure
    print("Available columns in the file:")
    print(df.columns.tolist())
    print("\n" + "="*60 + "\n")
    
    # Assuming common column names - adjust these based on your actual file
    # Common variations: 'Subject', 'Subject Name', 'Course', etc.
    subject_col = None
    date_col = None
    time_col = None
    
    # Try to identify columns (case-insensitive)
    for col in df.columns:
        col_lower = col.lower()
        if 'subject' in col_lower or 'course' in col_lower:
            subject_col = col
        elif 'date' in col_lower:
            date_col = col
        elif 'time' in col_lower:
            time_col = col
    
    # Print the filtered information
    if subject_col and date_col and time_col:
        print("EXAM SCHEDULE")
        print("="*60)
        
        for index, row in df.iterrows():
            print(f"\nSubject: {row[subject_col]}")
            print(f"Exam Date: {row[date_col]}")
            print(f"Exam Time: {row[time_col]}")
            print("-"*60)
    else:
        # If columns not found, print all data
        print("Could not auto-detect columns. Printing all data:")
        print("\n" + df.to_string())
        
except FileNotFoundError:
    print(f"Error: The file '{file_name}' was not found.")
    print("Please make sure the file exists in the same directory as this script.")
    
except Exception as e:
    print(f"An error occurred: {str(e)}")