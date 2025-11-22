"""
FeedbackAgent - Agno AI Agent for processing user feedback and updating classifications.

This agent takes user feedback on transaction classifications and intelligently updates
the classification based on the feedback, maintaining consistency and compliance.
"""

from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from typing import Dict, Any, Optional, List
import json


class FeedbackAgent:
    """
    Agno AI Agent that processes user feedback and updates transaction classifications.
    
    This agent:
    1. Analyzes user feedback (corrections, comments)
    2. Updates category/subcategory based on feedback
    3. Adjusts confidence levels
    4. Maintains MCC code consistency
    5. Generates feedback audit trail
    """
    
    def __init__(self, llm: AzureOpenAI, tools: List):
        """
        Initialize the FeedbackAgent with Agno framework.
        
        Args:
            llm: Azure OpenAI model instance for agent intelligence
            tools: List of Agno tools (must include store_user_preference)
        """
        self.llm = llm
        self.tools = tools
        
        # Create Agno Agent with feedback processing instructions and tools
        self.agent = Agent(
            name="Feedback Processor",
            id="feedback-agent",
            model=llm,
            tools=tools,
            instructions="""
            You are a feedback processing specialist that updates transaction classifications based on user input.
            
            Your responsibilities:
            1. Analyze the user's feedback carefully
            2. Determine if the feedback requires a classification change
            3. Update category and/or subcategory as appropriate
            4. Maintain MCC code consistency with the new classification
            5. Adjust confidence levels based on user certainty
            6. Generate clear audit notes explaining the changes
            7. **IMPORTANT:** If the feedback_type is "correction" and the classification was updated, 
               you MUST call the store_user_preference tool to save the correction to the RAG system.
            
            Guidelines:
            - If user provides a specific category/subcategory, use it
            - If user feedback is vague, interpret it intelligently
            - Always maintain data consistency (category-MCC alignment)
            - Set confidence to HIGH when user provides explicit corrections
            - Set confidence to MEDIUM when interpreting user intent
            - Generate detailed audit notes for compliance
            - **When feedback_type is "correction" and updated=true, call store_user_preference tool with:**
              * merchant_name: from original_classification
              * description: from original_classification
              * user_category: the new/corrected category
              * user_subcategory: the new/corrected subcategory
              * original_category: the original category before correction
              * original_subcategory: the original subcategory before correction
              * amount: from original_classification (if available)
            
            Output format (JSON):
            {
                "updated": true/false,
                "category": "New Category",
                "subcategory": "New Subcategory",
                "confidence": "HIGH/MEDIUM/LOW",
                "mcc_code": "XXXX",
                "mcc_description": "Description",
                "feedback_applied": "Explanation of what was changed",
                "audit_notes": "Detailed notes on the feedback processing",
                "reasoning": "Why these changes were made",
                "preference_stored": true/false,  // Whether preference was saved to RAG
                "preference_id": "abc123..."  // ID of stored preference (if stored)
            }
            """,
            markdown=False,
            add_history_to_context=True
        )
    
    def execute(
        self,
        original_classification: Dict[str, Any],
        user_feedback: str,
        feedback_type: str = "correction"
    ) -> Dict[str, Any]:
        """
        Process user feedback and update the classification.
        
        Args:
            original_classification: The original classification result
            user_feedback: User's feedback text
            feedback_type: Type of feedback - "correction", "comment", "approval"
            
        Returns:
            Dictionary with updated classification and feedback processing details
        """
        # Extract transaction details for tool calls
        merchant_name = original_classification.get('merchant_name') or original_classification.get('preprocessing_data', {}).get('canonical_merchant', 'Unknown')
        description = original_classification.get('preprocessing_data', {}).get('normalized_text', '') or original_classification.get('description', '') or original_classification.get('merchant_name', 'Unknown')
        amount = original_classification.get('preprocessing_data', {}).get('amount', 0) or original_classification.get('amount', 0)
        original_category = original_classification.get('category', 'Unknown')
        original_subcategory = original_classification.get('subcategory', 'Unknown')
        
        # Build the feedback processing prompt
        prompt = f"""
        Process this user feedback for a transaction classification:
        
        ORIGINAL CLASSIFICATION:
        - Merchant Name: {merchant_name}
        - Description: {description}
        - Category: {original_category}
        - Subcategory: {original_subcategory}
        - Confidence: {original_classification.get('confidence', 'Unknown')}
        - MCC Code: {original_classification.get('mcc_code', 'Unknown')}
        - Amount: ${amount}
        
        USER FEEDBACK TYPE: {feedback_type}
        USER FEEDBACK: "{user_feedback}"
        
        Analyze the feedback and determine if changes are needed. If the user is correcting
        the classification, update it accordingly. If the user is just commenting, acknowledge
        but don't change. If approving, mark as validated.
        
        **IMPORTANT:** If feedback_type is "correction" and you update the classification (updated=true),
        you MUST call the store_user_preference tool with these parameters:
        - merchant_name: "{merchant_name}"
        - description: "{description}"
        - user_category: [the new corrected category]
        - user_subcategory: [the new corrected subcategory]
        - original_category: "{original_category}"
        - original_subcategory: "{original_subcategory}"
        - amount: {amount}
        
        This saves the correction to the RAG system so future similar transactions will use the user's preferred category.
        
        Provide your response in JSON format with all required fields, including preference_stored and preference_id if you called the tool.
        """
        
        # Run the Agno agent
        response = self.agent.run(prompt)
        
        # Extract the response content
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)
        
        # Check if tool was called (store_user_preference)
        preference_stored = False
        preference_id = None
        tool_calls_made = []
        
        if hasattr(response, 'messages'):
            for msg in response.messages:
                if hasattr(msg, 'role') and msg.role == 'tool':
                    tool_calls_made.append(msg.content if hasattr(msg, 'content') else str(msg))
                    # Check if store_user_preference was called
                    if isinstance(msg.content, dict) and msg.content.get('stored'):
                        preference_stored = True
                        preference_id = msg.content.get('preference_id')
        
        # Parse the JSON response
        try:
            # Try to extract JSON from the response
            updated_classification = self._parse_json_response(response_text)
            
            # Add metadata
            updated_classification['agent_used'] = 'FeedbackAgent (Agno)'
            updated_classification['feedback_received'] = user_feedback
            updated_classification['feedback_type'] = feedback_type
            updated_classification['original_category'] = original_category
            updated_classification['original_subcategory'] = original_subcategory
            updated_classification['preference_stored'] = preference_stored
            if preference_id:
                updated_classification['preference_id'] = preference_id
            if tool_calls_made:
                updated_classification['tool_calls'] = tool_calls_made
            
            # If no update needed, preserve original values
            if not updated_classification.get('updated', False):
                updated_classification['category'] = original_category
                updated_classification['subcategory'] = original_subcategory
                updated_classification['confidence'] = original_classification.get('confidence')
                updated_classification['mcc_code'] = original_classification.get('mcc_code')
                updated_classification['mcc_description'] = original_classification.get('mcc_description')
            
            return updated_classification
            
        except Exception as e:
            # Fallback if parsing fails
            return {
                'updated': False,
                'category': original_classification.get('category'),
                'subcategory': original_classification.get('subcategory'),
                'confidence': original_classification.get('confidence'),
                'mcc_code': original_classification.get('mcc_code'),
                'mcc_description': original_classification.get('mcc_description'),
                'feedback_applied': 'Error processing feedback',
                'audit_notes': f'Failed to process feedback: {str(e)}',
                'reasoning': 'Error occurred during feedback processing',
                'agent_used': 'FeedbackAgent (Agno)',
                'error': str(e),
                'feedback_received': user_feedback,
                'feedback_type': feedback_type
            }
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON from the agent's response.
        
        Args:
            response_text: Raw response text from the agent
            
        Returns:
            Parsed JSON dictionary
        """
        # Try to find JSON in the response
        import re
        
        # Look for JSON block
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        
        # If no JSON found, try to parse the entire response
        try:
            return json.loads(response_text)
        except:
            # Return a basic structure
            return {
                'updated': False,
                'feedback_applied': 'Could not parse response',
                'audit_notes': response_text[:500],
                'reasoning': 'Response parsing failed'
            }
