import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Define the scope for Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# Define output file path
output_file = "accessibility_scores.csv"

# Load credentials from environment variable
creds_path = os.getenv("GOOGLE_CREDENTIALS")
if not creds_path or not os.path.exists(creds_path):
    raise FileNotFoundError("Please set the GOOGLE_CREDENTIALS environment variable to the path of your credentials.json file.")

creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)

# Open the Google Sheet with street accessibility data
spreadsheet = client.open_by_key("1idOzW4T52Sr69Eazpn_BMcNQFvLTeBYo4Nj258uFZMU")
streetInfo = spreadsheet.worksheet("Street_Accessibility_Info")

# Load data into a DataFrame
streetData = streetInfo.get_all_records()
streetDataFrame = pd.DataFrame(streetData)

# Check if data is empty
if streetDataFrame.empty:
    raise ValueError("No data retrieved from the Google Sheet. Check the sheet content or access permissions.")

# Filter out rows with empty or missing 'Street Name'
streetDataFrame = streetDataFrame[streetDataFrame['Street Name'].notna() & (streetDataFrame['Street Name'] != '')]

# Print raw data for inspection
print("Raw Data from Google Sheet:")
print(streetDataFrame)

# Define expected columns
expected_cols = ["Street Name", "Sidewalk?", "Traffic Volume", "Ramps?", "Public Restrooms?", 
                 "Bumpiness (1-10)", "Sidewalk Width (FT)", "Incline", "Crosswalks?", 
                 "Ratings (1-5)", "Maintenence (1-5)", "Pos Comment #", "Neg Comment #"]

# Check for missing columns
missing_cols = [col for col in expected_cols if col not in streetDataFrame.columns]
if missing_cols:
    print(f"Warning: Missing columns in data: {missing_cols}")

# Define numerical and categorical columns
numerical_cols = ["Sidewalk?", "Public Restrooms?", "Bumpiness (1-10)", "Sidewalk Width (FT)", 
                  "Crosswalks?", "Ratings (1-5)", "Maintenence (1-5)"]
categorical_cols = ["Traffic Volume", "Incline", "Pos Comment #", "Neg Comment #"]

# Convert numerical columns to float with robust handling
for col in numerical_cols:
    if col in streetDataFrame.columns:
        streetDataFrame[col] = pd.to_numeric(streetDataFrame[col], errors='coerce')
        default_value = 0 if col in ["Public Restrooms?", "Crosswalks?"] else 1 if col == "Sidewalk?" else 3
        streetDataFrame[col] = streetDataFrame[col].fillna(default_value)
    else:
        streetDataFrame[col] = default_value
        print(f"Warning: {col} not found, defaulting to {default_value}")

# Convert 'Ramps?' to 1/0 with flexible parsing
if 'Ramps?' in streetDataFrame.columns:
    streetDataFrame['Ramps?'] = streetDataFrame['Ramps?'].apply(
        lambda x: 1 if str(x).strip().upper() in ['TRUE', '1', 'YES'] else 0
    )
else:
    streetDataFrame['Ramps?'] = 1  # Default to present if missing
    print("Warning: 'Ramps?' not found, defaulting to 1")

# Handle categorical columns with case-insensitive mapping
for col in categorical_cols:
    if col in streetDataFrame.columns:
        streetDataFrame[col] = streetDataFrame[col].str.upper().fillna('MODERATE' if col in ["Traffic Volume", "Incline"] else 'FEW')
    else:
        streetDataFrame[col] = 'MODERATE' if col in ["Traffic Volume", "Incline"] else 'FEW'
        print(f"Warning: {col} not found, defaulting to {'MODERATE' if col in ['Traffic Volume', 'Incline'] else 'FEW'}")

# Print processed data
print("\nProcessed DataFrame:")
print(streetDataFrame)

# Initialize score column
streetDataFrame['score'] = 0

# Scoring Rules
# 1. Add 50 if there is a sidewalk
streetDataFrame['score'] += streetDataFrame['Sidewalk?'] * 50

# 2. Traffic Volume: +10 low, 0 moderate, -10 high
traffic_map = {'LOW': 10, 'MODERATE': 0, 'HIGH': -10}
streetDataFrame['score'] += streetDataFrame['Traffic Volume'].map(traffic_map).fillna(0)

# 3. Ramps: +10 if present, -10 if not
streetDataFrame['score'] += (streetDataFrame['Ramps?'] * 20) - 10

# 4. Public Restrooms: +10 if present, -10 if not
streetDataFrame['score'] += ((streetDataFrame['Public Restrooms?'] > 0).astype(int) * 20) - 10

# 5. Bumpiness: Subtract the value
streetDataFrame['score'] -= streetDataFrame['Bumpiness (1-10)'].fillna(0)

# 6. Sidewalk Width: width/10 if >8, -100 otherwise
streetDataFrame['score'] += streetDataFrame['Sidewalk Width (FT)'].apply(lambda x: x / 10 if x > 8 else -100)

# 7. Incline: +10 low, 0 moderate, -10 high
incline_map = {'LOW': 10, 'MODERATE': 0, 'HIGH': -10}
streetDataFrame['score'] += streetDataFrame['Incline'].map(incline_map).fillna(0)

# 8. Crosswalks: +5 per digit
def crosswalk_score(n):
    if pd.isna(n) or n == 0:
        return 0
    try:
        return 5 * len(str(int(n)))
    except (ValueError, TypeError):
        return 0
streetDataFrame['score'] += streetDataFrame['Crosswalks?'].apply(crosswalk_score)

# 9. Ratings: Add the value
streetDataFrame['score'] += streetDataFrame['Ratings (1-5)'].fillna(0)

# 10. Maintenance: Add the value
streetDataFrame['score'] += streetDataFrame['Maintenence (1-5)'].fillna(0)

# 11. Positive Comments: +5 few, +10 several, +15 many
pos_comment_map = {'FEW': 5, 'SEVERAL': 10, 'MANY': 15}
streetDataFrame['score'] += streetDataFrame['Pos Comment #'].map(pos_comment_map).fillna(5)

# 12. Negative Comments: -5 few, -10 several, -15 many
neg_comment_map = {'FEW': -5, 'SEVERAL': -10, 'MANY': -15}
streetDataFrame['score'] += streetDataFrame['Neg Comment #'].map(neg_comment_map).fillna(-5)

# Select and display results
result = streetDataFrame[['Street Name', 'score']]
print("\nWheelchair Accessibility Scores:")
print(result)

# Sort by score (highest to lowest)
result_sorted = result.sort_values(by='score', ascending=False)
print("\nSorted by Accessibility Score (Highest to Lowest):")
print(result_sorted)
# Save sorted results to CSV file (without index numbers)
result_sorted.to_csv(output_file, index=False)
