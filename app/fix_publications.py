import sqlite3
import re
import json
import os

# Connect to the database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "cv_database.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get all publications for researcher 1 (or all researchers)
cursor.execute("SELECT id, title FROM publications WHERE year IS NULL")
rows = cursor.fetchall()

# Simple keyword classification (same as in fieldClassifier.py)
field_keywords = {
    'Atmospheric Physics': ['atmospheric', 'physics', 'aerosol', 'radiation', 'cloud', 'precipitation'],
    'Climate Change': ['climate', 'change', 'global warming', 'temperature', 'co2', 'emission'],
    'Machine Learning': ['machine learning', 'deep learning', 'neural network', 'tensorflow', 'keras', 'ai', 'ml', 'algorithm'],
    'Numerical Modeling': ['wrf', 'model', 'simulation', 'forecast', 'numerical', 'prediction'],
    'Wind Energy': ['wind', 'turbine', 'energy', 'power', 'speed prediction']
}

def classify_text(text):
    lower = text.lower()
    matched = []
    for field, keywords in field_keywords.items():
        if any(kw in lower for kw in keywords):
            matched.append(field)
    return matched if matched else ['Other']

for pub_id, title in rows:
    # Extract year (4-digit number)
    year_match = re.search(r'\b(19|20)\d{2}\b', title)
    year = int(year_match.group(0)) if year_match else None
    
    # Classify fields
    fields = classify_text(title)
    fields_json = json.dumps(fields)
    
    # Update database
    cursor.execute("UPDATE publications SET year = ?, research_fields = ? WHERE id = ?", (year, fields_json, pub_id))
    print(f"Updated publication {pub_id}: year={year}, fields={fields}")

conn.commit()
conn.close()
print("✅ Database updated successfully!")