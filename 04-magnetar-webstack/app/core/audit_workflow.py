import asyncio
import logging
import re
import json
from typing import List, TypedDict
from langchain_ollama import ChatOllama
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from app.core.config import settings
from app.models.schemas import AuditReport, Reflection

logger = logging.getLogger(__name__)

def strip_think_tags(text: str) -> str:
    """Strips <think>...</think> reasoning blocks emitted by DeepSeek-R1 models."""
    if not isinstance(text, str):
        return ""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    # Extract json block if present in markdown code fences
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if json_match:
        return json_match.group(1).strip()
    return cleaned

class AgentState(TypedDict):
    contract_text: str
    junior_report: AuditReport
    reflection: Reflection
    evidence: str
    final_report: AuditReport

llm = ChatOllama(model=settings.OLLAMA_MODEL, base_url=settings.OLLAMA_URL, temperature=0.0)

junior_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI Legal Auditor specialized in EU Tech Regulation (GDPR & AI Act).

Your Task: Review the provided contract text.

STRICT RULES:
1. Look for violations of GDPR (e.g., Article 33 Breach Notification, Article 5 Storage Limitation).
2. Look for violations of the EU AI Act (e.g., prohibited practices, transparency).
3. Look for "Commercial Traps" (e.g., weak liability caps, weird audit restrictions).
4. Be PARANOID. If a clause looks vague ("commercially reasonable"), flag it as a risk.
5. Return ONLY a JSON object matching the requested schema. Do not output raw thinking tags if possible."""),
    ("human", "{contract_text}")
])

junior_chain = junior_prompt | llm.with_structured_output(AuditReport)

reflector_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a Senior Legal Researcher.

Your Task: Validate the 'Junior Auditor's' findings.
1. Identify any claims that lack specific Article numbers (e.g., "Violates GDPR").
2. Identify vaguely cited risks.
3. Generate search queries to find the OFFICIAL source text (e.g., "GDPR Article 33 time limit text")."""),
    ("human", "{audit_report}")
])

reflector_chain = reflector_prompt | llm.with_structured_output(Reflection)

def run_legal_research(queries: List[str]) -> str:
    if not settings.TAVILY_API_KEY:
        logger.warning("TAVILY_API_KEY not set; research will be empty.")
        return "No research performed (missing API key)."
    try:
        tavily = TavilySearchResults(max_results=3, tavily_api_key=settings.TAVILY_API_KEY)
        research_summary = ""
        for query in (queries or []):
            try:
                results = tavily.invoke(query)
                for result in results:
                    research_summary += f"SOURCE: {result.get('url', '')}\nCONTENT: {result.get('content', '')}\n\n"
            except Exception as e:
                logger.error(f"Error searching '{query}': {e}")
        return research_summary or "No evidence retrieved."
    except Exception as err:
        logger.error(f"Failed to initialize Tavily tool: {err}")
        return "Legal research unavailable."

revisor_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a Senior Partner at a Top Law Firm.

Your Task: Finalize the Legal Audit Report.

Inputs:
1. DRAFT REPORT (from Junior Associate) - May contain errors.
2. LEGAL EVIDENCE (from Research) - The truth.

Instructions:
- If the Evidence contradicts the Draft, OVERRIDE the Draft.
- Specifically, if the Draft says "10 days" but Evidence says "72 hours", you must flag it as a Critical Violation with the correct citation.
- Add the specific URL/Citation from the Evidence to the report.
- Keep the language professional, authoritative, and concise."""),
    ("human", "DRAFT REPORT:\n{draft_report}\n\nLEGAL EVIDENCE:\n{evidence}")
])

revisor_chain = revisor_prompt | llm.with_structured_output(AuditReport)

def run_junior_node(state: AgentState):
    logger.info("Junior Auditor running...")
    try:
        report = junior_chain.invoke({"contract_text": state["contract_text"]})
    except Exception as e:
        logger.warning(f"Structured output parse attempt failed ({e}); attempting raw invoke with clean parser...")
        raw_msg = (junior_prompt | llm).invoke({"contract_text": state["contract_text"]})
        cleaned_json = strip_think_tags(str(raw_msg.content))
        data = json.loads(cleaned_json)
        report = AuditReport(**data)
    return {"junior_report": report}

def run_reflector_node(state: AgentState):
    logger.info("Reflector running...")
    report_str = state["junior_report"].model_dump_json()
    try:
        reflection = reflector_chain.invoke({"audit_report": report_str})
    except Exception as e:
        logger.warning(f"Reflector parse fallback engaged: {e}")
        raw_msg = (reflector_prompt | llm).invoke({"audit_report": report_str})
        cleaned_json = strip_think_tags(str(raw_msg.content))
        data = json.loads(cleaned_json)
        reflection = Reflection(**data)
    return {"reflection": reflection}

def run_researcher_node(state: AgentState):
    logger.info("Researcher running...")
    queries = state.get("reflection", {}).search_queries if state.get("reflection") else []
    evidence = run_legal_research((queries or [])[:3])
    return {"evidence": evidence}

def run_revisor_node(state: AgentState):
    logger.info("Revisor (Senior Partner) running...")
    draft_json = state["junior_report"].model_dump_json()
    evidence_str = state.get("evidence", "")
    try:
        final_report = revisor_chain.invoke({
            "draft_report": draft_json,
            "evidence": evidence_str
        })
    except Exception as e:
        logger.warning(f"Revisor parse fallback engaged: {e}")
        raw_msg = (revisor_prompt | llm).invoke({
            "draft_report": draft_json,
            "evidence": evidence_str
        })
        cleaned_json = strip_think_tags(str(raw_msg.content))
        data = json.loads(cleaned_json)
        final_report = AuditReport(**data)
    return {"final_report": final_report}

workflow = StateGraph(AgentState)
workflow.add_node("junior", run_junior_node)
workflow.add_node("reflector", run_reflector_node)
workflow.add_node("researcher", run_researcher_node)
workflow.add_node("revisor", run_revisor_node)

workflow.set_entry_point("junior")
workflow.add_edge("junior", "reflector")
workflow.add_edge("reflector", "researcher")
workflow.add_edge("researcher", "revisor")
workflow.add_edge("revisor", END)

magnetar_app = workflow.compile()

async def run_audit_workflow(contract_text: str) -> AuditReport:
    def _run():
        final_state = magnetar_app.invoke({"contract_text": contract_text})
        return final_state["final_report"]
    return await asyncio.to_thread(_run)
