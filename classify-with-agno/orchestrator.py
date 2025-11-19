"""Orchestrator - Coordinates workflow between Agno agents"""
from typing import Dict, Any, Optional


class TransactionOrchestrator:
    """
    Orchestrates the transaction processing workflow using Agno agents:
    1. PreprocessingAgent: Extract and clean transaction data
    2. ClassificationAgent: Categorize the transaction
    3. GovernanceAgent: Validate and audit the classification
    """
    
    def __init__(self,
                 preprocessing_agent,
                 classification_agent,
                 governance_agent):
        """
        Initialize the orchestrator with Agno agents
        
        Args:
            preprocessing_agent: PreprocessingAgent instance
            classification_agent: ClassificationAgent instance
            governance_agent: GovernanceAgent instance
        """
        self.preprocessing_agent = preprocessing_agent
        self.classification_agent = classification_agent
        self.governance_agent = governance_agent
        self.workflow_log = []
    
    def process_transaction(self,
                          description: str,
                          amount: float,
                          merchant_name: Optional[str] = None,
                          mcc_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a transaction through the complete workflow
        
        Args:
            description: Raw transaction description
            amount: Transaction amount
            merchant_name: Optional pre-provided merchant name
            mcc_code: Optional pre-provided MCC code
            
        Returns:
            Complete processed transaction data with all agent results
        """
        self.workflow_log = []
        
        try:
            # Step 1: Preprocessing
            self._log_step("PreprocessingAgent", "Starting preprocessing...")
            preprocessing_result = self.preprocessing_agent.execute(
                description=description,
                amount=amount,
                merchant_name=merchant_name
            )
            self._log_step("PreprocessingAgent", f"Completed - Merchant: {preprocessing_result['merchant_name']}")
            
            # Step 2: Classification
            self._log_step("ClassificationAgent", "Starting classification...")
            classification_result = self.classification_agent.execute(
                merchant_name=preprocessing_result['merchant_name'],
                description=preprocessing_result['cleaned_description'],
                amount=amount,
                mcc_code=mcc_code,
                metadata=preprocessing_result.get('metadata')
            )
            self._log_step("ClassificationAgent", f"Completed - Category: {classification_result['category']}")
            
            # Step 3: Governance & Validation
            self._log_step("GovernanceAgent", "Starting governance and validation...")
            governance_result = self.governance_agent.execute(
                merchant_name=preprocessing_result['merchant_name'],
                description=preprocessing_result['cleaned_description'],
                amount=amount,
                category=classification_result['category'],
                confidence=classification_result['confidence'],
                reasoning=classification_result['reasoning'],
                subcategory=classification_result.get('subcategory'),
                mcc_code=mcc_code,
                metadata=preprocessing_result.get('metadata')
            )
            self._log_step("GovernanceAgent", f"Completed - Status: {governance_result['validation_status']}")
            
            # Compile final result with workflow information
            final_result = {
                **governance_result,
                "workflow_log": self.workflow_log,
                "original_description": description
            }
            
            return final_result
            
        except Exception as e:
            self._log_step("Orchestrator", f"Error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "workflow_log": self.workflow_log
            }
    
    def _log_step(self, agent_name: str, message: str):
        """Log a workflow step"""
        self.workflow_log.append({
            "agent": agent_name,
            "message": message
        })
