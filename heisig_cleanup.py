import pandas as pd

# load original
df = pd.read_csv("KANJI_INDEX.csv")

# keep only what you want
clean = df[["kanji", "keyword_6th_ed", "components"]].copy()

# rename columns
clean.columns = ["kanji", "heisig_keyword", "heisig_components"]

# clean whitespace
clean["heisig_keyword"] = clean["heisig_keyword"].str.strip()
clean["heisig_components"] = clean["heisig_components"].fillna("").str.strip()

# save
clean.to_csv("heisig_clean.csv", index=False)