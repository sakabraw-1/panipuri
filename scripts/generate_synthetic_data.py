import pandas as pd
import numpy as np
import os

# Paths
SEEDS_DIR = "etl/concordance/seeds"
os.makedirs(SEEDS_DIR, exist_ok=True)

def generate_concordance_weights():
    print("Generating synthetic concordance weights...")
    # Generate some dummy HS codes (6-digit)
    hs_codes = [f"{i:06d}" for i in range(101010, 101110)] # 100 products
    
    # Generate some dummy ISIC sectors
    sectors = ["A01", "B05", "C10", "C19", "C24", "C29", "D35", "F41"]
    
    data = []
    for hs in hs_codes:
        # Randomly assign 1 or 2 sectors to each HS code
        num_mappings = np.random.choice([1, 2], p=[0.7, 0.3])
        chosen_sectors = np.random.choice(sectors, num_mappings, replace=False)
        
        if num_mappings == 1:
            weights = [1.0]
        else:
            w1 = np.round(np.random.uniform(0.1, 0.9), 2)
            weights = [w1, 1.0 - w1]
            
        for s, w in zip(chosen_sectors, weights):
            data.append({"hs_code": hs, "isic_code": s, "weight": w})
            
    df = pd.DataFrame(data)
    output_path = os.path.join(SEEDS_DIR, "hs_to_isic_weights.csv")
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} rows to {output_path}")
    return hs_codes

def generate_trade_data(hs_codes):
    print("Generating synthetic trade flows...")
    countries = ["USA", "CHN", "DEU", "JPN", "IND", "GBR", "FRA", "BRA"]
    years = [2018, 2019, 2020]
    
    data = []
    for year in years:
        for _ in range(500): # 500 transactions per year
            reporter = np.random.choice(countries)
            partner = np.random.choice([c for c in countries if c != reporter])
            hs = np.random.choice(hs_codes)
            value = np.random.randint(10000, 10000000)
            
            data.append({
                "year": year,
                "reporter_iso": reporter,
                "partner_iso": partner,
                "hs_code": hs,
                "trade_value_usd": value
            })
            
    df = pd.DataFrame(data)
    output_path = os.path.join(SEEDS_DIR, "raw_trade_data.csv")
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} rows to {output_path}")

if __name__ == "__main__":
    hs_codes = generate_concordance_weights()
    generate_trade_data(hs_codes)
    print("Synthetic data generation complete.")
