import json
import time
from typing import Dict, Any, List
from core.auth import authenticate_user
from core.llm_brain import get_llm_brain
from mcp_core.tools import MCPToolServer

class MCPAgent:
    """Pure MCP Agent Architecture
    
    Control Flow:
    User -> Agent (LLM) -> MCP Tool Invocation (Auth Check Inside Tool) -> Context -> Agent -> UI Output
    """

    def __init__(self):
        self.tool_server = MCPToolServer()
        self.llm = get_llm_brain()
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}

    def chat(self, email: str, user_input: str) -> Dict[str, Any]:
        start_time = time.time()
        identity = authenticate_user(email)

        if not identity.is_authenticated():
            return {
                "success": False,
                "answer": "Access Denied: Please provide a registered official email ID to proceed.",
                "tool_calls": [],
                "audit_status": "DENIED_IDENTITY",
                "latency_sec": round(time.time() - start_time, 3)
            }

        email_key = identity.email
        if email_key not in self.conversation_history:
            self.conversation_history[email_key] = []

        # 1. Agent calls retrieve_policy_context tool
        tool_response_str = self.tool_server.call_tool(
            tool_name="retrieve_policy_context",
            arguments={"query": user_input},
            email=email_key
        )
        tool_data = json.loads(tool_response_str)
        context_matches = tool_data.get("context", [])

        # Log trace
        self.conversation_history[email_key].append({"role": "user", "content": user_input})
        self.conversation_history[email_key].append({"role": "tool", "content": tool_response_str})

        if not context_matches:
            fallback_ans = "No relevant policy found. Could you clarify the specific system or rule you are asking about?"
            self.conversation_history[email_key].append({"role": "assistant", "content": fallback_ans})
            return {
                "success": True,
                "answer": fallback_ans,
                "tool_calls": [{"tool": "retrieve_policy_context", "response": tool_data}],
                "audit_status": "ALLOWED_EMPTY_RETRIEVAL",
                "latency_sec": round(time.time() - start_time, 3)
            }

        # 2. Agent receives tool context and synthesizes document-grounded response
        context_ranking = "\n\n".join(
            [f"Source {i+1} [Relevance: {c['score']}]: {c['text']}" for i, c in enumerate(context_matches)]
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an enterprise MCP Policy Assistant. "
                    "Use the provided tool context sources ONLY to answer the user's question. "
                    "Do NOT hallucinate or use external assumptions. If information is missing, state so clearly. "
                    "Keep answers concise (maximum 5 lines)."
                )
            },
            {
                "role": "user",
                "content": f"MCP TOOL CONTEXT:\n{context_ranking}\n\nQUESTION: {user_input}"
            }
        ]

        answer = self.llm.generate_completion(messages=messages, temperature=0.1)
        self.conversation_history[email_key].append({"role": "assistant", "content": answer})

        return {
            "success": True,
            "answer": answer,
            "tool_calls": [{"tool": "retrieve_policy_context", "response": tool_data}],
            "audit_status": "ALLOWED_SUCCESS",
            "latency_sec": round(time.time() - start_time, 3)
        }

    def execute_policy_update_tool(self, email: str, policy_text: str) -> Dict[str, Any]:
        """Invoke update_policy_context tool with tool-level authorization enforcement."""
        start_time = time.time()
        tool_response_str = self.tool_server.call_tool(
            tool_name="update_policy_context",
            arguments={"text": policy_text},
            email=email
        )
        tool_data = json.loads(tool_response_str)

        return {
            "success": tool_data.get("status") == "SUCCESS",
            "message": tool_data.get("message") or tool_data.get("error", "Unknown error"),
            "tool_response": tool_data,
            "latency_sec": round(time.time() - start_time, 3)
        }
