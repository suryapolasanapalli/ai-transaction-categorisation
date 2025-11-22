import streamlit as st
import pandas as pd
import os
import json
from typing import Dict, List
from dotenv import load_dotenv
from agents.preprocessing_agent import PreprocessingAgent
from agents.classification_agent import ClassificationAgent
from agents.governance_agent import GovernanceAgent
from agents.feedback_agent import FeedbackAgent
from agno.models.azure import AzureOpenAI
from tools.vendor_database import vendor_database_search
from tools.taxonomy import get_taxonomy_structure, get_valid_categories, get_subcategories, TRANSACTION_CATEGORIES
from tools.mcc_codes import classify_by_mcc_code, assign_mcc_code_for_category, lookup_mcc_by_vendor, get_mcc_statistics, MCC_CODES
from tools.user_preferences_tool import lookup_user_preference
from tools.custom_categories_tool import get_custom_categories, match_to_custom_category
from tools.store_user_preference_tool import store_user_preference
from utils.user_preferences import get_preferences_store
from utils.custom_categories import get_custom_categories_manager

# Load environment variables from .env file
load_dotenv()

st.set_page_config(
    page_title="🤖 AI Transaction Classifier",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        display: block;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .success-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .info-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Agent badge styling */
    .agent-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .preprocessing-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .classification-badge {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
    }
    
    .governance-badge {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
    }
    
    .feedback-badge {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Input styling */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #667eea;
    }
    
    /* Success/Error message styling */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 8px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# INITIALIZE AGENTS
# ---------------------------------------------------------
@st.cache_resource
def get_preprocessing_agent():
    """Initialize and cache the preprocessing agent"""
    return PreprocessingAgent(llm=None)

@st.cache_resource
def get_azure_llm():
    """Initialize and cache Azure OpenAI LLM for Agno"""
    return AzureOpenAI(
        id=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        temperature=1.0  # Azure OpenAI requirement
    )

@st.cache_resource
def get_classification_agent():
    """Initialize and cache the classification agent with Agno"""
    llm = get_azure_llm()
    tools = [
        lookup_user_preference,      # RAG tool - highest priority
        get_custom_categories,      # Custom categories check
        match_to_custom_category,    # Custom category matching
        classify_by_mcc_code,       # MCC code classification
        lookup_mcc_by_vendor,       # Vendor lookup
        vendor_database_search,     # Vendor database search
        get_taxonomy_structure      # Default taxonomy
    ]
    return ClassificationAgent(llm=llm, tools=tools)

@st.cache_resource
def get_governance_agent():
    """Initialize and cache the governance agent with Agno"""
    llm = get_azure_llm()
    tools = [assign_mcc_code_for_category]
    return GovernanceAgent(llm=llm, tools=tools)

@st.cache_resource
def get_feedback_agent():
    """Initialize and cache the feedback agent with Agno"""
    llm = get_azure_llm()
    tools = [store_user_preference]  # Tool to store user preferences in RAG system
    return FeedbackAgent(llm=llm, tools=tools)

preprocessing_agent = get_preprocessing_agent()
classification_agent = get_classification_agent()
governance_agent = get_governance_agent()

# ---------------------------------------------------------
# HELPER FUNCTIONS FOR FEEDBACK UI
# ---------------------------------------------------------
def get_all_available_categories() -> Dict[str, List[str]]:
    """
    Get all available categories from different sources:
    - Custom categories
    - User preferences (RAG)
    - MCC codes
    - Default taxonomy
    
    Returns:
        Dict with category as key and list of (source, subcategories) as value
    """
    all_categories = {}
    
    # 1. Custom Categories
    custom_categories_manager = get_custom_categories_manager()
    custom_cats = custom_categories_manager.get_categories()
    for cat, subcats in custom_cats.items():
        if cat not in all_categories:
            all_categories[cat] = {"source": "Custom", "subcategories": subcats}
        else:
            # Merge subcategories
            all_categories[cat]["subcategories"].extend(subcats)
            all_categories[cat]["subcategories"] = list(set(all_categories[cat]["subcategories"]))
    
    # 2. User Preferences (RAG)
    preferences_store = get_preferences_store()
    preferences = preferences_store.get_all_preferences()
    for pref in preferences:
        cat = pref.get("user_category")
        subcat = pref.get("user_subcategory")
        if cat:
            if cat not in all_categories:
                all_categories[cat] = {"source": "User Preference", "subcategories": []}
            if subcat and subcat not in all_categories[cat]["subcategories"]:
                all_categories[cat]["subcategories"].append(subcat)
    
    # 3. MCC Codes
    mcc_categories = {}
    for code, info in MCC_CODES.items():
        cat = info.get("category")
        subcat = info.get("subcategory")
        if cat:
            if cat not in mcc_categories:
                mcc_categories[cat] = []
            if subcat and subcat not in mcc_categories[cat]:
                mcc_categories[cat].append(subcat)
    
    for cat, subcats in mcc_categories.items():
        if cat not in all_categories:
            all_categories[cat] = {"source": "MCC", "subcategories": subcats}
        else:
            # Merge subcategories
            all_categories[cat]["subcategories"].extend(subcats)
            all_categories[cat]["subcategories"] = list(set(all_categories[cat]["subcategories"]))
            if all_categories[cat]["source"] != "Custom":
                all_categories[cat]["source"] = f"{all_categories[cat]['source']}, MCC"
    
    # 4. Default Taxonomy
    default_taxonomy = TRANSACTION_CATEGORIES
    for cat, subcats in default_taxonomy.items():
        if cat not in all_categories:
            all_categories[cat] = {"source": "Default", "subcategories": subcats}
        else:
            # Merge subcategories
            all_categories[cat]["subcategories"].extend(subcats)
            all_categories[cat]["subcategories"] = list(set(all_categories[cat]["subcategories"]))
            if "Default" not in all_categories[cat]["source"]:
                all_categories[cat]["source"] = f"{all_categories[cat]['source']}, Default"
    
    return all_categories


def get_category_list_for_dropdown() -> List[str]:
    """Get sorted list of all available categories for dropdown"""
    all_cats = get_all_available_categories()
    return sorted(all_cats.keys())


def get_subcategories_for_category(category: str) -> List[str]:
    """Get all available subcategories for a given category"""
    all_cats = get_all_available_categories()
    
    if category in all_cats:
        return sorted(all_cats[category]["subcategories"])
    
    # Fallback to default taxonomy
    return sorted(get_subcategories(category))

# ---------------------------------------------------------
# TRANSACTION PROCESSING FUNCTION
# ---------------------------------------------------------
def process_single_transaction(description, amount, merchant_name=None, mcc_code=None, status_placeholder=None):
    """Process transaction through Preprocessing Agent, Classification Agent, and Governance Agent with live status updates"""
    try:
        # Step 1: Preprocessing
        if status_placeholder:
            status_placeholder.info("🔄 **Step 1/3:** Preprocessing Agent is extracting and cleaning transaction data...")
        
        preprocessed_result = preprocessing_agent.execute(
            description=description,
            amount=amount,
            merchant_name=merchant_name,
            mcc_code=mcc_code
        )
        
        if status_placeholder:
            status_placeholder.success(f"✅ **Step 1/3 Complete:** Merchant: `{preprocessed_result.get('merchant_name', 'Unknown')}` | CMID: `{preprocessed_result.get('canonical_merchant_id', 'N/A')[:12]}...` | Tokens: {len(preprocessed_result.get('tokens', []))}")
        
        # Step 2: Classification using Agno Agent
        if status_placeholder:
            status_placeholder.info("🔄 **Step 2/3:** Classification Agent is analyzing with AI tools (RAG,MCC lookup, vendor search, taxonomy)...")
        
        classification_result = classification_agent.execute(
            merchant_name=preprocessed_result.get("merchant_name", "Unknown"),
            description=preprocessed_result.get("normalized_text", description),
            amount=amount,
            mcc_code=mcc_code,
            metadata=preprocessed_result.get("metadata", {})
        )
        
        if status_placeholder:
            status_placeholder.success(f"✅ **Step 2/3 Complete:** Category: `{classification_result.get('category', 'N/A')}` → `{classification_result.get('subcategory', 'N/A')}` | Confidence: `{classification_result.get('confidence', 'N/A').upper()}` | Tools Used: {len(classification_result.get('tool_calls', []))}")
        
        # Step 3: Governance and Validation using Agno Agent
        if status_placeholder:
            status_placeholder.info("🔄 **Step 3/3:** Governance Agent is validating classification ...")
        
        governance_result = governance_agent.execute(
            merchant_name=preprocessed_result.get("merchant_name", "Unknown"),
            description=preprocessed_result.get("normalized_text", description),
            amount=amount,
            category=classification_result.get("category", "Other"),
            confidence=classification_result.get("confidence", "medium"),
            reasoning=classification_result.get("reasoning", "No reasoning provided"),
            subcategory=classification_result.get("subcategory", "General"),
            mcc_code=mcc_code,
            metadata=preprocessed_result.get("metadata", {})
        )
        
        if status_placeholder:
            flags_display = f" | ⚠️ Flags: {len(governance_result.get('flags', []))}" if governance_result.get('flags') else ""
            status_placeholder.success(f"✅ **All Steps Complete!** Validation: `{governance_result.get('validation_status', 'N/A')}` | MCC: `{governance_result.get('mcc_code', 'N/A')}` | Final Confidence: `{governance_result.get('confidence', 'N/A').upper()}`{flags_display}")
        
        # Combine all results
        return {
            "merchant_name": governance_result.get("merchant_name", "Unknown"),
            "canonical_merchant_id": preprocessed_result.get("canonical_merchant_id", "N/A"),
            "category": governance_result.get("category", "Other"),
            "subcategory": governance_result.get("subcategory", "General"),
            "mcc_code": governance_result.get("mcc_code", "5999"),
            "mcc_description": governance_result.get("mcc_description", "Miscellaneous"),
            "confidence": governance_result.get("confidence", "medium"),
            "reasoning": classification_result.get("reasoning", "No reasoning provided"),
            "validation_status": governance_result.get("validation_status", "PASS"),
            "flags": governance_result.get("flags"),
            "audit_notes": governance_result.get("audit_notes", ""),
            "preprocessing_data": preprocessed_result,
            "classification_data": classification_result,
            "governance_data": governance_result,
            "workflow_log": [
                {"agent": "PreprocessingAgent", "message": "✅ Successfully preprocessed transaction"},
                {"agent": "PreprocessingAgent", "message": f"Created CMID: {preprocessed_result.get('canonical_merchant_id', 'N/A')}"},
                {"agent": "PreprocessingAgent", "message": f"Encrypted sensitive data: amount_token={preprocessed_result.get('sensitive_data', {}).get('amount_token', 'N/A')[:16]}..."},
                {"agent": "PreprocessingAgent", "message": f"Normalized text: {preprocessed_result.get('normalized_text', 'N/A')}"},
                {"agent": "ClassificationAgent", "message": f"✅ Classified as {classification_result.get('category', 'N/A')} > {classification_result.get('subcategory', 'N/A')}"},
                {"agent": "ClassificationAgent", "message": f"Confidence: {classification_result.get('confidence', 'N/A').upper()}"},
                {"agent": "ClassificationAgent", "message": f"Tool calls: {len(classification_result.get('tool_calls', []))}"},
                {"agent": "GovernanceAgent", "message": f"✅ Validated classification: {governance_result.get('validation_status', 'N/A')}"},
                {"agent": "GovernanceAgent", "message": f"Assigned MCC Code: {governance_result.get('mcc_code', 'N/A')} - {governance_result.get('mcc_description', 'N/A')}"},
                {"agent": "GovernanceAgent", "message": f"Final Confidence: {governance_result.get('confidence', 'N/A').upper()}"},
                {"agent": "GovernanceAgent", "message": f"Flags: {', '.join(governance_result.get('flags', [])) if governance_result.get('flags') else 'None'}"}
            ],
            "status": "success"
        }
    except Exception as e:
        if status_placeholder:
            status_placeholder.error(f"❌ **Error:** {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "workflow_log": [
                {"agent": "System", "message": f"❌ Error: {str(e)}"}
            ]
        }


# ---------------------------------------------------------
# STREAMLIT UI
# ---------------------------------------------------------
st.markdown('<h1 class="main-title">🤖 AI Transaction Classifier</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Agno Framework + Azure OpenAI | Intelligent Multi-Agent System</p>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 🤖 Multi-Agent AI System with Agno Framework")
st.info("**Preprocessing Agent** → **Classification Agent** → **Governance Agent** → **Feedback Agent**")

tab1, tab2, tab3, tab4 = st.tabs(["💳 Single Entry", "📊 Batch CSV Upload", "⚙️ Settings", "🏗️ Agent Architecture"])

# --- TAB 1: Single Transaction ---
with tab1:
    st.markdown("### 💳 Process Single Transaction")
    st.markdown("Enter transaction details below and let our AI agents classify it for you.")
    st.markdown("---")
    
    # Input section with better layout
    st.markdown("#### 📝 Transaction Details")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        desc = st.text_input(
            "Transaction Description",
            "Starbucks 00421 CA",
            help="Enter the transaction description as it appears on the statement",
            placeholder="e.g., STARBUCKS COFFEE #12345"
        )
    
    with col2:
        amt = st.number_input(
            "Amount ($)",
            value=5.00,
            min_value=0.01,
            step=0.01,
            help="Transaction amount in dollars"
        )
    
    st.markdown("#### 🔍 Optional Information (Improves Accuracy)")
    col1, col2 = st.columns(2)
    with col1:
        merchant = st.text_input(
            "Merchant Name",
            "",
            help="Official merchant name if known",
            placeholder="e.g., Starbucks Corporation"
        )
    with col2:
        mcc = st.text_input(
            "MCC Code",
            "",
            help="Merchant Category Code (4 digits)",
            placeholder="e.g., 5812"
        )

    # Create persistent status placeholder outside button handler
    agent_status = st.empty()
    
    # Initialize session state variables
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'final_status_message' not in st.session_state:
        st.session_state.final_status_message = None

    if st.button("Process Transaction", type="primary"):
        # Set processing flag
        st.session_state.processing = True
        st.session_state.final_status_message = None
        
        result = process_single_transaction(
            desc, 
            amt, 
            merchant_name=merchant if merchant else None,
            mcc_code=mcc if mcc else None,
            status_placeholder=agent_status
        )
        
        # Store in session state for feedback
        st.session_state.classification_result = result
        st.session_state.feedback_submitted = False
        st.session_state.updated_result = None
        st.session_state.processing = False
        # Reset feedback radio button to "Approve Classification"
        st.session_state.feedback_type_radio = "✅ Approve Classification"
        st.session_state.quick_feedback = None
        
        # Store final status message if available
        if result.get('status') == 'success':
            flags_display = f" | ⚠️ Flags: {len(result.get('flags', []))}" if result.get('flags') else ""
            st.session_state.final_status_message = f"✅ **All Steps Complete!** Validation: `{result.get('validation_status', 'N/A')}` | MCC: `{result.get('mcc_code', 'N/A')}` | Final Confidence: `{result.get('confidence', 'N/A').upper()}`{flags_display}"
        else:
            st.session_state.final_status_message = f"❌ **Error:** {result.get('error', 'Unknown error')}"
        
        # Rerun to display results immediately (status placeholder will persist)
        st.rerun()
    
    # Show final status message if available (after rerun) - this ensures it persists
    if st.session_state.get('final_status_message') and not st.session_state.get('processing', False):
        agent_status.success(st.session_state.final_status_message)
    
    # Display results if available in session state
    if 'classification_result' in st.session_state and st.session_state.classification_result:
        result = st.session_state.classification_result
        
        if result.get('status') == 'error':
            st.error(f"Error: {result.get('error')}")
        else:
            st.success("✅ **Classification Complete!**")
            st.markdown("---")
            
            # Main results in beautiful cards
            st.markdown("### 🎯 Classification Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div style='padding: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                    <h4 style='margin: 0; font-size: 0.9rem; opacity: 0.9;'>🏪 MERCHANT</h4>
                    <h2 style='margin: 0.5rem 0;'>{result.get('merchant_name', 'N/A')}</h2>
                    <p style='margin: 0; font-size: 0.85rem; opacity: 0.8;'>CMID: {result.get('canonical_merchant_id', 'N/A')[:12]}...</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style='padding: 1.5rem; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 15px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                    <h4 style='margin: 0; font-size: 0.9rem; opacity: 0.9;'>📂 CATEGORY</h4>
                    <h2 style='margin: 0.5rem 0;'>{result.get('category', 'N/A')}</h2>
                    <p style='margin: 0; font-size: 0.85rem; opacity: 0.8;'>{result.get('subcategory', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                confidence_value = result.get('confidence', 'N/A')
                conf_color = '#f093fb' if confidence_value == 'HIGH' else ('#feca57' if confidence_value == 'MEDIUM' else '#ff6b6b')
                conf_color2 = '#f5576c' if confidence_value == 'HIGH' else ('#ff9ff3' if confidence_value == 'MEDIUM' else '#ffa07a')
                st.markdown(f"""
                <div style='padding: 1.5rem; background: linear-gradient(135deg, {conf_color} 0%, {conf_color2} 100%); border-radius: 15px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                    <h4 style='margin: 0; font-size: 0.9rem; opacity: 0.9;'>📊 CONFIDENCE</h4>
                    <h2 style='margin: 0.5rem 0;'>{confidence_value.upper() if confidence_value != 'N/A' else 'N/A'}</h2>
                    <p style='margin: 0; font-size: 0.85rem; opacity: 0.8;'>AI Certainty Level</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # MCC Code and Description
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div style='padding: 1rem; background: #f8f9fa; border-left: 4px solid #667eea; border-radius: 8px;'>
                    <strong>🏷️ MCC Code:</strong> <code>{result.get('mcc_code', 'N/A')}</code>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style='padding: 1rem; background: #f8f9fa; border-left: 4px solid #4facfe; border-radius: 8px;'>
                    <strong>📋 Description:</strong> {result.get('mcc_description', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
            
            # Validation status
            validation_status = result.get('validation_status', 'UNKNOWN')
            if validation_status == 'PASS':
                st.success(f"✅ Validation Status: {validation_status}")
            elif validation_status == 'FAIL':
                st.error(f"❌ Validation Status: {validation_status}")
            elif validation_status == 'CLASSIFICATION_COMPLETE':
                st.success(f"✅ Status: {validation_status}")
            elif validation_status == 'PREPROCESSING_COMPLETE':
                st.info(f"🔄 Status: {validation_status}")
            else:
                st.warning(f"⚠️ Validation Status: {validation_status}")
            
            # Reasoning and audit notes
            st.markdown("**Reasoning:**")
            st.write(result.get('reasoning', 'N/A'))
            
            if result.get('audit_notes'):
                st.markdown("**Audit Notes:**")
                st.write(result.get('audit_notes'))
            
            # Flags if any
            if result.get('flags'):
                st.warning(f"⚠️ Flags: {', '.join(result.get('flags'))}")
            
            # Preprocessing Data Details
            if 'preprocessing_data' in result:
                with st.expander("🔍 View Preprocessing Details"):
                        prep_data = result['preprocessing_data']
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**📝 Extracted Information:**")
                            st.write(f"- **Canonical Merchant:** {prep_data.get('canonical_merchant', 'N/A')}")
                            st.write(f"- **CMID:** `{prep_data.get('canonical_merchant_id', 'N/A')}`")
                            st.write(f"- **Original Merchant:** {prep_data.get('original_merchant', 'N/A')}")
                            st.write(f"- **Cleaned Description:** {prep_data.get('cleaned_description', 'N/A')}")
                            
                            metadata = prep_data.get('metadata', {})
                            if metadata.get('location'):
                                st.write(f"- **Location:** {metadata['location']}")
                            if metadata.get('transaction_type'):
                                st.write(f"- **Transaction Type:** {metadata['transaction_type']}")
                        
                        with col2:
                            st.markdown("**🔒 Sensitive Data (Encrypted):**")
                            sensitive = prep_data.get('sensitive_data', {})
                            if sensitive:
                                amount_token = sensitive.get('amount_token', 'N/A')
                                st.code(f"Amount Token: {amount_token[:32] if amount_token != 'N/A' else 'N/A'}...", language="text")
                                
                                mcc_token = sensitive.get('mcc_token', 'N/A')
                                if mcc_token and mcc_token != 'N/A':
                                    st.code(f"MCC Token: {mcc_token[:32]}...", language="text")
                                else:
                                    st.code(f"MCC Token: Not provided", language="text")
                            
                            st.markdown("**⚙️ Operations Performed:**")
                            operations = ['Tokenization', 'Noise Removal', 'Text Normalization', 'Merchant Canonicalization', 'Sensitive Data Encryption']
                            for op in operations:
                                st.write(f"✓ {op}")
                        
                        st.markdown("**📊 Full Preprocessing Output:**")
                        st.json(prep_data)
                
                # Classification Data Details
                if 'classification_data' in result:
                    with st.expander("🎯 View Classification Details (Agno AI Agent)"):
                        class_data = result['classification_data']
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**🤖 Classification Results:**")
                            st.write(f"- **Category:** {class_data.get('category', 'N/A')}")
                            st.write(f"- **Subcategory:** {class_data.get('subcategory', 'N/A')}")
                            st.write(f"- **Confidence:** {class_data.get('confidence', 'N/A').upper()}")
                            st.write(f"- **Agent:** {class_data.get('agent_used', 'N/A')}")
                            
                            st.markdown("**💭 AI Reasoning:**")
                            st.write(class_data.get('reasoning', 'No reasoning provided'))
                        
                        with col2:
                            st.markdown("**🔧 Tool Usage:**")
                            tool_calls = class_data.get('tool_calls', [])
                            if tool_calls:
                                st.write(f"- **Tools Called:** {len(tool_calls)}")
                                for idx, tool_call in enumerate(tool_calls, 1):
                                    with st.container():
                                        st.text(f"Tool {idx}:")
                                        st.code(str(tool_call)[:200], language="text")
                            else:
                                st.write("No tool calls recorded")
                            
                            st.markdown("**📋 Metadata:**")
                            metadata = class_data.get('metadata', {})
                            st.write(f"- Merchant Analyzed: {metadata.get('merchant_analyzed', 'N/A')}")
                            st.write(f"- Amount: ${metadata.get('amount_analyzed', 0):.2f}")
                            st.write(f"- MCC Provided: {'Yes' if metadata.get('mcc_provided') else 'No'}")
                        
                        st.markdown("**📊 Full Classification Output:**")
                        st.json(class_data)
                
                # Governance Data Details
                if 'governance_data' in result:
                    with st.expander("⚖️ View Governance & Validation Details (Agno AI Agent)"):
                        gov_data = result['governance_data']
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**✅ Validation Results:**")
                            validation = gov_data.get('validation_status', 'N/A')
                            if validation == 'PASS':
                                st.success(f"Status: {validation}")
                            else:
                                st.error(f"Status: {validation}")
                            
                            st.write(f"- **Final Category:** {gov_data.get('category', 'N/A')}")
                            st.write(f"- **Final Subcategory:** {gov_data.get('subcategory', 'N/A')}")
                            st.write(f"- **Final Confidence:** {gov_data.get('confidence', 'N/A').upper()}")
                            st.write(f"- **Assigned MCC:** {gov_data.get('mcc_code', 'N/A')}")
                            st.write(f"- **MCC Description:** {gov_data.get('mcc_description', 'N/A')}")
                            st.write(f"- **Agent:** {gov_data.get('agent_used', 'N/A')}")
                            
                            # Flags
                            flags = gov_data.get('flags')
                            if flags:
                                st.markdown("**🚩 Compliance Flags:**")
                                for flag in flags:
                                    st.warning(f"⚠️ {flag}")
                            else:
                                st.markdown("**🚩 Compliance Flags:**")
                                st.success("✓ No flags - All clear")
                        
                        with col2:
                            st.markdown("**📝 Audit Notes:**")
                            st.write(gov_data.get('audit_notes', 'No audit notes'))
                            
                            st.markdown("**🔧 Tool Usage:**")
                            tool_calls = gov_data.get('tool_calls', [])
                            if tool_calls:
                                st.write(f"- **Tools Called:** {len(tool_calls)}")
                                for idx, tool_call in enumerate(tool_calls, 1):
                                    with st.container():
                                        st.text(f"Tool {idx}:")
                                        st.code(str(tool_call)[:200], language="text")
                            else:
                                st.write("No additional tools called")
                            
                            st.markdown("**💬 Governance Response:**")
                            gov_response = gov_data.get('governance_response', 'N/A')
                            if len(gov_response) > 300:
                                st.text_area("Full Response", gov_response, height=150)
                            else:
                                st.write(gov_response)
                        
                        st.markdown("**📊 Full Governance Output:**")
                        st.json(gov_data)
                
                # Workflow log
                with st.expander("🔍 View Agent Workflow (Agentic AI in Action)"):
                    st.markdown("**Complete Agent Execution Log:**")
                    workflow_log = result.get('workflow_log', [])
                    
                    # Group by agent
                    preprocessing_logs = [log for log in workflow_log if 'Preprocessing' in log['agent']]
                    classification_logs = [log for log in workflow_log if 'Classification' in log['agent']]
                    governance_logs = [log for log in workflow_log if 'Governance' in log['agent']]
                    
                    if preprocessing_logs:
                        st.markdown("**🔄 PreprocessingAgent:**")
                        for log in preprocessing_logs:
                            st.text(f"  → {log['message']}")
                    
                    if classification_logs:
                        st.markdown("**📊 ClassificationAgent:**")
                        for log in classification_logs:
                            st.text(f"  → {log['message']}")
                    
                    if governance_logs:
                        st.markdown("**✅ GovernanceAgent:**")
                        for log in governance_logs:
                            st.text(f"  → {log['message']}")
                    
                    st.caption("Each agent operates autonomously with its own LLM calls and decision-making")
                
                # Full JSON
                with st.expander("📄 View Full JSON Response"):
                    st.json(result)
                
                # ========================================
                # FEEDBACK SECTION
                # ========================================
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.markdown("""
                <div style='padding: 1.5rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 15px; color: white; margin: 2rem 0;'>
                    <h2 style='margin: 0; font-size: 1.8rem;'>💬 Provide Feedback</h2>
                    <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Help us improve by sharing your thoughts on this classification</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Initialize session state for feedback
                if 'feedback_submitted' not in st.session_state:
                    st.session_state.feedback_submitted = False
                if 'updated_result' not in st.session_state:
                    st.session_state.updated_result = None
                
                # Feedback options with styled cards
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("#### Choose Feedback Type")
                    # Initialize feedback_type_radio if not exists or reset to approve
                    feedback_options = ["✅ Approve Classification", "✏️ Correct Classification", "💬 Add Comment"]
                    if 'feedback_type_radio' not in st.session_state:
                        st.session_state.feedback_type_radio = feedback_options[0]
                    
                    feedback_type = st.radio(
                        "Select one:",
                        feedback_options,
                        key="feedback_type_radio",
                        help="Choose how you want to provide feedback"
                    )
                
                # with col2:
                #     st.markdown("#### Quick Actions")
                #     st.markdown("""
                #     <style>
                #     .quick-btn {
                #         display: block;
                #         width: 100%;
                #         margin-bottom: 0.5rem;
                #     }
                #     </style>
                #     """, unsafe_allow_html=True)
                #     if st.button("👍 Looks Good!", use_container_width=True, key="quick_approve"):
                #         st.session_state.quick_feedback = "approve"
                #     if st.button("👎 Needs Fix", use_container_width=True, key="quick_fix"):
                #         st.session_state.quick_feedback = "correct"
                
                # Feedback form
                if "✏️ Correct Classification" in feedback_type or st.session_state.get('quick_feedback') == 'correct':
                    st.markdown("**Provide Correct Classification:**")
                    
                    try:
                        # Get all available categories
                        all_categories = get_all_available_categories()
                        category_list = get_category_list_for_dropdown()
                    except Exception as e:
                        st.error(f"Error loading categories: {str(e)}")
                        st.info("Please refresh the page and try again.")
                        category_list = []
                        all_categories = {}
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Category:**")
                        # Add "Custom Input" option to the list
                        category_options = ["--- Select or Enter Custom ---"] + category_list
                        
                        # Find current index
                        current_category = result.get('category', '') or ''
                        current_idx = 0
                        if current_category and current_category in category_list:
                            try:
                                current_idx = category_list.index(current_category) + 1
                            except ValueError:
                                current_idx = 0
                        
                        selected_category_idx = st.selectbox(
                            "Choose from available categories:",
                            options=range(len(category_options)),
                            format_func=lambda x: category_options[x],
                            index=current_idx,
                            key="category_selectbox"
                        )
                        
                        # Determine selected category
                        corrected_category = ''
                        try:
                            if selected_category_idx == 0:
                                # Custom input selected
                                corrected_category = st.text_input(
                                    "Enter Custom Category:",
                                    value=current_category if current_category and current_category not in category_list else '',
                                    key="custom_category_input",
                                    placeholder="e.g., Business Expenses"
                                ) or ''
                            else:
                                # Category from dropdown selected
                                if selected_category_idx < len(category_options):
                                    corrected_category = category_options[selected_category_idx] or ''
                        except Exception as e:
                            st.error(f"Error in category selection: {str(e)}")
                            corrected_category = current_category
                    
                    with col2:
                        st.markdown("**Subcategory:**")
                        
                        # Initialize corrected_subcategory
                        corrected_subcategory = ''
                        current_subcategory = result.get('subcategory', '') or ''
                        
                        # Get subcategories for selected category
                        if corrected_category and corrected_category.strip() and selected_category_idx > 0:
                            # Category selected from dropdown
                            try:
                                available_subcategories = get_subcategories_for_category(corrected_category)
                                
                                if available_subcategories:
                                    subcategory_options = ["--- Select or Enter Custom ---"] + available_subcategories
                                    
                                    # Find current subcategory index
                                    current_sub_idx = 0
                                    if current_subcategory in available_subcategories:
                                        current_sub_idx = available_subcategories.index(current_subcategory) + 1
                                    
                                    selected_subcategory_idx = st.selectbox(
                                        "Choose from available subcategories:",
                                        options=range(len(subcategory_options)),
                                        format_func=lambda x: subcategory_options[x],
                                        index=current_sub_idx,
                                        key="subcategory_selectbox"
                                    )
                                    
                                    if selected_subcategory_idx == 0:
                                        # Custom subcategory input
                                        corrected_subcategory = st.text_input(
                                            "Enter Custom Subcategory:",
                                            value=current_subcategory if current_subcategory not in available_subcategories else '',
                                            key="custom_subcategory_input",
                                            placeholder="e.g., Office Supplies"
                                        ) or ''
                                    else:
                                        # Subcategory from dropdown
                                        corrected_subcategory = subcategory_options[selected_subcategory_idx] or ''
                                else:
                                    # No subcategories available, use custom input
                                    corrected_subcategory = st.text_input(
                                        "Enter Subcategory:",
                                        value=current_subcategory,
                                        key="custom_subcategory_input",
                                        placeholder="e.g., General"
                                    ) or ''
                            except Exception as e:
                                # Fallback to custom input if error
                                st.warning(f"Error loading subcategories: {str(e)}")
                                corrected_subcategory = st.text_input(
                                    "Enter Subcategory:",
                                    value=current_subcategory,
                                    key="custom_subcategory_input",
                                    placeholder="e.g., General"
                                ) or ''
                        else:
                            # Custom category or no category selected, allow custom subcategory
                            corrected_subcategory = st.text_input(
                                "Enter Subcategory:",
                                value=current_subcategory,
                                key="custom_subcategory_input",
                                placeholder="e.g., General"
                            ) or ''
                    
                    # Show category source info
                    if corrected_category and corrected_category in all_categories:
                        source_info = all_categories[corrected_category]["source"]
                        st.info(f"ℹ️ Category source: {source_info}")
                    
                    feedback_text = st.text_area(
                        "Additional Comments (Optional):",
                        placeholder="Explain why this classification is incorrect...",
                        key="correction_comments"
                    )
                    
                    if st.button("🔄 Apply Correction", type="primary", key="apply_correction"):
                        # Validate inputs
                        corrected_category = corrected_category or ''
                        corrected_subcategory = corrected_subcategory or ''
                        
                        if not corrected_category.strip():
                            st.error("❌ Please provide a category")
                        elif not corrected_subcategory.strip():
                            st.error("❌ Please provide a subcategory")
                        else:
                            with st.spinner("Processing your feedback..."):
                                feedback_agent = get_feedback_agent()
                                
                                # Build feedback message
                                feedback_msg = f"Correct category to: {corrected_category.strip()} / {corrected_subcategory.strip()}"
                                if feedback_text:
                                    feedback_msg += f". Additional comments: {feedback_text}"
                                
                                # Process feedback
                                updated_result = feedback_agent.execute(
                                    original_classification=result,
                                    user_feedback=feedback_msg,
                                    feedback_type="correction"
                                )
                                
                                # Store user preference in RAG system for future transactions
                                # Check if agent already stored it via tool (preference_stored flag)
                                if updated_result.get('updated', False) and not updated_result.get('preference_stored', False):
                                    # Agent didn't store it, so we'll store it manually as fallback
                                    preferences_store = get_preferences_store()
                                    preferences_store.add_preference(
                                        merchant_name=result.get('merchant_name', 'Unknown'),
                                        description=result.get('preprocessing_data', {}).get('normalized_text', '') or result.get('description', ''),
                                        user_category=updated_result.get('category', corrected_category.strip()),
                                        user_subcategory=updated_result.get('subcategory', corrected_subcategory.strip()),
                                        original_category=result.get('category'),
                                        original_subcategory=result.get('subcategory'),
                                        amount=result.get('preprocessing_data', {}).get('amount', 0) or result.get('amount', 0)
                                    )
                                    updated_result['preference_stored'] = True
                                elif updated_result.get('preference_stored', False):
                                    # Agent already stored it via tool
                                    st.success(f"✅ User preference stored in RAG system (ID: {updated_result.get('preference_id', 'N/A')})")
                                
                                st.session_state.updated_result = updated_result
                                st.session_state.feedback_submitted = True
                                st.rerun()
                
                elif "💬 Add Comment" in feedback_type:
                    feedback_text = st.text_area(
                        "Your Comments:",
                        placeholder="Share your thoughts about this classification...",
                        key="comment_text"
                    )
                    
                    if st.button("📝 Submit Comment", type="primary", key="submit_comment"):
                        with st.spinner("Processing your feedback..."):
                            feedback_agent = get_feedback_agent()
                            
                            updated_result = feedback_agent.execute(
                                original_classification=result,
                                user_feedback=feedback_text,
                                feedback_type="comment"
                            )
                            
                            st.session_state.updated_result = updated_result
                            st.session_state.feedback_submitted = True
                            st.rerun()
                
                else:  # Approve
                    if st.button("✅ Approve This Classification", type="primary", key="approve_classification") or st.session_state.get('quick_feedback') == 'approve':
                        with st.spinner("Recording your approval..."):
                            feedback_agent = get_feedback_agent()
                            
                            updated_result = feedback_agent.execute(
                                original_classification=result,
                                user_feedback="User approved this classification as correct",
                                feedback_type="approval"
                            )
                            
                            st.session_state.updated_result = updated_result
                            st.session_state.feedback_submitted = True
                            st.rerun()
                
                # Show updated result if feedback was processed
                if st.session_state.feedback_submitted and st.session_state.updated_result:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("""
                    <div style='padding: 1.5rem; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); border-radius: 15px; color: white;'>
                        <h3 style='margin: 0;'>✅ Feedback Processed Successfully!</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    updated = st.session_state.updated_result
                    
                    # Show what changed
                    if updated.get('updated', False):
                        st.markdown("""
                        <div style='padding: 1rem; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 8px; margin-bottom: 1rem;'>
                            <h4 style='margin: 0; color: #856404;'>🔄 Classification Updated Based on Your Feedback</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("""
                            <div style='padding: 1rem; background: #f8f9fa; border-radius: 8px; border: 2px solid #dc3545;'>
                                <h4 style='color: #dc3545; margin-top: 0;'>❌ Before</h4>
                            """, unsafe_allow_html=True)
                            st.write(f"**Category:** {updated.get('original_category', 'N/A')}")
                            st.write(f"**Subcategory:** {updated.get('original_subcategory', 'N/A')}")
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("""
                            <div style='padding: 1rem; background: #f8f9fa; border-radius: 8px; border: 2px solid #28a745;'>
                                <h4 style='color: #28a745; margin-top: 0;'>✅ After</h4>
                            """, unsafe_allow_html=True)
                            st.write(f"**Category:** {updated.get('category', 'N/A')}")
                            st.write(f"**Subcategory:** {updated.get('subcategory', 'N/A')}")
                            st.write(f"**Confidence:** {updated.get('confidence', 'N/A')}")
                            st.write(f"**MCC Code:** {updated.get('mcc_code', 'N/A')}")
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # AI Reasoning card
                        st.markdown(f"""
                        <div style='padding: 1rem; background: #e7f3ff; border-left: 4px solid #0066cc; border-radius: 8px; margin-bottom: 1rem;'>
                            <h4 style='color: #0066cc; margin-top: 0;'>🤖 AI Reasoning</h4>
                            <p style='margin-bottom: 0; color: #333;'>{updated.get('reasoning', 'No reasoning provided')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Audit Trail card
                        st.markdown(f"""
                        <div style='padding: 1rem; background: #f0f0f0; border-left: 4px solid #6c757d; border-radius: 8px;'>
                            <h4 style='color: #6c757d; margin-top: 0;'>📋 Audit Trail</h4>
                            <p style='margin-bottom: 0; color: #333;'>{updated.get('audit_notes', 'No audit notes')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    else:
                        st.markdown("""
                        <div style='padding: 1.5rem; background: #d1ecf1; border-left: 4px solid #0c5460; border-radius: 8px;'>
                            <h4 style='color: #0c5460; margin-top: 0;'>✅ Feedback Acknowledged</h4>
                            <p style='margin-bottom: 0; color: #0c5460;'>""" + updated.get('feedback_applied', 'Thank you for your feedback!') + """</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Show full feedback result
                    with st.expander("📊 View Full Feedback Processing Result"):
                        st.json(updated)
                    
                    # Reset button with styling
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("🔄 Clear Feedback and Try Again", use_container_width=True, type="secondary"):
                            st.session_state.feedback_submitted = False
                            st.session_state.updated_result = None
                            st.session_state.quick_feedback = None
                            st.rerun()

# --- TAB 2: Batch CSV Processing ---
with tab2:
    st.markdown("### 📊 Batch Processing")
    st.markdown("Upload a CSV file to process multiple transactions at once. Our AI agents will classify each transaction automatically.")
    st.markdown("---")
    
    # Sample CSV template for download with better styling
    st.markdown("#### 📥 Download Sample Template")
    
    sample_data = {
        'description': ['Starbucks Coffee Shop', 'Shell Gas Station', 'Walmart Supercenter', 'Netflix Subscription'],
        'amount': [5.50, 45.00, 123.45, 15.99],
        'merchant_name': ['Starbucks', 'Shell', 'Walmart', 'Netflix'],
        'mcc_code': ['5812', '5541', '5411', '7841']
    }
    sample_df = pd.DataFrame(sample_data)
    sample_csv = sample_df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        "📥 Download Sample CSV Template",
        sample_csv,
        "sample_transactions.csv",
        "text/csv",
        help="Download this template to see the expected format"
    )
    
    st.divider()

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            # Try to read with error handling and flexible options
            df = pd.read_csv(
                uploaded_file,
                on_bad_lines='skip',  # Skip bad lines instead of failing
                encoding='utf-8',
                skipinitialspace=True
            )
            
            # Clean column names - strip whitespace and convert to lowercase
            df.columns = df.columns.str.strip().str.lower()
            
            # Check for required columns (now in lowercase)
            required_columns = ['description', 'amount']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                st.info("📋 Your CSV must have at least: `description` and `amount` columns")
                st.info("📋 Optional columns: `merchant_name`, `mcc_code`")
                
                # Show what columns were found
                st.write("**Columns found in your file (after cleaning):**")
                st.write(df.columns.tolist())
                
                # Show a debug view with raw column names
                with st.expander("🔍 Debug: Raw file preview"):
                    uploaded_file.seek(0)
                    st.text(uploaded_file.read().decode('utf-8')[:500])
                
            else:
                st.success(f"✅ CSV loaded successfully! Found {len(df)} rows")
                st.write("**Preview:**", df.head())

                if st.button("Start Batch Job", type="primary"):
                    results = []
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    # Limit for demo purposes to prevent long waits/high costs
                    rows_to_process = df.head(5)
                    total_rows = len(rows_to_process)

                    st.warning(f"Processing first {total_rows} rows for demo speed...")
                    
                    # Create dynamic status placeholder for each transaction
                    transaction_status = st.empty()

                    for index, row in rows_to_process.iterrows():
                        try:
                            # Update overall progress
                            status_text.text(f"📋 Processing Row {index + 1}/{total_rows}: {row['description'][:50]}...")
                            
                            # Process the transaction with dynamic status updates
                            result = process_single_transaction(
                                str(row['description']), 
                                float(row.get('amount', 0)),
                                merchant_name=str(row.get('merchant_name')) if 'merchant_name' in row and pd.notna(row.get('merchant_name')) else None,
                                mcc_code=str(row.get('mcc_code')) if 'mcc_code' in row and pd.notna(row.get('mcc_code')) else None,
                                status_placeholder=transaction_status
                            )

                            # Flatten result for CSV
                            flattened = {
                                'original_description': row['description'],
                                'original_amount': row.get('amount', 0),
                                'merchant_name': result.get('merchant_name'),
                                'category': result.get('category'),
                                'subcategory': result.get('subcategory'),
                                'mcc_code': result.get('mcc_code'),
                                'mcc_description': result.get('mcc_description'),
                                'confidence': result.get('confidence'),
                                'validation_status': result.get('validation_status'),
                                'reasoning': result.get('reasoning'),
                                'flags': ', '.join(result.get('flags', [])) if result.get('flags') else None
                            }
                            results.append(flattened)
                            
                        except Exception as e:
                            st.error(f"Error processing row {index + 1}: {str(e)}")
                            flattened = {
                                'original_description': row.get('description', 'N/A'),
                                'original_amount': row.get('amount', 0),
                                'merchant_name': 'ERROR',
                                'category': 'ERROR',
                                'subcategory': 'ERROR',
                                'mcc_code': 'ERROR',
                                'mcc_description': 'ERROR',
                                'confidence': 'ERROR',
                                'validation_status': 'ERROR',
                                'reasoning': f'Error: {str(e)}',
                                'flags': 'Processing Error'
                            }
                            results.append(flattened)

                        # Update Progress
                        progress_bar.progress((index + 1) / total_rows)

                    # Clear transaction status and show completion
                    transaction_status.empty()
                    status_text.text("✅ Job Complete!")
                    final_df = pd.DataFrame(results)

                    st.divider()
                    st.subheader("Final Categorization Results")
                    st.dataframe(final_df, use_container_width=True)

                    # Download Button
                    csv = final_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📥 Download Results CSV",
                        csv,
                        "transaction_results.csv",
                        "text/csv",
                        type="primary"
                    )
                    
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")
            st.info("""
            **Troubleshooting Tips:**
            - Make sure your CSV has proper headers
            - Required columns: `description`, `amount`
            - Optional columns: `merchant_name`, `mcc_code`
            - Check for special characters or encoding issues
            - Try opening and re-saving the file in Excel or Google Sheets
            
            **Example CSV format:**
            ```
            description,amount,merchant_name,mcc_code
            Starbucks Coffee,5.50,Starbucks,5812
            Shell Gas Station,45.00,Shell,5541
            ```
            """)
            
            # Show raw file content for debugging
            with st.expander("🔍 Debug: View Raw File Content"):
                uploaded_file.seek(0)
                content = uploaded_file.read().decode('utf-8', errors='ignore')
                st.text_area("Raw content:", content[:1000], height=200)

# --- TAB 3: Settings (Custom Categories & Preferences) ---
with tab3:
    st.markdown("### ⚙️ Settings & Customization")
    st.markdown("Manage custom categories and view user preferences")
    st.markdown("---")
    
    # Custom Categories Management
    st.markdown("#### 📁 Custom Categories")
    st.info("Define your own transaction categories. The AI will use these categories first before default taxonomy.")
    
    custom_categories_manager = get_custom_categories_manager()
    existing_categories = custom_categories_manager.get_categories()
    
    if existing_categories:
        st.markdown("**Current Custom Categories:**")
        for category, subcategories in existing_categories.items():
            with st.expander(f"📂 {category}"):
                st.write("**Subcategories:**")
                for subcat in subcategories:
                    st.write(f"- {subcat}")
                if st.button(f"🗑️ Delete {category}", key=f"delete_{category}"):
                    custom_categories_manager.remove_category(category)
                    st.success(f"Deleted category: {category}")
                    st.rerun()
    
    st.markdown("---")
    st.markdown("#### ➕ Add New Custom Category")
    
    with st.form("add_custom_category"):
        new_category = st.text_input("Category Name", placeholder="e.g., Business Expenses")
        new_subcategories = st.text_area(
            "Subcategories (one per line)",
            placeholder="e.g., Office Supplies\nTravel\nMeals",
            help="Enter subcategories, one per line"
        )
        
        submitted = st.form_submit_button("➕ Add Category", type="primary")
        
        if submitted:
            if new_category and new_subcategories:
                subcategories_list = [s.strip() for s in new_subcategories.split('\n') if s.strip()]
                if subcategories_list:
                    success = custom_categories_manager.add_category(new_category, subcategories_list)
                    if success:
                        st.success(f"✅ Added custom category: {new_category} with {len(subcategories_list)} subcategories")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add category")
                else:
                    st.warning("⚠️ Please provide at least one subcategory")
            else:
                st.warning("⚠️ Please fill in both category name and subcategories")
    
    st.markdown("---")
    
    # User Preferences View
    st.markdown("#### 💾 User Preferences (RAG)")
    st.info("View your transaction classification preferences learned from your feedback.")
    
    preferences_store = get_preferences_store()
    all_preferences = preferences_store.get_all_preferences()
    
    if all_preferences:
        st.markdown(f"**Total Preferences Stored:** {len(all_preferences)}")
        
        with st.expander("📋 View All Preferences"):
            for idx, pref in enumerate(all_preferences):
                st.markdown(f"""
                **Preference {idx + 1}:**
                - Merchant: `{pref.get('merchant_name', 'N/A')}`
                - User Category: `{pref.get('user_category', 'N/A')}` / `{pref.get('user_subcategory', 'N/A')}`
                - Original: `{pref.get('original_category', 'N/A')}` / `{pref.get('original_subcategory', 'N/A')}`
                - Usage Count: {pref.get('usage_count', 0)}
                - Created: {pref.get('created_at', 'N/A')[:10]}
                """)
        
        if st.button("🗑️ Clear All Preferences", type="secondary"):
            preferences_store.clear_preferences()
            st.success("✅ All preferences cleared")
            st.rerun()
    else:
        st.info("No preferences stored yet. Preferences are automatically saved when you correct a classification.")

# --- TAB 4: Agent Architecture ---
with tab4:
    st.subheader("🤖 Agno Framework - Transaction Classification System")
    
    st.markdown("""
    This system uses **Agno Framework v2.2.13** - a production-ready agentic AI framework 
    that powers autonomous agents with specialized roles and tools. Each agent operates 
    independently while collaborating in a sequential pipeline to ensure accurate transaction 
    classification with full compliance and auditability.
    
    ### ⚡ Technology Stack
    
    - **Framework:** Agno 2.2.13
    - **LLM:** Azure OpenAI (gpt-5)
    - **Security:** SHA-256 encryption for sensitive data
    - **UI:** Streamlit with real-time processing
    - **Architecture:** 4-Agent Sequential Pipeline with RAG Feedback Loop
    - **RAG System:** User preference learning with similarity search
    - **Custom Categories:** User-defined taxonomy support
    
    ---
    
    ### 🔄 Four-Agent Pipeline
    """)
    
    # Visual flow
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        st.markdown("#### 1️⃣ Preprocessing Agent")
        st.success("""
        **Type:** Deterministic (No LLM, No Tools)
        
        **Role:** Data Cleaning & Security
        
        **Operations:**
        - Tokenization (regex-based)
        - Noise removal (5 patterns)
        - Text normalization
        - Merchant canonicalization
        - CMID generation (SHA-256)
        - Sensitive data encryption
        
        **Input:**
        - Raw description
        - Amount, merchant, MCC
        
        **Output:**
        - CMID (Canonical Merchant ID)
        - Encrypted tokens
        - Clean metadata
        - Normalized text
        """)
    
    with col2:
        st.markdown("#### 2️⃣ Classification Agent")
        st.info("""
        **Type:** Agno Agent + Azure OpenAI + RAG
        
        **Role:** AI-Powered Classification with Learning
        
        **Priority Order:**
        1. User Preferred Category (RAG)
        2. Custom Categories (GenAI)
        3. MCC Categorization
        4. GenAI LLM (Default)
        
        **Agno Tools (7):**
        1. `lookup_user_preference()` - RAG user preference lookup
        2. `get_custom_categories()` - Custom categories check
        3. `match_to_custom_category()` - Custom category matching
        4. `classify_by_mcc_code()` - 200+ MCC codes
        5. `lookup_mcc_by_vendor()` - 100+ brands
        6. `vendor_database_search()` - 20 patterns
        7. `get_taxonomy_structure()` - 12 categories
        
        **RAG Features:**
        - User preference learning
        - Similarity-based retrieval
        - Custom categories support
        
        **Output:**
        - Category & Subcategory
        - Confidence level
        - Classification method used
        - Reasoning explanation
        """)
    
    with col3:
        st.markdown("#### 3️⃣ Governance Agent")
        st.warning("""
        **Type:** Agno Agent + Azure OpenAI
        
        **Role:** Validation & Compliance
        
        **Agno Tools (1):**
        1. `assign_mcc_code_for_category()` - Reverse lookup (Category → MCC)
        
        **Intelligence:**
        - Category validation
        - MCC code verification/assignment
        - Confidence adjustment
        - Compliance flagging
        
        **Output:**
        - Validation status (PASS/FAIL)
        - Final MCC code
        - Adjusted confidence
        - Audit notes
        - Compliance flags
        """)
    
    with col4:
        st.markdown("#### 4️⃣ Feedback Agent")
        st.markdown("""
        <div style='padding: 1rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 10px; color: white;'>
        <strong>Type:</strong> Agno Agent + Azure OpenAI<br><br>
        <strong>Role:</strong> User Feedback Processing<br><br>
        <strong>Agno Tools (1):</strong><br>
        1. `store_user_preference()` - Save corrections to RAG<br><br>
        <strong>UI Features:</strong><br>
        - Category dropdown (Custom/RAG/MCC/Default)<br>
        - Dynamic subcategory selection<br>
        - Custom input options<br>
        - Auto-saves to RAG system<br><br>
        <strong>Intelligence:</strong><br>
        - Interprets user feedback<br>
        - Updates classifications<br>
        - Maintains consistency<br>
        - Generates audit trails<br>
        - Automatically stores preferences via tool<br><br>
        <strong>Output:</strong><br>
        - Updated classification<br>
        - Adjusted confidence<br>
        - Feedback reasoning<br>
        - Audit documentation<br>
        - RAG preference storage (via tool)
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # RAG System and Custom Categories
    st.markdown("### RAG System & Custom Categories")
    
    col_rag1, col_rag2 = st.columns(2)
    
    with col_rag1:
        st.markdown("""
        #### 💾 User Preferences Store (RAG)
        
        **Location:** `utils/user_preferences.py`
        
        **Features:**
        - Similarity-based preference retrieval
        - Automatic learning from user corrections
        - JSON-based persistent storage
        - Merchant + description matching
        
        **Similarity Algorithm:**
        - Merchant name matching (70% weight)
        - Description word overlap (30% weight)
        - Threshold: 60% similarity
        
        **Storage Format:**
        ```json
        {
          "id": "merchant_hash",
          "merchant_name": "STARBUCKS",
          "user_category": "Shopping",
          "user_subcategory": "Retail",
          "original_category": "Food & Dining",
          "usage_count": 3,
          "created_at": "2024-01-01T00:00:00"
        }
        ```
        """)
    
    with col_rag2:
        st.markdown("""
        #### 📁 Custom Categories Manager
        
        **Location:** `utils/custom_categories.py`
        
        **Features:**
        - User-defined categories
        - Custom subcategories
        - GenAI matching
        - JSON-based storage
        
        **Usage:**
        - Define business-specific categories
        - Override default taxonomy
        - GenAI matches transactions to custom categories
        
        **Storage Format:**
        ```json
        {
          "categories": {
            "Business Expenses": [
              "Office Supplies",
              "Travel",
              "Meals"
            ]
          }
        }
        ```
        """)
    
    st.markdown("---")
    
    # Detailed implementation
    st.markdown("### 🛠️ Implementation Details")
    
    tab_impl1, tab_impl2, tab_impl3, tab_impl4 = st.tabs(["Preprocessing Agent", "Classification Agent", "Governance Agent", "Feedback Agent"])
    
    with tab_impl1:
        st.markdown("""
        #### Preprocessing Agent (agents/preprocessing_agent.py)
        
        **No LLM Required** - Pure Python implementation for speed and cost efficiency.
        
        **Key Methods:**
        - `_tokenize(text)` - Regex pattern `\\b\\w+\\b`
        - `_remove_noise(text)` - Removes 5 noise patterns (POS, PURCHASE, etc.)
        - `_normalize_text(text)` - Uppercase + special char removal
        - `_canonicalize_merchant(merchant)` - Maps to 9 canonical merchants
        - `_tokenize_sensitive_data()` - SHA-256 encryption
        
        **CMID Generation:**
        ```python
        canonical_name = self._canonicalize_merchant(merchant_text)
        cmid = hashlib.sha256(canonical_name.encode()).hexdigest()[:16]
        ```
        
        **Security:** All sensitive data encrypted with SHA-256 before storage.
        """)
        
        st.code("""
# Example preprocessing execution
preprocessor = PreprocessingAgent()
result = preprocessor.execute(
    description="STARBUCKS COFFEE #12345 PURCHASE",
    amount=5.50,
    merchant_name="Starbucks Corp",
    mcc_code="5812"
)

# Returns:
{
    'cmid': 'a1b2c3d4e5f6g7h8',  # SHA-256[:16]
    'encrypted_amount': 'sha256_hash...',
    'encrypted_mcc': 'sha256_hash...',
    'canonical_merchant': 'STARBUCKS',
    'cleaned_description': 'STARBUCKS COFFEE',
    'tokens': ['starbucks', 'coffee']
}
        """, language="python")
    
    with tab_impl2:
        st.markdown("""
        #### ClassificationAgent (agents/classification_agent.py)
        
        **RAG-Enhanced Classification with Priority Order**
        
        The ClassificationAgent implements a four-step priority-based classification system that learns from user feedback and supports custom taxonomies.
        
        **Initialization:**
        ```python
        ClassificationAgent(
            llm=AzureOpenAI(...),
            tools=[
                lookup_user_preference,      # RAG tool
                get_custom_categories,      # Custom categories
                match_to_custom_category,    # Custom category matching
                classify_by_mcc_code,       # MCC classification
                lookup_mcc_by_vendor,       # Vendor lookup
                vendor_database_search,     # Vendor database
                get_taxonomy_structure      # Default taxonomy
            ]
        )
        ```
        
        The agent initializes with:
        - UserPreferencesStore for RAG-based preference retrieval
        - CustomCategoriesManager for custom taxonomy support
        - Agno Agent with 4 tools for fallback classification
        
        **Execution Flow (execute method):**
        
        **Step 1: User Preferred Category (RAG)**
        - Calls `preferences_store.find_similar_preference(merchant_name, description, similarity_threshold=0.6)`
        - Similarity algorithm: Merchant name (70% weight) + Description word overlap (30% weight)
        - If match found (similarity ≥ 60%):
          - Returns immediately with user's preferred category/subcategory
          - Confidence: HIGH
          - Classification method: `user_preference_rag`
          - Includes similarity score and preference ID in response
        
        **Step 2: Custom Categories (GenAI)**
        - Checks if custom categories exist via `custom_categories_manager.get_categories()`
        - If custom categories exist:
          - Creates a separate Agno Agent for custom category matching
          - Builds prompt with custom category structure
          - Agent responds with MATCH: YES/NO_MATCH, CATEGORY, SUBCATEGORY, REASONING
          - If MATCH=YES and category is valid:
            - Returns with custom category/subcategory
            - Confidence: HIGH
            - Classification method: `custom_categories_genai`
          - If no match, continues to Step 3
        
        **Step 3: MCC Categorization**
        - If MCC code provided, sets classification_method to `mcc_categorization`
        - Builds prompt for Agno Agent with MCC code priority
        - Agent uses `classify_by_mcc_code` tool if MCC provided
        - Falls back to `lookup_mcc_by_vendor` for known brands
        - Confidence: HIGH
        
        **Step 4: GenAI LLM Categorization (Default)**
        - If no previous method matched, uses default Agno Agent classification
        - Classification method: `genai_llm_default`
        - Agent uses tools in priority order:
          1. `classify_by_mcc_code` (if MCC provided)
          2. `lookup_mcc_by_vendor` (for known brands)
          3. `vendor_database_search` (for merchant patterns)
          4. `get_taxonomy_structure` (for taxonomy reasoning)
        - Confidence: MEDIUM/LOW
        
        **Response Structure:**
        ```python
        {
            "category": str,
            "subcategory": str,
            "confidence": "high/medium/low",
            "reasoning": str,  # Combined reasoning from all steps
            "raw_response": str,
            "tool_calls": list,
            "agent_used": str,
            "classification_method": str,  # user_preference_rag, custom_categories_genai, mcc_categorization, genai_llm_default
            "user_preference_match": {  # Only if RAG match
                "similarity_score": float,
                "preference_id": str,
                "original_category": str,
                "original_subcategory": str
            },
            "metadata": {
                "merchant_analyzed": str,
                "amount_analyzed": float,
                "mcc_provided": bool,
                "user_preference_checked": bool,
                "custom_categories_checked": bool
            }
        }
        ```
        
        **RAG System Integration:**
        - **UserPreferencesStore:** JSON-based storage at `user_preferences.json`
        - **Similarity Algorithm:** 
          - Merchant name exact match: 1.0
          - Merchant name partial match: 0.8
          - Description word overlap: Jaccard similarity
          - Final score: (merchant_match * 0.7) + (desc_similarity * 0.3)
        - **Threshold:** 60% similarity required for match
        - **Auto-learning:** Preferences automatically saved when user corrects classifications
        
        **Custom Categories Integration:**
        - **CustomCategoriesManager:** JSON-based storage at `custom_categories.json`
        - **GenAI Matching:** Creates dedicated Agno Agent for custom category classification
        - **Prompt Format:** Includes custom category structure, transaction details, and matching instructions
        - **Response Parsing:** Extracts MATCH, CATEGORY, SUBCATEGORY, REASONING from agent response
        
        **Agno Tools Available:**
        1. `classify_by_mcc_code(mcc_code)` - 200+ MCC codes (ISO 18245)
        2. `lookup_mcc_by_vendor(merchant_name)` - 100+ known brands
        3. `vendor_database_search(query)` - 20 merchant patterns
        4. `get_taxonomy_structure()` - 12 default categories
        
        **Error Handling:**
        - If RAG search fails: Continues to next step
        - If custom category matching fails: Logs warning, continues to MCC
        - If Agno Agent fails: Returns fallback with "Other/General" category, LOW confidence
        """)
        
        st.code("""
# Actual implementation flow
classifier = ClassificationAgent(llm=azure_llm, tools=tools)

result = classifier.execute(
    merchant_name="STARBUCKS",
    description="Starbucks Coffee Shop",
    amount=5.50,
    mcc_code="5812",
    metadata={...}
)

# Internal execution:
# 1. preferences_store.find_similar_preference() → checks RAG
# 2. custom_categories_manager.get_categories() → checks custom
# 3. If custom exists: custom_agent.run(prompt) → GenAI match
# 4. If no match: agent.run(classification_prompt) → Agno tools
# 5. Returns structured result with classification_method
        """, language="python")
        
        st.markdown("""
        **Key Implementation Details:**
        
        - **Reasoning Accumulation:** The agent builds reasoning incrementally through each step, combining all reasoning parts into final response
        - **Method Tracking:** `classification_method` field indicates which path was taken
        - **Metadata Tracking:** Response includes flags showing which systems were checked
        - **Fallback Chain:** Each step gracefully falls back to next if no match found
        - **Dual Agent System:** Uses separate agent for custom categories vs. default classification
        """)
    
    with tab_impl3:
        st.markdown("""
        #### GovernanceAgent (agents/governance_agent.py)
        
        **Agno Agent Configuration:**
        ```python
        Agent(
            name="Transaction Governance Auditor",
            id="governance-agent",
            model=AzureOpenAI(id="gpt-5", temperature=1.0),
            tools=[assign_mcc_code_for_category]
        )
        ```
        
        **Validation Logic:**
        1. **Category Appropriateness:** Does the category make sense?
        2. **MCC Verification:** Is the MCC code correct for this category?
        3. **Confidence Review:** Should confidence be adjusted?
        4. **Compliance Checks:** Any red flags?
        
        **Audit Trail Generation:**
        - Validation status (APPROVED/FLAGGED)
        - Adjusted confidence
        - Final MCC code
        - Compliance flags
        - Detailed audit notes
        
        **MCC Assignment Tool:**
        - Reverse lookup: Category → MCC code
        - Handles missing MCC codes
        - Validates MCC-category alignment
        """)
        
        st.code("""
# Example governance execution
governance = GovernanceAgent(llm=azure_llm, tools=[assign_mcc_code_for_category])
result = governance.execute(
    merchant_name="STARBUCKS",
    description="Coffee Purchase",
    amount=5.50,
    category="Food & Dining",
    subcategory="Restaurant",
    confidence="high",
    reasoning="MCC code 5812 matches restaurant category"
)

# Agent validates and enhances:
{
    'validation_status': 'APPROVED',
    'adjusted_confidence': 95,
    'mcc_code': '5812',
    'flags': [],
    'audit_notes': 'Category-MCC alignment verified...'
}
        """, language="python")
    
    with tab_impl4:
        st.markdown("""
        #### FeedbackAgent (agents/feedback_agent.py)
        
        **Agno Agent Configuration:**
        ```python
        Agent(
            name="Feedback Processor",
            id="feedback-agent",
            model=AzureOpenAI(id="gpt-5", temperature=1.0),
            tools=[],  # Pure LLM reasoning, no tools needed
            instructions="Process user feedback and update classifications..."
        )
        ```
        
        **UI Features:**
        1. **Category Selection Dropdown:**
           - Shows all available categories from:
             - Custom categories
             - User preferences (RAG)
             - MCC codes
             - Default taxonomy
           - Option to enter custom category
        
        2. **Dynamic Subcategory Selection:**
           - Updates based on selected category
           - Shows available subcategories
           - Option to enter custom subcategory
        
        3. **Auto-Save to RAG:**
           - Automatically stores user corrections
           - Enables future similar transactions to use user preference
        
        **Feedback Processing Logic:**
        1. **Analyze Feedback:** Understand user intent and corrections
        2. **Update Classification:** Apply changes to category/subcategory
        3. **Maintain Consistency:** Ensure MCC code aligns with new category
        4. **Adjust Confidence:** Set to HIGH for user corrections
        5. **Generate Audit Trail:** Document all changes for compliance
        6. **Store in RAG:** Save preference for future similar transactions
        
        **Three Feedback Types:**
        - ✅ **Approval:** User validates classification (no changes)
        - ✏️ **Correction:** User provides correct category/subcategory (saved to RAG)
        - 💬 **Comment:** User shares observations (recorded for learning)
        
        **Intelligence Features:**
        - Interprets ambiguous user feedback
        - Maintains data consistency across fields
        - Generates detailed reasoning for changes
        - Creates compliance-ready audit documentation
        - Automatic RAG learning from corrections
        """)
        
        st.code("""
# Example feedback execution
feedback = FeedbackAgent(llm=azure_llm, tools=[store_user_preference])

# User corrects classification
result = feedback.execute(
    original_classification={
        'category': 'Shopping',
        'subcategory': 'Retail',
        'confidence': 'MEDIUM'
    },
    user_feedback="This is actually a restaurant, not retail",
    feedback_type="correction"
)

# Agent processes and updates:
{
    'updated': True,
    'category': 'Food & Dining',
    'subcategory': 'Restaurant',
    'confidence': 'HIGH',  # User correction = high confidence
    'mcc_code': '5812',    # Updated to match new category
    'feedback_applied': 'Updated category from Shopping to Food & Dining',
    'reasoning': 'User provided explicit correction with context',
    'audit_notes': 'User feedback: restaurant identification...',
    'original_category': 'Shopping',
    'original_subcategory': 'Retail'
}
        """, language="python")
        
        st.markdown("""
        **Benefits:**
        - 🎯 **Learning Loop:** Captures user corrections for model improvement
        - ✅ **Data Quality:** Enables real-time correction of misclassifications
        - 📊 **User Control:** Gives users power to fix AI mistakes
        - 📝 **Audit Trail:** Complete documentation of all changes
        - 🤖 **Intelligent:** AI interprets and applies feedback appropriately
        """)
    
    st.markdown("---")
    
    # Architecture diagram
    st.markdown("### 📊 Complete System Architecture")
    st.code("""
┌─────────────────────────────────────────────────────────────────┐
│                      Streamlit UI (app.py)                      │
│         Single Entry | Batch CSV | Architecture | Feedback      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              process_single_transaction() Orchestrator          │
│                  (Sequential Agent Pipeline)                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │      STEP 1: PreprocessingAgent         │
        │      Type: Deterministic (No LLM)       │
        │      Location: agents/preprocessing_agent.py │
        ├─────────────────────────────────────────┤
        │  Input: Raw transaction data            │
        │  • description, amount, merchant, MCC   │
        │                                         │
        │  Processing:                            │
        │  • Tokenization (regex)                 │
        │  • Noise removal (5 patterns)           │
        │  • Text normalization                   │
        │  • Merchant canonicalization (9 names)  │
        │  • CMID generation (SHA-256[:16])       │
        │  • Sensitive data encryption            │
        │                                         │
        │  Output: Clean, encrypted data          │
        │  • CMID, tokens, canonical_merchant     │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │  STEP 2: ClassificationAgent            │
        │  Type: Agno Agent + Azure OpenAI + RAG  │
        │  Location: agents/classification_agent.py │
        ├─────────────────────────────────────────┤
        │  Input: Preprocessed data + MCC         │
        │                                         │
        │  PRIORITY ORDER:                        │
        │  1. User Preference (RAG)               │
        │     - Similarity search (60% threshold) │
        │     - UserPreferencesStore              │
        │     - HIGH confidence                   │
        │                                         │
        │  2. Custom Categories (GenAI)           │
        │     - CustomCategoriesManager           │
        │     - GenAI matching                    │
        │     - HIGH confidence (if matched)      │
        │                                         │
        │  3. MCC Categorization                  │
        │     - classify_by_mcc_code()            │
        │     - 200+ MCC codes (ISO 18245)        │
        │     - HIGH confidence                   │
        │                                         │
        │  4. GenAI LLM (Default)                 │
        │     - lookup_mcc_by_vendor()            │
        │     - vendor_database_search()          │
        │     - get_taxonomy_structure()          │
        │     - MEDIUM/LOW confidence             │
        │                                         │
        │  Output: Category + Method + Confidence │
        │  • category, subcategory, reasoning      │
        │  • classification_method (tracking)     │
        │  • user_preference_match (if RAG)       │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │      STEP 3: GovernanceAgent            │
        │      Type: Agno Agent + Azure OpenAI    │
        │      Location: agents/governance_agent.py │
        ├─────────────────────────────────────────┤
        │  Input: Classification result           │
        │                                         │
        │  Agno Tools (1):                        │
        │  1. assign_mcc_code_for_category()      │
        │     - Reverse lookup (tools/mcc_codes.py) │
        │     - Category → MCC code               │
        │                                         │
        │  LLM Intelligence:                      │
        │  • Category validation                  │
        │  • MCC verification                     │
        │  • Confidence adjustment                │
        │  • Compliance checking                  │
        │  • Audit trail generation               │
        │                                         │
        │  Output: Validated result + Audit       │
        │  • validation_status, mcc_code, flags   │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │         Final Validated Result          │
        │  • Complete classification              │
        │  • MCC code assigned                    │
        │  • Confidence level                     │
        │  • Audit trail                          │
        │  • Compliance flags                     │
        └─────────────────────────────────────────┘
                              ↓
                    [User Reviews Result]
                              ↓
        ┌─────────────────────────────────────────┐
        │  STEP 4: FeedbackAgent         │
        │  Type: Agno Agent + Azure OpenAI        │
        │  Location: agents/feedback_agent.py     │
        ├─────────────────────────────────────────┤
        │  Input: User feedback + Original result │
        │                                         │
        │  UI Features:                           │
        │  • Category dropdown (all sources)     │
        │  • Dynamic subcategory selection        │
        │  • Custom input options                 │
        │                                         │
        │  Feedback Types:                        │
        │  • ✅ Approval (validates result)       │
        │  • ✏️ Correction (updates + saves RAG) │
        │  • 💬 Comment (records observation)    │
        │                                         │
        │  LLM Intelligence:                      │
        │  • Interprets user feedback             │
        │  • Updates classification intelligently │
        │  • Maintains MCC-category consistency   │
        │  • Adjusts confidence (HIGH for user)   │
        │  • Generates detailed audit notes       │
        │                                         │
        │  RAG Integration:                       │
        │  • Auto-saves corrections to RAG        │
        │  • UserPreferencesStore.add_preference()│
        │  • Enables future preference matching   │
        │                                         │
        │  Output: Updated result + Audit + RAG   │
        │  • updated classification (if changed)  │
        │  • feedback reasoning & audit trail     │
        │  • before/after comparison              │
        │  • preference stored in RAG system       │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │      Final Result with User Feedback    │
        │  • User-validated/corrected data        │
        │  • Complete feedback audit trail        │
        │  • Preference saved to RAG system       │
        │  • Learning data for future transactions│
        └─────────────────────────────────────────┘
    """, language="text")
    
    st.markdown("---")
    
    # Data flow example
    st.markdown("### 🔍 Real-World Example Flow")
    
    st.code("""
INPUT:
  Description: "STARBUCKS COFFEE #12345 PURCHASE 08/15"
  Amount: $5.50
  Merchant: "Starbucks Corp"
  MCC Code: "5812"

⬇️  STEP 1: PreprocessingAgent
  ✅ Tokenize: ['starbucks', 'coffee', '12345', 'purchase', '08', '15']
  ✅ Remove noise: ['starbucks', 'coffee']
  ✅ Normalize: "STARBUCKS COFFEE"
  ✅ Canonicalize: "STARBUCKS"
  ✅ CMID: "a1b2c3d4e5f6g7h8" (SHA-256[:16])
  ✅ Encrypt amount: "sha256_hash..."
  
  OUTPUT: {cmid: "a1b2...", canonical_merchant: "STARBUCKS", tokens: [...]}

⬇️  STEP 2: ClassificationAgent (Agno Agent)
  🤖 Agent receives preprocessed data + MCC "5812"
  🔧 Tool 1: classify_by_mcc_code("5812")
      → Returns: Food & Dining / Restaurant (HIGH confidence)
  💭 LLM reasons: "MCC 5812 is definitive for restaurants"
  
  OUTPUT: {category: "Food & Dining", subcategory: "Restaurant", 
           confidence: 95, reasoning: "MCC code match"}

⬇️  STEP 3: GovernanceAgent (Agno Agent)
  🤖 Agent validates classification
  🔧 Tool: assign_mcc_code_for_category("Food & Dining", "Restaurant")
      → Confirms MCC 5812 is correct
  💭 LLM validates: "Category-MCC alignment verified"
  ✅ No compliance issues
  
  OUTPUT: {validation_status: "APPROVED", mcc_code: "5812",
           adjusted_confidence: 95, flags: [], audit_notes: "..."}

FINAL RESULT (Presented to User):
  ✅ Category: Food & Dining / Restaurant
  ✅ MCC Code: 5812
  ✅ Confidence: 95%
  ✅ Validation: APPROVED
  ✅ CMID: a1b2c3d4e5f6g7h8

⬇️  [User Reviews & Provides Feedback]
  User Action: Clicks "👍 Looks Good!" (Approval)

⬇️  STEP 4: FeedbackAgent (Agno Agent)
  🤖 Agent processes approval feedback
  💭 LLM analyzes: "User confirmed classification is correct"
  📝 Generates audit: "User validation recorded at [timestamp]"
  ✅ No changes needed (approval only)
  
  OUTPUT: {updated: false, feedback_applied: "User approved",
           audit_notes: "Classification validated by user"}

ALTERNATIVE: User Correction Example
  User Action: Corrects to "Transportation / Gas Station"
  
⬇️  STEP 4: FeedbackAgent (Agno Agent)
  🤖 Agent processes correction
  💭 LLM reasons: "User provided explicit correction"
  🔄 Updates: Category → "Transportation", Subcategory → "Gas Station"
  🏷️ Updates MCC: 5812 → 5541 (maintains consistency)
  📈 Adjusts confidence: 95% → HIGH (user correction)
  📝 Audit: "User correction applied: restaurant→gas station"
  
  OUTPUT: {updated: true, category: "Transportation",
           subcategory: "Gas Station", mcc_code: "5541",
           confidence: "HIGH", reasoning: "User provided explicit correction",
           audit_notes: "Original: Food & Dining/Restaurant. Updated per user feedback."}

FINAL RESULT WITH FEEDBACK:
  ✅ Updated classification OR validated original
  ✅ Complete audit trail of user interaction
  ✅ Learning data captured for model improvement
    """, language="text")
    
    st.markdown("---")
    
    # Technical specifications
    st.markdown("### ⚙️ Technical Specifications")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Framework & Tools:**
        - Agno 2.2.13
        - Azure OpenAI gpt-5
        - Streamlit 1.51.0
        - Python 3.13+
        - pandas for batch processing
        
        **Security:**
        - SHA-256 encryption
        - CMID for merchant deduplication
        - Sensitive data tokenization
        - No PII stored in plain text
        """)
    
    with col2:
        st.markdown("""
        **Performance:**
        - PreprocessingAgent: <100ms (no LLM)
        - ClassificationAgent: 1-3s (Azure OpenAI)
        - GovernanceAgent: 1-2s (Azure OpenAI)
        - Total: ~2-5s per transaction
        
        **Data Coverage:**
        - 200+ MCC codes (ISO 18245 standard)
        - 100+ known brand vendors
        - 20 merchant pattern matchers
        - 12 transaction categories
        - Instant brand recognition
        
        **Scalability:**
        - Batch processing supported (CSV upload)
        - Cached agent instances
        - Parallel-ready architecture
        """)
    
    st.markdown("---")
    
    st.markdown("### 📁 Project Structure")
    st.code("""
classify-with-agno/
├── app.py                          # Main Streamlit UI
├── .env                            # Azure OpenAI credentials
├── requirements.txt                # Dependencies
│
├── agents/
│   ├── preprocessing_agent.py      # PreprocessingAgent (no LLM)
│   ├── classification_agent.py     # ClassificationAgent (Agno)
│   └── governance_agent.py         # GovernanceAgent (Agno)
│
├── tools/
│   ├── mcc_codes.py                # 200+ MCC codes, 100+ vendors, 3 tools
│   ├── vendor_database.py          # 20 merchant patterns, 1 tool
│   └── taxonomy.py                 # 12 categories, 1 tool
│
└── utils/
    ├── parsers.py                  # JSON extraction
    └── validators.py               # Data validation
    """, language="text")
    
    st.success("""
    ✅ **System Status:** Fully Implemented & Production-Ready
    
    All three agents are operational with Agno framework integration,
    Azure OpenAI connectivity, and complete tool implementations.
    """)
