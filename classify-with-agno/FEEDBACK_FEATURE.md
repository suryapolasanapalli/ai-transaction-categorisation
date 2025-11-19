# Feedback Feature Documentation

## Overview
The Feedback Feature allows users to provide feedback on transaction classifications and have the AI update the classification based on their input.

## Components

### 1. FeedbackAgent (agents/feedback_agent.py)
**Agno AI Agent** that processes user feedback and intelligently updates classifications.

**Key Features:**
- Analyzes user feedback (corrections, comments, approvals)
- Updates category/subcategory based on feedback
- Adjusts confidence levels appropriately
- Maintains MCC code consistency
- Generates detailed audit trails

**Agent Configuration:**
```python
Agent(
    name="Feedback Processor",
    id="feedback-agent",
    model=AzureOpenAI(id="gpt-5"),
    tools=[],  # Pure reasoning, no tools needed
    instructions="""Process user feedback and update classifications intelligently"""
)
```

### 2. Feedback UI (app.py)
Located after the classification results in Tab 1 (Single Entry).

**Three Feedback Types:**

#### ✅ Approve Classification
- Quick "Looks Good!" button
- Records user approval
- No changes to classification
- Generates approval audit trail

#### ✏️ Correct Classification
- User provides correct category/subcategory
- Optional additional comments
- AI processes and applies correction
- Updates confidence to HIGH (user-corrected)
- Maintains MCC code alignment

#### 💬 Add Comment
- User shares thoughts/observations
- No classification changes
- Feedback recorded for future improvements
- Generates comment audit trail

## User Flow

### Step 1: Process Transaction
User enters transaction details → System classifies → Shows results

### Step 2: Review Results
User reviews the classification in the detailed view

### Step 3: Provide Feedback
Choose one of three options:
- **Approve:** Click "👍 Looks Good!" or "✅ Approve This Classification"
- **Correct:** Select "✏️ Correct Classification", enter correct category/subcategory
- **Comment:** Select "💬 Add Comment", enter thoughts

### Step 4: AI Processing
FeedbackAgent analyzes the feedback using Azure OpenAI:
- Interprets user intent
- Determines necessary changes
- Updates classification intelligently
- Generates audit trail

### Step 5: View Updated Result
System shows:
- **Before/After comparison** (if updated)
- **AI reasoning** for the changes
- **Audit notes** for compliance
- **Full JSON response** with all details

### Step 6: Reset (Optional)
Click "🔄 Clear Feedback and Try Again" to provide different feedback

## Technical Implementation

### FeedbackAgent.execute()
```python
def execute(
    original_classification: Dict[str, Any],
    user_feedback: str,
    feedback_type: str = "correction"
) -> Dict[str, Any]:
    """
    Process user feedback and update classification
    
    Returns:
        {
            'updated': bool,
            'category': str,
            'subcategory': str,
            'confidence': str,
            'mcc_code': str,
            'feedback_applied': str,
            'audit_notes': str,
            'reasoning': str,
            'agent_used': 'FeedbackAgent (Agno)'
        }
    """
```

### Session State Management
```python
st.session_state.feedback_submitted = False  # Track if feedback was submitted
st.session_state.updated_result = None       # Store updated classification
st.session_state.quick_feedback = None       # Track quick action buttons
```

## Output Format

### Approval Output
```json
{
    "updated": false,
    "feedback_applied": "User approved classification as correct",
    "audit_notes": "Classification validated by user on [timestamp]",
    "reasoning": "User confirmed the classification is accurate",
    "agent_used": "FeedbackAgent (Agno)"
}
```

### Correction Output
```json
{
    "updated": true,
    "category": "Food & Dining",
    "subcategory": "Restaurant",
    "confidence": "HIGH",
    "mcc_code": "5812",
    "mcc_description": "Eating Places, Restaurants",
    "feedback_applied": "Updated category from 'Shopping' to 'Food & Dining'",
    "audit_notes": "User correction applied: [details]",
    "reasoning": "User provided explicit correction to category",
    "original_category": "Shopping",
    "original_subcategory": "Retail",
    "agent_used": "FeedbackAgent (Agno)"
}
```

### Comment Output
```json
{
    "updated": false,
    "feedback_applied": "Comment recorded for future improvements",
    "audit_notes": "User comment: [feedback text]",
    "reasoning": "User provided feedback without requesting changes",
    "agent_used": "FeedbackAgent (Agno)"
}
```

## Benefits

### For Users
✅ **Control:** Correct misclassifications immediately
✅ **Transparency:** See exactly how AI interprets feedback
✅ **Flexibility:** Multiple feedback types for different needs
✅ **Quick Actions:** One-click approval or correction initiation

### For System
✅ **Learning:** Collect user corrections for model improvement
✅ **Audit Trail:** Complete record of all feedback and changes
✅ **Consistency:** AI ensures MCC codes align with updated categories
✅ **Compliance:** Detailed audit notes for regulatory requirements

### For AI
✅ **Intelligent:** Uses LLM to interpret ambiguous feedback
✅ **Context-Aware:** Maintains data consistency across fields
✅ **Adaptive:** Adjusts confidence based on feedback certainty
✅ **Explainable:** Provides reasoning for all changes

## Examples

### Example 1: Approve Classification
**Input:**
- Original: "Food & Dining / Restaurant" (95% confidence)
- User Action: Click "👍 Looks Good!"

**Output:**
- No changes to classification
- Audit note: "User approved classification as correct"
- Feedback recorded for quality metrics

### Example 2: Correct Category
**Input:**
- Original: "Shopping / Retail" (85% confidence)
- User Action: Correct to "Food & Dining / Restaurant"
- User Comment: "This is a restaurant, not retail"

**Output:**
- Updated: "Food & Dining / Restaurant" (HIGH confidence)
- MCC Code: 5812 (aligned with new category)
- Reasoning: "User provided explicit correction with context"
- Audit: Complete before/after trail

### Example 3: Add Comment
**Input:**
- Original: "Entertainment / Streaming" (90% confidence)
- User Action: Comment "Should track these separately from cable TV"

**Output:**
- No changes to classification
- Comment recorded: "User suggested separate tracking"
- Feedback available for future system improvements

## Integration with Existing Pipeline

The FeedbackAgent integrates seamlessly with the existing 3-agent pipeline:

```
PreprocessingAgent → ClassificationAgent → GovernanceAgent
                                                ↓
                                         [User Reviews]
                                                ↓
                                          FeedbackAgent
                                                ↓
                                    [Updated Classification]
```

## Future Enhancements

1. **Batch Feedback:** Allow feedback on CSV batch results
2. **Learning Loop:** Use feedback to fine-tune classification rules
3. **Feedback Analytics:** Dashboard showing common corrections
4. **Auto-Learning:** System automatically applies patterns from feedback
5. **Confidence Boost:** Frequently approved classifications get confidence boost
6. **Export Feedback:** Download feedback history for analysis

## Testing

To test the feature:

1. Run the app: `streamlit run app.py`
2. Go to "Single Entry" tab
3. Enter a transaction (e.g., "Starbucks Coffee", $5.50)
4. Wait for classification
5. Scroll down to "Provide Feedback" section
6. Try each feedback type:
   - Click "👍 Looks Good!" for approval
   - Select "Correct Classification" and change category
   - Select "Add Comment" and enter feedback
7. Observe the AI processing and updated results

## Troubleshooting

**Issue:** Feedback not applying
- Check Azure OpenAI credentials in .env
- Verify FeedbackAgent is initialized
- Check browser console for errors

**Issue:** UI not showing
- Clear Streamlit cache: Click "C" in the app
- Refresh the page
- Check session state is initialized

**Issue:** JSON parsing errors
- FeedbackAgent has fallback handling
- Check agent response format
- Verify LLM is returning valid JSON
