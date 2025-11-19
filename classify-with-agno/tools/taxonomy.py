"""Taxonomy Tool - Provides valid transaction categories"""
from typing import List, Dict
from agno.tools import tool


# Valid transaction taxonomy
TRANSACTION_CATEGORIES = {
    "Food & Dining": [
        "Restaurant",
        "Fast Food",
        "Coffee Shop",
        "Grocery",
        "Bar/Club"
    ],
    "Transportation": [
        "Gas Station",
        "Rideshare",
        "Public Transit",
        "Parking",
        "Auto Service"
    ],
    "Shopping": [
        "Retail",
        "Online",
        "Warehouse",
        "Clothing",
        "Electronics"
    ],
    "Utilities": [
        "Electric",
        "Gas",
        "Water",
        "Internet",
        "Telecom"
    ],
    "Healthcare": [
        "Pharmacy",
        "Doctor",
        "Dentist",
        "Hospital",
        "Insurance"
    ],
    "Entertainment": [
        "Streaming",
        "Music",
        "Movies",
        "Events",
        "Gaming"
    ],
    "Travel": [
        "Hotel",
        "Airline",
        "Car Rental",
        "Vacation"
    ],
    "Financial Services": [
        "Bank Fee",
        "ATM",
        "Investment",
        "Insurance"
    ],
    "Personal Care": [
        "Salon",
        "Spa",
        "Gym",
        "Beauty"
    ],
    "Education": [
        "Tuition",
        "Books",
        "Supplies",
        "Online Course"
    ],
    "Home & Garden": [
        "Hardware",
        "Furniture",
        "Garden",
        "Home Improvement"
    ],
    "Other": [
        "General",
        "Miscellaneous"
    ]
}


@tool
def get_taxonomy_structure() -> Dict[str, List[str]]:
    """
    Get the complete transaction taxonomy structure.
    
    Use this tool to see all valid categories and their subcategories
    when you need to classify a transaction that's not in the vendor database.
    
    Returns:
        Dict mapping category names to lists of subcategories
    """
    return TRANSACTION_CATEGORIES


def get_valid_categories() -> List[str]:
    """
    Get list of all valid transaction categories
    
    Returns:
        List of category names
    """
    return list(TRANSACTION_CATEGORIES.keys())


def get_subcategories(category: str) -> List[str]:
    """
    Get subcategories for a specific category
    
    Args:
        category: Category name
        
    Returns:
        List of subcategories for the category
    """
    return TRANSACTION_CATEGORIES.get(category, [])


def get_taxonomy_as_text() -> str:
    """
    Get taxonomy as formatted text for LLM prompts
    
    Returns:
        Formatted string with categories and subcategories
    """
    result = "Valid Transaction Categories:\n\n"
    for category, subcategories in TRANSACTION_CATEGORIES.items():
        result += f"- {category}\n"
        for subcat in subcategories:
            result += f"  • {subcat}\n"
    return result
