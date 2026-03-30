import re
from typing import List, Tuple

LOCATION_KEYWORDS = {"new york","los angeles","london","paris","tokyo","beijing","dubai","sydney","moscow","berlin","rome","toronto","singapore","mumbai","shanghai","chicago","houston","washington","california","texas","united states","usa","uk","europe","asia","africa","australia"}
KNOWN_ORGS = {"google","apple","microsoft","amazon","facebook","meta","twitter","netflix","tesla","nasa","who","un","fbi","cia","nba","nfl","bbc","cnn","nyt","reuters","bloomberg"}

def extract_entities(text: str) -> List[Tuple[str, str]]:
    entities, seen = [], set()
    for pattern in [r"\b(Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b"]:
        for match in re.finditer(pattern, text):
            name = match.group(0).strip()
            if name not in seen and len(name) > 3:
                entities.append((name, "PERSON")); seen.add(name)
    text_lower = text.lower()
    for loc in LOCATION_KEYWORDS:
        if loc in text_lower:
            display = loc.title()
            if display not in seen: entities.append((display, "LOCATION")); seen.add(display)
    for org in KNOWN_ORGS:
        if org in text_lower:
            display = org.upper()
            if display not in seen: entities.append((display, "ORG")); seen.add(display)
    return entities[:20]
