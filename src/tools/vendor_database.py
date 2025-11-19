"""Vendor Database Tool - Search for known merchants"""
from typing import Dict, Optional
from agno.tools import tool


# Known merchant database
VENDOR_DATABASE = {
    "UBER": {"category": "Transportation", "subcategory": "Rideshare"},
    "LYFT": {"category": "Transportation", "subcategory": "Rideshare"},
    "SHELL": {"category": "Transportation", "subcategory": "Gas Station"},
    "EXXON": {"category": "Transportation", "subcategory": "Gas Station"},
    "CHEVRON": {"category": "Transportation", "subcategory": "Gas Station"},
    "STARBUCKS": {"category": "Food & Dining", "subcategory": "Coffee Shop"},
    "MCDONALDS": {"category": "Food & Dining", "subcategory": "Fast Food"},
    "CHIPOTLE": {"category": "Food & Dining", "subcategory": "Restaurant"},
    "WALMART": {"category": "Shopping", "subcategory": "Retail"},
    "TARGET": {"category": "Shopping", "subcategory": "Retail"},
    "AMAZON": {"category": "Shopping", "subcategory": "Online"},
    "COSTCO": {"category": "Shopping", "subcategory": "Warehouse"},
    "NETFLIX": {"category": "Entertainment", "subcategory": "Streaming"},
    "SPOTIFY": {"category": "Entertainment", "subcategory": "Music"},
    "HULU": {"category": "Entertainment", "subcategory": "Streaming"},
    "CVS": {"category": "Healthcare", "subcategory": "Pharmacy"},
    "WALGREENS": {"category": "Healthcare", "subcategory": "Pharmacy"},
    "AT&T": {"category": "Utilities", "subcategory": "Telecom"},
    "VERIZON": {"category": "Utilities", "subcategory": "Telecom"},
    "COMCAST": {"category": "Utilities", "subcategory": "Internet"}
}


@tool
def vendor_database_search(query: str) -> Dict[str, any]:
    """
    Search the vendor database for a matching merchant.
    
    Use this tool to check if a merchant is in our known vendor database.
    The database contains common merchants with pre-assigned categories.
    
    Args:
        query: Transaction description or merchant name to search (e.g., "STARBUCKS", "Uber trip")
        
    Returns:
        Dict with vendor name, category, subcategory, and match status
    """
    query_upper = query.upper()
    
    for vendor, info in VENDOR_DATABASE.items():
        if vendor in query_upper:
            return {
                "vendor": vendor,
                "category": info["category"],
                "subcategory": info["subcategory"],
                "match": True,
                "confidence_boost": "HIGH - Found in verified vendor database"
            }
    
    return {
        "vendor": None,
        "category": None,
        "subcategory": None,
        "match": False,
        "message": "Merchant not found in database. Use taxonomy to classify manually."
    }
