import json
import time
from typing import Dict, Any, List
from core.auth import authenticate_user
from core.vector_store import get_vector_store

class MCPToolServer:
    """MCP Tool Server with Tool-Level Security & Auditing.
    
    In a pure Model Context Protocol (MCP) architecture, authority and 
    access boundaries are enforced inside Tool execution contracts.
    """

    def __init__(self):
        self.vector_store = get_vector_store()
        self.audit_log: List[Dict[str, Any]] = []

    def call_tool(self, tool_name: str, arguments: Dict[str, Any], email: str) -> str:
        identity = authenticate_user(email)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        if tool_name == "retrieve_policy_context":
            query = arguments.get("query", "")
            result = self.vector_store.query(query_text=query, top_k=3, min_score=0.45)
            self.audit_log.append({
                "timestamp": timestamp,
                "email": email,
                "role": identity.role.value,
                "tool": tool_name,
                "status": "SUCCESS",
                "details": f"Retrieved {len(result)} context chunks for query: '{query}'"
            })
            return json.dumps({"status": "SUCCESS", "context": result})

        elif tool_name == "update_policy_context":
            # Tool-level Authorization Enforcement
            if not identity.can_update_policy():
                err_msg = "[UNAUTHORIZED] Authorization Failure: Admin permissions required to execute policy update."
                self.audit_log.append({
                    "timestamp": timestamp,
                    "email": email,
                    "role": identity.role.value,
                    "tool": tool_name,
                    "status": "BLOCKED",
                    "details": "Unauthorized write attempt"
                })
                return json.dumps({"status": "UNAUTHORIZED", "error": err_msg})

            text = arguments.get("text", "").strip()
            if len(text) < 10:
                return json.dumps({"status": "ERROR", "error": "[ERROR] Error: Policy snippet text too short."})

            inserted_count = self.vector_store.upsert(texts=[text])
            success_msg = f"[SUCCESS] {inserted_count} policy snippet(s) injected into RAG memory."
            self.audit_log.append({
                "timestamp": timestamp,
                "email": email,
                "role": identity.role.value,
                "tool": tool_name,
                "status": "SUCCESS",
                "details": "Policy context injected into vector store"
            })
            return json.dumps({"status": "SUCCESS", "message": success_msg})

        return json.dumps({"status": "ERROR", "error": f"[ERROR] Unknown tool '{tool_name}'."})

    def get_audit_logs(self) -> List[Dict[str, Any]]:
        return self.audit_log
