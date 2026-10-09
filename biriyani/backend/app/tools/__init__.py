"""Agent tools module for Multi-Agent AI Assistant."""

from app.tools.registry import tool_registry
from app.tools.schemas import (
    RAGSearchInput,
    WebSearchInput,
    DataAnalysisInput,
    SearchUsersInput,
    EmptyInput,
)
from app.tools.rag_retriever import retrieve_document_chunks
from app.tools.user_tools import tool_get_my_profile, tool_get_my_subscription, tool_get_my_usage
from app.tools.web_search import search_web
from app.tools.data_sandbox import calculate_data_metrics
from app.tools.crm_tools import tool_get_admin_analytics, tool_search_users
from app.models.document import Document
from app.models.user import User
from sqlalchemy.orm import Session


# 1. RAG Search Tool (USER)
@tool_registry.register(
    name="rag_search",
    description="Retrieve grounded, user-isolated document chunks from uploaded conversation files.",
    permission="USER",
    read_only=True,
    input_schema=RAGSearchInput,
)
def rag_search(db: Session, current_user: User, query: str, top_k: int = 5) -> dict:
    # Retrieve user's conversation documents
    docs = (
        db.query(Document)
        .join(Document.conversation)
        .filter(Document.conversation.has(user_id=current_user.id))
        .all()
    )
    chunks = retrieve_document_chunks(query, docs, top_k=top_k)
    return {
        "query": query,
        "chunks_retrieved": len(chunks),
        "chunks": chunks,
    }


# 2. Get My Profile Tool (USER)
@tool_registry.register(
    name="get_my_profile",
    description="Fetch current user's profile details (id, name, email, role, status).",
    permission="USER",
    read_only=True,
    input_schema=EmptyInput,
)
def get_my_profile(db: Session, current_user: User) -> dict:
    return tool_get_my_profile(db, current_user)


# 3. Get My Subscription Tool (USER)
@tool_registry.register(
    name="get_my_subscription",
    description="Fetch current user's active subscription tier, plan status, and feature limits.",
    permission="USER",
    read_only=True,
    input_schema=EmptyInput,
)
def get_my_subscription(db: Session, current_user: User) -> dict:
    return tool_get_my_subscription(db, current_user)


# 4. Get My Usage Tool (USER)
@tool_registry.register(
    name="get_my_usage",
    description="Fetch current user's usage metrics (total conversations and documents count).",
    permission="USER",
    read_only=True,
    input_schema=EmptyInput,
)
def get_my_usage(db: Session, current_user: User) -> dict:
    return tool_get_my_usage(db, current_user)


# 5. Web Search Tool (USER)
@tool_registry.register(
    name="web_search",
    description="Search public web intelligence for current framework documentation, benchmarks, and trends.",
    permission="USER",
    read_only=True,
    input_schema=WebSearchInput,
)
def web_search_tool(query: str, max_results: int = 5) -> dict:
    results = search_web(query, max_results=max_results)
    return {
        "query": query,
        "count": len(results),
        "results": results,
    }


# 6. Data Analysis Tool (USER)
@tool_registry.register(
    name="analyze_data",
    description="Inspect tabular CSV data or numerical expressions and return structured summary metrics.",
    permission="USER",
    read_only=True,
    input_schema=DataAnalysisInput,
)
def analyze_data_tool(data_or_text: str) -> dict:
    return calculate_data_metrics(data_or_text)


# 7. Get Admin Analytics Tool (ADMIN ONLY)
@tool_registry.register(
    name="get_admin_analytics",
    description="Retrieve executive system analytics (Requires ADMIN role).",
    permission="ADMIN",
    read_only=True,
    input_schema=EmptyInput,
)
def get_admin_analytics_tool(db: Session, current_user: User) -> dict:
    return tool_get_admin_analytics(db, current_user)


# 8. Search Admin Users Tool (ADMIN ONLY)
@tool_registry.register(
    name="search_admin_users",
    description="Search registered system users by name, email, or role (Requires ADMIN role).",
    permission="ADMIN",
    read_only=True,
    input_schema=SearchUsersInput,
)
def search_admin_users_tool(
    db: Session,
    current_user: User,
    query: str | None = None,
    role: str | None = None,
    limit: int = 10,
) -> dict:
    return tool_search_users(db, current_user, query=query, role=role, limit=limit)
