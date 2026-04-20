# Hierarchical classification: main fields + subfields
hierarchy = {
    "Astronomy": {
        "keywords": ["astronomy", "galaxy", "star", "planet", "exoplanet", "cosmology", "nebula", "supernova", "black hole", "telescope", "observatory", "celestial", "stellar", "solar system", "universe", "dark matter", "dark energy"],
        "subfields": ["Stellar Astronomy", "Galactic Astronomy", "Extragalactic Astronomy", "Cosmology", "Planetary Science", "Exoplanets", "Astrobiology", "Instrumentation"]
    },
    "Space Science": {
        "keywords": ["space", "satellite", "rocket", "orbital", "spacecraft", "space weather", "ionosphere", "magnetosphere", "space debris", "space exploration", "launch vehicle", "space mission", "space station", "astronaut", "microgravity", "space physics"],
        "subfields": ["Space Physics", "Space Weather", "Satellite Technology", "Space Debris", "Space Exploration", "Astrodynamics", "Space Instrumentation"]
    },
    "Meteorology": {
        "keywords": ["meteorology", "weather", "climate", "atmospheric", "precipitation", "wind", "temperature", "humidity", "cyclone", "hurricane", "typhoon", "storm", "rainfall", "drought", "forecast", "WRF", "atmospheric physics", "climate change", "global warming", "aerosol", "cloud", "radar", "lidar", "numerical weather prediction", "NWP"],
        "subfields": ["Physical Meteorology", "Dynamic Meteorology", "Synoptic Meteorology", "Climatology", "Climate Change", "Atmospheric Physics", "Atmospheric Chemistry", "Weather Forecasting", "Remote Sensing", "Hydrometeorology"]
    }
}

def classify_to_main_field(text):
    """Return main field (Astronomy, Space Science, Meteorology) and subfield."""
    text_lower = text.lower()
    for main_field, data in hierarchy.items():
        for kw in data["keywords"]:
            if kw in text_lower:
                # Determine subfield: try to match a specific subfield keyword
                subfield = "General " + main_field
                for sf in data["subfields"]:
                    if sf.lower() in text_lower:
                        subfield = sf
                        break
                return main_field, subfield
    return "Other", "Other"

def classify_publications(publications):
    """Add main_field and subfield to each publication dict."""
    enriched = []
    for pub in publications:
        main_field, subfield = classify_to_main_field(pub.get("title", "") + " " + pub.get("journal", ""))
        pub["main_field"] = main_field
        pub["subfield"] = subfield
        enriched.append(pub)
    return enriched

# Keep original classify_text if needed for backward compatibility
def classify_text(text):
    main_field, _ = classify_to_main_field(text)
    return [main_field]