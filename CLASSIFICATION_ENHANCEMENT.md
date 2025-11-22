# Classification Agent Enhancement with RAG

## Overview
The Classification Agent has been enhanced with **RAG (Retrieval Augmented Generation)** capabilities and a new priority-based classification system that learns from user feedback and supports custom categories.

## New Priority Order

The enhanced classification follows this priority order:

1. **User Preferred Category (RAG)** - Highest Priority
   - Uses similarity search to find previous user corrections
   - If user previously corrected a similar transaction, uses their preferred category
   - Confidence: **HIGH**
   - Method: RAG-based similarity matching

2. **Custom Categories (GenAI)** - Second Priority
   - If custom categories exist, uses GenAI LLM to match transaction
   - Only uses custom categories if they are defined by the user
   - Confidence: **HIGH** (if matched)
   - Method: GenAI LLM categorization with custom taxonomy

3. **MCC Categorization** - Third Priority
   - Uses Merchant Category Code if provided
   - Falls back to vendor lookup for known brands
   - Confidence: **HIGH**
   - Method: MCC code database lookup

4. **GenAI LLM Categorization (Default)** - Fallback
   - Uses default taxonomy and AI reasoning
   - Confidence: **MEDIUM/LOW**
   - Method: Agno Agent with standard tools

## Implementation Details

### 1. User Preferences Store (RAG System)
**File:** `src/utils/user_preferences.py`

- **Storage:** JSON-based persistent storage
- **Similarity Search:** Merchant name + description matching
- **Features:**
  - Stores user corrections automatically
  - Similarity threshold: 0.6 (60% match)
  - Tracks usage count and timestamps
  - Automatic preference learning from feedback

**Key Methods:**
- `add_preference()` - Store user correction
- `find_similar_preference()` - RAG-based similarity search
- `get_all_preferences()` - Retrieve all stored preferences

### 2. Custom Categories Manager
**File:** `src/utils/custom_categories.py`

- **Storage:** JSON-based persistent storage
- **Features:**
  - Add/remove custom categories
  - Define custom subcategories
  - GenAI matching against custom taxonomy

**Key Methods:**
- `add_category()` - Add custom category with subcategories
- `remove_category()` - Delete custom category
- `get_categories()` - Get all custom categories
- `get_category_structure()` - Format for LLM prompts

### 3. Enhanced Classification Agent
**File:** `src/agents/classification_agent.py`

**New Features:**
- RAG-based user preference checking
- Custom categories support with GenAI
- Enhanced priority order implementation
- Detailed reasoning with classification method tracking

**Classification Flow:**
```
1. Check User Preferences (RAG)
   ↓ (if no match)
2. Check Custom Categories (GenAI)
   ↓ (if no match or no custom categories)
3. MCC Categorization
   ↓ (if no MCC)
4. GenAI LLM Categorization (Default)
```

**Response Format:**
```python
{
    "category": str,
    "subcategory": str,
    "confidence": "high/medium/low",
    "reasoning": str,  # Includes which method was used
    "classification_method": str,  # user_preference_rag, custom_categories_genai, mcc_categorization, genai_llm_default
    "user_preference_match": {...},  # If RAG match found
    "metadata": {
        "user_preference_checked": bool,
        "custom_categories_checked": bool,
        ...
    }
}
```

### 4. UI Integration
**File:** `src/app.py`

**New Tab: "⚙️ Settings"**
- **Custom Categories Management:**
  - View existing custom categories
  - Add new categories with subcategories
  - Delete categories
  - Form-based input

- **User Preferences View:**
  - View all stored preferences
  - See usage statistics
  - Clear all preferences

**Automatic Preference Storage:**
- When user corrects a classification, preference is automatically stored
- Future similar transactions will use the user's preferred category

## Usage Examples

### Example 1: User Preference (RAG)
```
Transaction 1: "STARBUCKS COFFEE #12345"
User corrects: Shopping / Retail (instead of Food & Dining / Restaurant)

Transaction 2: "STARBUCKS COFFEE #67890" (similar transaction)
Result: Automatically classified as Shopping / Retail (from user preference)
Method: user_preference_rag
Confidence: HIGH
```

### Example 2: Custom Categories
```
User defines custom category:
- Business Expenses
  - Office Supplies
  - Travel
  - Meals

Transaction: "OFFICE DEPOT #456"
Result: Business Expenses / Office Supplies
Method: custom_categories_genai
Confidence: HIGH
```

### Example 3: MCC Categorization
```
Transaction: "SHELL GAS STATION", MCC: "5541"
Result: Transportation / Gas Station
Method: mcc_categorization
Confidence: HIGH
```

### Example 4: Default GenAI
```
Transaction: "UNKNOWN MERCHANT XYZ"
Result: Other / General (after checking all other methods)
Method: genai_llm_default
Confidence: MEDIUM/LOW
```

## Benefits

1. **Personalization:** Learns from user corrections and applies them automatically
2. **Flexibility:** Supports custom categories for business-specific needs
3. **Accuracy:** RAG ensures similar transactions get consistent classification
4. **Transparency:** Clear reasoning shows which method was used
5. **Efficiency:** Reduces need for repeated corrections

## Technical Stack

- **RAG:** Similarity-based retrieval (can be enhanced with vector embeddings)
- **Storage:** JSON files (can be migrated to database)
- **LLM:** Azure OpenAI (gpt-5) via Agno framework
- **Similarity Algorithm:** String matching with weighted scoring

## Future Enhancements

1. **Vector Embeddings:** Replace string matching with semantic embeddings for better similarity
2. **Database Storage:** Migrate from JSON to database for scalability
3. **Multi-user Support:** Add user IDs for multi-tenant scenarios
4. **Preference Analytics:** Track which preferences are most effective
5. **Batch Preference Import:** Allow bulk import of preferences

## Files Modified/Created

**New Files:**
- `src/utils/user_preferences.py` - RAG-based preference storage
- `src/utils/custom_categories.py` - Custom categories management
- `CLASSIFICATION_ENHANCEMENT.md` - This documentation

**Modified Files:**
- `src/agents/classification_agent.py` - Enhanced with RAG and new priority order
- `src/app.py` - Added Settings tab and preference storage integration

## Testing

To test the enhancements:

1. **Test User Preferences:**
   - Process a transaction
   - Correct the classification
   - Process a similar transaction
   - Verify it uses the user's preferred category

2. **Test Custom Categories:**
   - Go to Settings tab
   - Add a custom category
   - Process a transaction that matches
   - Verify it uses the custom category

3. **Test Priority Order:**
   - Process transactions with different scenarios
   - Check the `classification_method` in results
   - Verify correct priority order is followed

