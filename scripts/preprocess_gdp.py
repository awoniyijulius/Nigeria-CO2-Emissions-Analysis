import zipfile
import pandas as pd
import os

# Path to the ZIP file
zip_path = "data/API_NY.GDP.PCAP.PP.CD_DS2_en_csv_v2_216039.zip"
extract_path = "data/gdp_raw"

# --- Extract ZIP ---
with zipfile.ZipFile(zip_path, "r") as z:
    z.extractall(extract_path)

# --- Find the main CSV file inside ---
csv_file = [f for f in os.listdir(extract_path) if f.startswith("API_NY.GDP.PCAP.PP.CD") and f.endswith(".csv")][0]
csv_path = os.path.join(extract_path, csv_file)

# --- Load GDP data (skip metadata rows) ---
df = pd.read_csv(csv_path, skiprows=4)

# --- Keep Nigeria + peers + World ---
countries = ["Nigeria", "South Africa", "Ghana", "Kenya", "World"]
df = df[df["Country Name"].isin(countries)]

# --- Melt into tidy format ---
df_tidy = df.melt(
    id_vars=["Country Name", "Country Code"],
    var_name="year",
    value_name="gdp_per_capita"
)

# --- Convert year to int ---
df_tidy["year"] = pd.to_numeric(df_tidy["year"], errors="coerce")
df_tidy = df_tidy.dropna(subset=["year", "gdp_per_capita"])

# --- Save cleaned dataset ---
df_tidy.to_csv("worldbank_gdp.csv", index=False)

print("✅ Preprocessed GDP data saved as worldbank_gdp.csv")
