#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP-AGENTIC-CONTROL-LAB: Pure MCP-Native Control Center
--------------------------------------------------------
Model Context Protocol (MCP) Agent -> Tool -> Context Control Architecture
"""

import json
import gradio as gr
import config
from core.document_parser import extract_text_from_file, chunk_text
from core.vector_store import get_vector_store
from mcp_core.agent import MCPAgent

mcp_agent = MCPAgent()
vector_store = get_vector_store()

def handle_document_ingestion(file_obj):
    if file_obj is None:
        return "[WARNING] Please select a document file to upload."
    try:
        raw_text = extract_text_from_file(file_obj.name, file_obj.name)
        chunks = chunk_text(raw_text)
        if not chunks:
            return "[WARNING] File contained no extractable text."
        count = vector_store.upsert(texts=chunks)
        return f"[SUCCESS] Ingested {count} document chunks into RAG memory."
    except Exception as e:
        return f"[ERROR] Ingestion Error: {str(e)}"

def handle_agent_chat(email, query):
    res = mcp_agent.chat(email=email, user_input=query)
    return (
        res.get("answer", ""),
        json.dumps(res.get("tool_calls", []), indent=2)
    )

def handle_policy_update(email, snippet):
    res = mcp_agent.execute_policy_update_tool(email=email, policy_text=snippet)
    return res.get("message", ""), json.dumps(res.get("tool_response", {}), indent=2)

def fetch_tool_audit_logs():
    return json.dumps(mcp_agent.tool_server.get_audit_logs(), indent=2)

def build_app():
    theme = gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="slate"
    )

    with gr.Blocks(theme=theme, title="🛡️ MCP-AGENTIC-CONTROL-LAB") as demo:
        gr.Markdown(
            "# 🛡️ MCP-AGENTIC-CONTROL-LAB\n"
            "### Pure MCP-Native Control (Agent → Tool → Context Architecture)\n"
            f"**AI Brain Base URL**: `{config.AI_BRAIN_BASE_URL}` | **Model**: `{config.AI_BRAIN_MODEL}`"
        )

        with gr.Accordion("📂 Policy Document Ingestion Pipeline", open=True):
            file_in = gr.File(label="Upload Policy Document (.pdf, .docx, .txt)")
            ingest_btn = gr.Button("Ingest Document into Memory", variant="primary")
            ingest_out = gr.Textbox(label="Ingestion Result Status", interactive=False)
            ingest_btn.click(handle_document_ingestion, inputs=[file_in], outputs=[ingest_out])

        with gr.Tabs():
            # ---------------- TAB 1: MCP AGENT ASSISTANT ----------------
            with gr.Tab("💬 MCP Policy Assistant"):
                gr.Markdown(
                    "### Agent-Tool Interaction\n"
                    "The Agent calls `retrieve_policy_context` tool to retrieve document context, "
                    "reason over tool outputs, and synthesize strict non-hallucinated answers."
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        user_email = gr.Textbox(label="Identity Email Context", value=config.USER_EMAIL)
                        user_q = gr.Textbox(label="Policy Question", placeholder="What is the policy regarding travel expenses?")
                        ask_btn = gr.Button("Ask MCP Agent", variant="primary")

                    with gr.Column(scale=1):
                        agent_ans = gr.Textbox(label="Agent Response (Document-Grounded)", lines=6)
                        tool_trace = gr.Code(label="MCP Tool Execution Trace JSON", language="json")

                ask_btn.click(handle_agent_chat, inputs=[user_email, user_q], outputs=[agent_ans, tool_trace])

            # ---------------- TAB 2: TOOL-ENFORCED POLICY UPDATES ----------------
            with gr.Tab("⚡ Tool-Enforced Policy Injection"):
                gr.Markdown(
                    "### Tool-Level RBAC Security Proof\n"
                    "Authority & write access are checked **inside the `update_policy_context` tool**. "
                    "Attempts by unauthorized roles (`USER`) are blocked directly at the tool boundary."
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        caller_email = gr.Textbox(label="Caller Email Identity", value=config.ADMIN_EMAIL, placeholder="xyz@gmail.com")
                        policy_snippet = gr.Textbox(label="New Policy Text Snippet", lines=4, placeholder="Admin update: Remote work budget cap is $500 per annum.")
                        upd_btn = gr.Button("Execute Policy Update Tool", variant="secondary")

                    with gr.Column(scale=1):
                        upd_status = gr.Textbox(label="Tool Status Message", interactive=False)
                        upd_json = gr.Code(label="Tool Return Payload JSON", language="json")

                upd_btn.click(handle_policy_update, inputs=[caller_email, policy_snippet], outputs=[upd_status, upd_json])

            # ---------------- TAB 3: MCP AUDIT LOGS ----------------
            with gr.Tab("🔍 MCP Tool Audit History"):
                gr.Markdown("### Audit Trail at MCP Tool Execution Boundary")
                refresh_btn = gr.Button("Refresh Audit Logs")
                audit_logs_code = gr.Code(label="Tool Audit History Log", language="json")
                refresh_btn.click(fetch_tool_audit_logs, inputs=[], outputs=[audit_logs_code])

    return demo

if __name__ == "__main__":
    app = build_app()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)
