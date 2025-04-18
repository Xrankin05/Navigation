import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Define the scope for Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# Define output file path
streetOutputFile = "street_accessibility_scores.csv"
businessOutputFile = "business_accessibility_scores.csv"
# Load credentials from environment variable
creds_path = os.getenv("GOOGLE_CREDENTIALS")
if not creds_path or not os.path.exists(creds_path):
    raise FileNotFoundError("Please set the GOOGLE_CREDENTIALS environment variable to the path of your credentials.json file.")

creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)

# Open the Google Sheet with street accessibility data
streetSpreadsheet = client.open_by_key("1idOzW4T52Sr69Eazpn_BMcNQFvLTeBYo4Nj258uFZMU")
streetInfo = streetSpreadsheet.worksheet("Street_Accessibility_Info")
businessSpreadsheet = client.open_by_key("1-t_5-twXtjssF3e1OVUAEs8LscrXC3KiedAuUgqjFPA")
businessInfo = businessSpreadsheet.worksheet("Business_Info")

# Load data into a DataFrame
streetData = streetInfo.get_all_records()
streetDataFrame = pd.DataFrame(streetData)
businessData = businessInfo.get_all_records()
businessDataFrame = pd.DataFrame(businessData)

# Check if data is empty
if streetDataFrame.empty:
    raise ValueError("No data retrieved from the Street Sheet. Check the sheet content or access permissions.")
if businessDataFrame.empty:
    raise ValueError("No data retrieved from the Business Sheet. Check the sheet content or access permissions.")

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

# 8. Crosswalks: 2 per crosswalk capped at 30
def crosswalk_score(n):
    if pd.isna(n) or n == 0:
        return 0
    try:
        return min(int(n) * 2, 30)  
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
streetResult = streetDataFrame[['Street Name', 'score']]
print("\nWheelchair Accessibility Scores:")
print(streetResult)

# Sort by score (highest to lowest)
streetResultSorted = streetResult.sort_values(by='score', ascending=False)
print("\nSorted by Accessibility Score (Highest to Lowest):")
print(streetResultSorted)
# Save sorted results to CSV file
streetResultSorted.to_csv(streetOutputFile, index=False)
# Initialize business score column
businessDataFrame['score'] = 0

# Apply scoring rules for businesses
street_scores = dict(zip(streetResultSorted['Street Name'], streetResultSorted['score']))
for index, business in businessDataFrame.iterrows():
    # Start with street score
    street_name = business['Street Name']
    if street_name in street_scores:
        businessDataFrame.at[index, 'score'] = street_scores[street_name]
    else:
        print(f"Warning: Street '{street_name}' not found in street data for business '{business['Company Name']}'")
        businessDataFrame.at[index, 'score'] = 0

    # Bathroom accessibility: -20 if no accessible bathrooms, +10 if accessible bathrooms, +0 if not specified
    if business['Accessible Bathrooms?'] == 'TRUE':
        businessDataFrame.at[index, 'score'] += 10
    elif business['Accessible Bathrooms?'] == 'FALSE':
        businessDataFrame.at[index, 'score'] -= 20
    # No change if not specified

    # Stairs and elevators: -50 if stairs AND no elevators, +10 if elevators, -25 if stairs AND elevator not specified
    if business['Stairs?']:
        if business['Elevators?'] == 'FALSE':
            businessDataFrame.at[index, 'score'] -= 50
        elif business['Elevators?'] == 'TRUE':
            businessDataFrame.at[index, 'score'] += 10
        else:  # Elevator not specified
            businessDataFrame.at[index, 'score'] -= 25

    # Surface: -10 if not flat
    if business['Surface Type'] != 'Flat':
        businessDataFrame.at[index, 'score'] -= 10

    # Push door button: -20 if none, -10 if not specified, +5 if present
    if business['Push door button'] == 'FALSE':
        businessDataFrame.at[index, 'score'] -= 20
    elif business['Push door button'] == 'TRUE':
        businessDataFrame.at[index, 'score'] += 5
    else:  # Not specified
        businessDataFrame.at[index, 'score'] -= 10

    # Ramps: -10 if no ramps
    if business['Ramps?'] == False:
        businessDataFrame.at[index, 'score'] -= 10

    # Ratings: Add the value
    try:
        rating = float(business['Ratings (1-5)'])
        businessDataFrame.at[index, 'score'] += rating
    except (ValueError, TypeError):
        pass  # Skip if rating can't be converted to float

    # Maintenance: Add the value
    try:
        maintenance = float(business['Maintenance (1-5)'])
        businessDataFrame.at[index, 'score'] += maintenance
    except (ValueError, TypeError):
        pass  # Skip if maintenance can't be converted to float

    # Positive Comments: +5 few, +10 several, +15 many
    pos_comment = str(business['Pos Comment #']).upper()
    if pos_comment == 'FEW':
        businessDataFrame.at[index, 'score'] += 5
    elif pos_comment == 'SEVERAL':
        businessDataFrame.at[index, 'score'] += 10
    elif pos_comment in ['MANY', 'PLENTY']:
        businessDataFrame.at[index, 'score'] += 15

    # Negative Comments: -5 few, -10 several, -15 many
    neg_comment = str(business['Neg Comment #']).upper()
    if neg_comment == 'FEW':
        businessDataFrame.at[index, 'score'] -= 5
    elif neg_comment == 'SEVERAL':
        businessDataFrame.at[index, 'score'] -= 10
    elif neg_comment in ['MANY', 'PLENTY']:
        businessDataFrame.at[index, 'score'] -= 15

# Select and display results
businessResult = businessDataFrame[['Company Name', 'Street Name','Address', 'score']]
print("\nWheelchair Accessibility Scores for Businesses:")
print(businessResult)

# Sort by score (highest to lowest)
businessDataFrame = businessDataFrame[['Company Name', 'Street Name', 'Address', 'score']]
businessResultSorted = businessResult.sort_values(by='score', ascending=False)
print("\nBusinesses Sorted by Accessibility Score (Highest to Lowest):")
print(businessResultSorted)

# Save sorted results to CSV file
businessResultSorted.to_csv(businessOutputFile, index=False)