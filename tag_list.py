import pandas as pd
import json

#converts csv of e621 tags to json list
# Load your CSV
df = pd.read_csv('e621tags.csv', dtype=str)

# Convert the 'tags' column into a Python list
tags = df['tags'].dropna().str.strip().tolist()

# Save as JSON file
with open('tags.json', 'w', encoding='utf-8') as f:
    json.dump(tags, f, ensure_ascii=False, indent=2)

print("Saved", len(tags), "tags to tags.json")
