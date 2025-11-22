"""User Preferences Storage with RAG - Stores and retrieves user classification preferences"""
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib


class UserPreferencesStore:
    """
    RAG-based storage for user classification preferences.
    Stores user corrections and uses similarity search to retrieve relevant preferences.
    """
    
    def __init__(self, storage_path: str = "user_preferences.json"):
        """
        Initialize the user preferences store.
        
        Args:
            storage_path: Path to JSON file for persistent storage
        """
        self.storage_path = storage_path
        self.preferences: List[Dict[str, Any]] = []
        self._load_preferences()
    
    def _load_preferences(self):
        """Load preferences from storage file"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    self.preferences = json.load(f)
            except Exception as e:
                print(f"Error loading preferences: {e}")
                self.preferences = []
        else:
            self.preferences = []
    
    def _save_preferences(self):
        """Save preferences to storage file"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def _create_preference_key(self, merchant_name: str, description: str) -> str:
        """
        Create a unique key for a transaction based on merchant and description.
        Uses normalized merchant name for matching.
        """
        # Normalize merchant name (uppercase, remove special chars)
        normalized_merchant = merchant_name.upper().strip()
        normalized_desc = description.upper().strip()[:50]  # First 50 chars
        
        # Create hash for consistent key
        key_string = f"{normalized_merchant}:{normalized_desc}"
        return hashlib.md5(key_string.encode()).hexdigest()[:16]
    
    def _calculate_similarity(self, merchant1: str, desc1: str, merchant2: str, desc2: str) -> float:
        """
        Calculate similarity score between two transactions.
        Simple string matching - can be enhanced with embeddings later.
        
        Returns:
            Similarity score between 0.0 and 1.0
        """
        merchant1_norm = merchant1.upper().strip()
        merchant2_norm = merchant2.upper().strip()
        desc1_norm = desc1.upper().strip()
        desc2_norm = desc2.upper().strip()
        
        # Merchant name similarity (weight: 0.7)
        merchant_match = 1.0 if merchant1_norm == merchant2_norm else 0.0
        if merchant1_norm in merchant2_norm or merchant2_norm in merchant1_norm:
            merchant_match = 0.8
        
        # Description similarity (weight: 0.3)
        desc_words1 = set(desc1_norm.split())
        desc_words2 = set(desc2_norm.split())
        if desc_words1 and desc_words2:
            desc_similarity = len(desc_words1.intersection(desc_words2)) / len(desc_words1.union(desc_words2))
        else:
            desc_similarity = 0.0
        
        # Weighted similarity
        similarity = (merchant_match * 0.7) + (desc_similarity * 0.3)
        return similarity
    
    def add_preference(
        self,
        merchant_name: str,
        description: str,
        user_category: str,
        user_subcategory: str,
        original_category: Optional[str] = None,
        original_subcategory: Optional[str] = None,
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Add a user preference (correction) to the store.
        
        Args:
            merchant_name: Merchant name
            description: Transaction description
            user_category: User's preferred category
            user_subcategory: User's preferred subcategory
            original_category: Original category (for tracking)
            original_subcategory: Original subcategory (for tracking)
            amount: Transaction amount
            
        Returns:
            The stored preference dictionary
        """
        preference = {
            "id": self._create_preference_key(merchant_name, description),
            "merchant_name": merchant_name.upper().strip(),
            "description": description,
            "user_category": user_category,
            "user_subcategory": user_subcategory,
            "original_category": original_category,
            "original_subcategory": original_subcategory,
            "amount": amount,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        # Check if preference already exists
        existing_idx = None
        for idx, pref in enumerate(self.preferences):
            if pref["id"] == preference["id"]:
                existing_idx = idx
                break
        
        if existing_idx is not None:
            # Update existing preference
            self.preferences[existing_idx].update(preference)
            self.preferences[existing_idx]["updated_at"] = datetime.now().isoformat()
        else:
            # Add new preference
            self.preferences.append(preference)
        
        self._save_preferences()
        return preference
    
    def find_similar_preference(
        self,
        merchant_name: str,
        description: str,
        similarity_threshold: float = 0.6
    ) -> Optional[Dict[str, Any]]:
        """
        Find a similar user preference using RAG-like similarity search.
        
        Args:
            merchant_name: Merchant name to search for
            description: Transaction description
            similarity_threshold: Minimum similarity score (0.0-1.0)
            
        Returns:
            Most similar preference if found, None otherwise
        """
        if not self.preferences:
            return None
        
        best_match = None
        best_score = 0.0
        
        for preference in self.preferences:
            similarity = self._calculate_similarity(
                merchant_name,
                description,
                preference["merchant_name"],
                preference.get("description", "")
            )
            
            if similarity > best_score and similarity >= similarity_threshold:
                best_score = similarity
                best_match = preference
        
        if best_match:
            # Increment usage count
            best_match["usage_count"] = best_match.get("usage_count", 0) + 1
            best_match["last_used_at"] = datetime.now().isoformat()
            self._save_preferences()
            
            return {
                **best_match,
                "similarity_score": best_score
            }
        
        return None
    
    def get_all_preferences(self) -> List[Dict[str, Any]]:
        """Get all stored preferences"""
        return self.preferences
    
    def clear_preferences(self):
        """Clear all preferences"""
        self.preferences = []
        self._save_preferences()


# Global instance
_preferences_store: Optional[UserPreferencesStore] = None


def get_preferences_store() -> UserPreferencesStore:
    """Get or create the global preferences store instance"""
    global _preferences_store
    if _preferences_store is None:
        _preferences_store = UserPreferencesStore()
    return _preferences_store

