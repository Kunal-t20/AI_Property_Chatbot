# utils/query_parser.py
import re

def parse_query(query: str) -> dict:
    """
    Extract city, BHK, budget, readiness status, and locality from a natural query.
    Example input:
        "3BHK in Pune under 1.2 Cr ready to move"
    """
    query = query.lower()

    # --- Extract BHK ---
    bhk_match = re.search(r"(\d+)\s*bhk", query)
    bhk = int(bhk_match.group(1)) if bhk_match else None

    # --- Extract City ---
    cities = ["pune", "mumbai", "bangalore", "delhi", "chennai", "hyderabad"]
    city = None
    for c in cities:
        if c in query:
            city = c.title()
            break

    # --- Extract Budget (Cr or Lakh) ---
    budget = None
    cr_match = re.search(r"(\d+(\.\d+)?)\s*cr", query)
    lakh_match = re.search(r"(\d+(\.\d+)?)\s*l", query)

    if cr_match:
        budget = float(cr_match.group(1)) * 10000000  # Convert Cr → ₹
    elif lakh_match:
        budget = float(lakh_match.group(1)) * 100000  # Convert L → ₹

    # --- Extract Readiness ---
    if "ready" in query:
        readiness = "Ready to move"
    elif "under" in query and "construction" in query:
        readiness = "Under Construction"
    else:
        readiness = None

    # --- Extract Locality ---
    locality = None
    near_match = re.search(r"near\s+([a-zA-Z\s]+)", query)
    if near_match:
        locality = near_match.group(1).strip()

    return {
        "city": city,
        "bhk": bhk,
        "budget": budget,
        "readiness": readiness,
        "locality": locality,
    }
