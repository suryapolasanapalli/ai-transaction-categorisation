"""User Preferences Tool - RAG-based preference lookup for Agno agents"""
from typing import Dict, Any, Optional
from agno.tools import tool
import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.user_preferences import get_preferences_store


@tool
def lookup_user_preference(merchant_name: str, description: str, similarity_threshold: float = 0.6) -> Dict[str, Any]:
    """
    Look up user preference for a transaction using RAG-based similarity search.
    
    Use this tool FIRST when classifying a transaction. If the user has previously
    corrected a similar transaction, this will return their preferred category with
    HIGH confidence. This is the highest priority classification method.
    
    The tool uses similarity matching based on:
    - Merchant name (70% weight) - exact or partial match
    - Description word overlap (30% weight) - Jaccard similarity
    
    Args:
        merchant_name: Merchant name from the transaction (e.g., "STARBUCKS")
        description: Transaction description (e.g., "Starbucks Coffee Shop")
        similarity_threshold: Minimum similarity score (0.0-1.0). Default: 0.6 (60%)
        
    Returns:
        Dict with preference match information:
        - If match found:
          {
              "match": True,
              "category": "User's preferred category",
              "subcategory": "User's preferred subcategory",
              "similarity_score": 0.85,
              "preference_id": "abc123...",
              "original_category": "Original category before correction",
              "original_subcategory": "Original subcategory before correction",
              "confidence": "HIGH",
              "message": "Found user preference via RAG (similarity: 85%)"
          }
        - If no match:
          {
              "match": False,
              "message": "No user preference found for this transaction",
              "confidence": "NONE"
          }
    """
    preferences_store = get_preferences_store()
    
    user_preference = preferences_store.find_similar_preference(
        merchant_name=merchant_name,
        description=description,
        similarity_threshold=similarity_threshold
    )
    
    if user_preference:
        return {
            "match": True,
            "category": user_preference.get("user_category"),
            "subcategory": user_preference.get("user_subcategory"),
            "similarity_score": user_preference.get("similarity_score", 0.0),
            "preference_id": user_preference.get("id"),
            "original_category": user_preference.get("original_category"),
            "original_subcategory": user_preference.get("original_subcategory"),
            "confidence": "HIGH",
            "message": f"Found user preference via RAG (similarity: {user_preference.get('similarity_score', 0):.0%}). User previously corrected from '{user_preference.get('original_category', 'N/A')}' to '{user_preference.get('user_category')}' / '{user_preference.get('user_subcategory')}'."
        }
    else:
        return {
            "match": False,
            "message": "No user preference found for this transaction. Proceed with other classification methods.",
            "confidence": "NONE"
        }

