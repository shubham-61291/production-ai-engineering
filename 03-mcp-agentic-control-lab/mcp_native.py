#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP-Native RAG (Agent-Tool Orchestrated Control)
-------------------------------------------------
Control Flow: User -> Agent (LLM) -> Tool Invocation -> Context/Outcome -> Agent -> UI
Authority Location: MCP Tool Layer
"""

import json
import gradio as gr
import config
from core.document_parser import extract_text_from_file, chunk_text
from core.vector_store import get_vector_store
from mcp_core.agent import MCPAgent

agent = MCPAgent()
vector_store = get_vector_store()

def ingest_uploaded_file(file_obj):
    if file_obj is None:
        return "[WARNING] No file uploaded."
    try:
        raw_text = extract_text_from_file(file_obj.name, file_obj.name)
        chunks = chunk_text(raw_text)
        if not chunks:
            return "[WARNING] Document contains no extractable text."
        count = vector_store.upsert(texts=chunks)
        return f"[SUCCESS] Ingested {count} document chunks into vector store."
    except Exception as e:
        return f"[ERROR] Ingestion Error: {str(e)}"

def run_agent_chat(email, question):
    res = agent.chat(email=email, user_input=question)
    answer = res.get("answer", "")
    trace_str = json.dumps(res.get("tool_calls", []), indent=2)
    return answer, trace_str

def run_tool_policy_update(email, text_snippet):
    res = agent.execute_policy_update_tool(email=email, policy_text=text_snippet)
    return res.get("message", ""), json.dumps(res.get("tool_response", {}), indent=2)

def view_audit_logs():
    logs = agent.tool_server.get_audit_logs()
    return json.dumps(logs, indent=2)

def build_ui():
    with gr.Blocks(theme=gr.themes.Soft(), title="MCP-Native RAG Control Lab") as demo:
        gr.Markdown("# [MCP-Native RAG Control Lab]")
        gr.Markdown(
            "**Architecture**: Agent -> Tool -> Context Control.\n"
            "Authority & role permissions are enforced **inside MCP Tools**.\n"
            f"- **Admin Email**: `{config.ADMIN_EMAIL}` | **User Email**: `{config.USER_EMAIL}`"
        )

        with gr.Tab("Document Ingestion"):
            file_input = gr.File(label="Upload Policy Document (PDF, DOCX, TXT)")
            ingest_btn = gr.Button("Push Document to RAG Memory", variant="primary")
            ingest_status = gr.Textbox(label="Ingestion Outcome", interactive=False)
            ingest_btn.click(ingest_uploaded_file, inputs=[file_input], outputs=[ingest_status])

        with gr.Tab("MCP Agent Assistant"):
            with gr.Row():
                e_in = gr.Textbox(label="Registered Identity Email", value=config.USER_EMAIL, placeholder="abc@gmail.com")
                q_in = gr.Textbox(label="Question", placeholder="What is the policy regarding remote working?")
            ans_out = gr.Textbox(label="Agent Response (Document-Grounded)", lines=6)
            tool_trace = gr.Code(label="MCP Tool Execution Trace", language="json")
            btn_ask = gr.Button("Submit Request to Agent", variant="primary")

            btn_ask.click(run_agent_chat, inputs=[e_in, q_in], outputs=[ans_out, tool_trace])

        with gr.Tab("Tool-Enforced Policy Injection"):
            gr.Markdown("### Tool-Level Security Enforcement Proof")
            adm_email = gr.Textbox(label="Caller Identity Email", value=config.ADMIN_EMAIL, placeholder="xyz@gmail.com")
            upd_text = gr.Textbox(label="New Policy Snippet", lines=4, placeholder="Admin Injection: All system updates require 2FA approval.")
            upd_status = gr.Textbox(label="Tool Output", interactive=False)
            tool_res_json = gr.Code(label="Raw Tool Response JSON", language="json")
            btn_upd = gr.Button("Execute Policy Update Tool", variant="secondary")

            btn_upd.click(run_tool_policy_update, inputs=[adm_email, upd_text], outputs=[upd_status, tool_res_json])

        with gr.Tab("MCP Audit Logs"):
            log_btn = gr.Button("Refresh Tool Audit Log")
            log_display = gr.Code(label="Tool Security Audit Log History", language="json")
            log_btn.click(view_audit_logs, inputs=[], outputs=[log_display])

    return demo

if __name__ == "__main__":
    app = build_ui()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)
