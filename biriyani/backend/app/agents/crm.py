import re
from typing import Any
from sqlalchemy.orm import Session

from app.agents.state import AgentState
from app.models.user import User
from app.tools.crm_tools import (
    tool_search_customer,
    tool_get_customer_details,
    tool_get_customer_deals,
    tool_get_top_customers,
    tool_get_recent_activities,
    tool_search_deals,
    tool_customer_summary,
    tool_get_pipeline_summary,
)


class CRMAgent:
    """
    CRM Agent:
    - Parses natural-language intent for CRM data
    - Selects controlled CRM tools safely
    - Executes database tools through CRMService
    - Populates state["crm_results"] with structured CRM data
    """

    def run(self, state: AgentState, db: Session, current_user: User) -> dict[str, Any]:
        query = state.get("user_query", "").strip()
        q_lower = query.lower()

        # Extract target customer name heuristics if present (e.g. "ABC Ltd", "Apex Global", "TechCorp")
        cust_match = None
        for known_name in ["abc ltd", "apex global", "techcorp", "biriyani palace", "nexus systems", "vortex logistics", "zenith analytics"]:
            if known_name in q_lower:
                cust_match = known_name.title() if known_name != "abc ltd" else "ABC Ltd"
                break
        
        if not cust_match:
            # Fallback regex for "customer X" or "for X"
            m = re.search(r'(?:customer|company|for)\s+([A-Za-z0-9\s]+?)(?:\'?s|\s+open|\s+deals|\s+activities|\?|\.|$)', query, re.IGNORECASE)
            if m:
                extracted = m.group(1).strip()
                if extracted.lower() not in ["the", "top", "all", "our", "recent", "my"]:
                    cust_match = extracted

        tool_used = ""
        results = {}

        # Intent heuristic mapping for CRM queries
        if any(w in q_lower for w in ["pipeline", "total pipeline", "sales pipeline", "pipeline summary", "open pipeline"]):
            tool_used = "get_pipeline_summary"
            results = tool_get_pipeline_summary(db, current_user)

        elif "top" in q_lower and ("customer" in q_lower or "deal" in q_lower):
            limit = 5
            if "top 1" in q_lower or "highest deal" in q_lower or "highest value" in q_lower:
                limit = 1
            elif "top 10" in q_lower:
                limit = 10
            tool_used = "get_top_customers"
            results = tool_get_top_customers(db, current_user, limit=limit)

        elif "highest" in q_lower and ("customer" in q_lower or "deal" in q_lower):
            tool_used = "get_top_customers"
            results = tool_get_top_customers(db, current_user, limit=1)

        elif cust_match and any(w in q_lower for w in ["open deal", "deals"]):
            tool_used = "get_customer_deals"
            results = tool_get_customer_deals(db, current_user, customer_id=cust_match, status="open")

        elif cust_match and any(w in q_lower for w in ["activity", "activities", "recent activit"]):
            tool_used = "get_recent_activities"
            results = tool_get_recent_activities(db, current_user, customer_id=cust_match)

        elif cust_match and any(w in q_lower for w in ["info", "information", "summary", "about", "detail", "profile"]):
            tool_used = "customer_summary"
            results = tool_customer_summary(db, current_user, customer_id=cust_match)

        elif cust_match and ("find" in q_lower or "search" in q_lower or "show" in q_lower):
            tool_used = "search_customer"
            results = tool_search_customer(db, current_user, query=cust_match)

        elif "deal" in q_lower and ("closing" in q_lower or "this month" in q_lower or "close" in q_lower):
            tool_used = "search_deals"
            results = tool_search_deals(db, current_user, status="open")

        elif "open deal" in q_lower or "how many deal" in q_lower:
            tool_used = "search_deals"
            results = tool_search_deals(db, current_user, status="open")

        elif cust_match:
            tool_used = "get_customer_details"
            res = tool_get_customer_details(db, current_user, customer_id=cust_match)
            results = res if res else tool_search_customer(db, current_user, query=cust_match)

        else:
            tool_used = "get_pipeline_summary"
            results = tool_get_pipeline_summary(db, current_user)

        return {
            "crm_tool": tool_used,
            "crm_results": results,
            "agent_trace": state.get("agent_trace", []) + [{
                "agent": "CRM Agent",
                "action": f"Executed tool `{tool_used}`",
            }],
        }
