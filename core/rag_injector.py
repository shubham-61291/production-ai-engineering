import json
from typing import List
from config import DEFAULT_EMBED_MODEL, DEFAULT_OLLAMA_MODEL

def inject_brand_header(base_html: str) -> str:
    header = """
<!-- AETHERIS Brand Banner -->
<div style="background:linear-gradient(90deg, #090d16 0%, #1e1b4b 100%);color:#f8fafc;padding:10px 24px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,0.1);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:14px;">
  <div style="display:flex;align-items:center;gap:10px;">
    <span style="background:#6366f1;color:#fff;padding:2px 8px;border-radius:6px;font-weight:700;font-size:12px;">AETHERIS</span>
    <span style="font-weight:600;opacity:0.9;">Sovereign Web Application Platform</span>
  </div>
  <div style="font-size:12px;opacity:0.75;">Document-Grounded Intelligence & Cloud Deployment Engine</div>
</div>
"""
    if "<body" in base_html:
        return base_html.replace("<body", header + "\n<body", 1)
    return header + base_html

def inject_rag_bot(base_html: str, doc_chunks: List[str], embed_model: str = DEFAULT_EMBED_MODEL) -> str:
    store = {
        "texts": doc_chunks,
        "vectors": None,
        "embed_model": embed_model
    }

    rag_ui = f"""
<!-- AETHERIS FLOATING RAG ASSISTANT -->
<style>
  #aetheris-rag-fab {{
    position: fixed;
    bottom: 28px;
    right: 28px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
    color: #ffffff;
    border: none;
    box-shadow: 0 10px 25px rgba(79, 70, 229, 0.4);
    cursor: pointer;
    z-index: 99999;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }}
  #aetheris-rag-fab:hover {{ transform: scale(1.08); }}

  #aetheris-rag-drawer {{
    position: fixed;
    bottom: 100px;
    right: 28px;
    width: 420px;
    max-width: calc(100vw - 32px);
    height: 600px;
    max-height: calc(100vh - 120px);
    background: rgba(15, 23, 42, 0.95);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 20px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
    z-index: 99998;
    display: none;
    flex-direction: column;
    overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #f8fafc;
  }}

  .rag-header {{ padding: 16px 20px; background: rgba(30, 41, 59, 0.8); border-bottom: 1px solid rgba(255, 255, 255, 0.08); display: flex; align-items: center; justify-content: space-between; }}
  .rag-body {{ flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }}
  .rag-msg {{ max-width: 85%; padding: 12px 16px; border-radius: 14px; font-size: 14px; line-height: 1.5; }}
  .rag-msg-user {{ align-self: flex-end; background: #4f46e5; color: #ffffff; border-bottom-right-radius: 4px; }}
  .rag-msg-bot {{ align-self: flex-start; background: #1e293b; color: #e2e8f0; border-bottom-left-radius: 4px; border: 1px solid rgba(255, 255, 255, 0.08); }}
  .rag-citation {{ font-size: 11px; background: rgba(99, 102, 241, 0.15); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.3); padding: 4px 8px; border-radius: 6px; margin-top: 6px; display: inline-block; }}
  .rag-footer {{ padding: 14px; background: rgba(15, 23, 42, 0.95); border-top: 1px solid rgba(255, 255, 255, 0.08); display: flex; flex-direction: column; gap: 8px; }}
</style>

<button id="aetheris-rag-fab" onclick="toggleRagDrawer()" title="Ask AETHERIS AI">🤖</button>

<div id="aetheris-rag-drawer">
  <div class="rag-header">
    <div style="display:flex;align-items:center;gap:10px;">
      <div style="width:10px;height:10px;border-radius:50%;background:#10b981;"></div>
      <div style="font-weight:700;font-size:16px;">AETHERIS AI Assistant</div>
    </div>
    <button onclick="toggleRagDrawer()" style="background:none;border:none;color:#94a3b8;cursor:pointer;font-size:18px;">✕</button>
  </div>

  <div class="rag-body" id="rag-chat-history">
    <div class="rag-msg rag-msg-bot">
      👋 Welcome to AETHERIS Sovereign Assistant. Ask any question regarding the document policy.
    </div>
  </div>

  <div class="rag-footer">
    <div style="display:flex;gap:8px;">
      <select id="rag-provider-select" onchange="toggleProviderSettings()"
        style="padding:6px;font-size:12px;border-radius:6px;border:1px solid #334155;background:#0f172a;color:#cbd5e1;">
        <option value="ollama">Local Brain (Ollama)</option>
        <option value="openai">OpenAI API</option>
      </select>
      <input id="rag-api-key" type="password" placeholder="OpenAI Key (optional)"
        style="flex:1;padding:6px 10px;font-size:12px;border-radius:6px;border:1px solid #334155;background:#0f172a;color:#f8fafc;" />
    </div>

    <div id="ollama-config-div" style="display:flex;gap:8px;">
      <input id="rag-ollama-url" type="text" value="http://localhost:11434" placeholder="Ollama URL"
        style="flex:1;padding:6px 10px;font-size:12px;border-radius:6px;border:1px solid #334155;background:#0f172a;color:#f8fafc;" />
      <input id="rag-ollama-model" type="text" value="{DEFAULT_OLLAMA_MODEL}" placeholder="Model"
        style="width:140px;padding:6px 10px;font-size:12px;border-radius:6px;border:1px solid #334155;background:#0f172a;color:#f8fafc;" />
    </div>

    <div style="display:flex;gap:8px;margin-top:4px;">
      <input id="rag-input-box" placeholder="Ask a question..."
        style="flex:1;padding:10px 14px;font-size:14px;border-radius:8px;border:1px solid #334155;background:#1e293b;color:#f8fafc;"
        onkeypress="if(event.key==='Enter') sendRagMessage()" />
      <button onclick="sendRagMessage()"
        style="padding:10px 18px;font-size:14px;font-weight:600;border-radius:8px;border:none;background:#4f46e5;color:#fff;cursor:pointer;">
        Send
      </button>
    </div>
  </div>
</div>

<script type="application/json" id="vector-store">
{json.dumps(store)}
</script>

<script>
const EMBED_MODEL = "{embed_model}";
const store = JSON.parse(document.getElementById("vector-store").textContent);

function toggleRagDrawer() {{
  const d = document.getElementById("aetheris-rag-drawer");
  d.style.display = d.style.display === "flex" ? "none" : "flex";
}}

function toggleProviderSettings() {{
  const p = document.getElementById("rag-provider-select").value;
  document.getElementById("ollama-config-div").style.display = (p === "ollama") ? "flex" : "none";
}}

function sanitizeHTML(str) {{
  const temp = document.createElement("div");
  temp.textContent = str;
  return temp.innerHTML;
}}

function addChatMessage(sender, text, citation = null) {{
  const history = document.getElementById("rag-chat-history");
  const msgDiv = document.createElement("div");
  msgDiv.className = sender === "user" ? "rag-msg rag-msg-user" : "rag-msg rag-msg-bot";
  let contentHtml = sanitizeHTML(text);
  if (citation) {{
    contentHtml += `<div class="rag-citation">📄 Grounded Source: "${{sanitizeHTML(citation)}}"</div>`;
  }}
  msgDiv.innerHTML = contentHtml;
  history.appendChild(msgDiv);
  history.scrollTop = history.scrollHeight;
}}

function cosine(a, b) {{
  let d=0, na=0, nb=0;
  const n = Math.min(a.length, b.length);
  for (let i=0; i<n; i++) {{
    d += a[i]*b[i];
    na += a[i]*a[i];
    nb += b[i]*b[i];
  }}
  return d/(Math.sqrt(na)*Math.sqrt(nb) + 1e-9);
}}

async function embedBatch(texts, provider, apiKey, ollamaUrl) {{
  if (provider === "openai") {{
    const r = await fetch("https://api.openai.com/v1/embeddings", {{
      method: "POST",
      headers: {{ "Content-Type":"application/json", "Authorization":"Bearer " + apiKey }},
      body: JSON.stringify({{ model: EMBED_MODEL, input: texts }})
    }});
    if (!r.ok) throw new Error("OpenAI Embed Error: " + r.status);
    const j = await r.json();
    return j.data.map(x => x.embedding);
  }} else {{
    const model = document.getElementById("rag-ollama-model").value || "{DEFAULT_OLLAMA_MODEL}";
    const embeddings = [];
    for (const text of texts) {{
      const r = await fetch(ollamaUrl.replace(/\\/+$/, "") + "/api/embeddings", {{
        method: "POST",
        headers: {{ "Content-Type":"application/json" }},
        body: JSON.stringify({{ model: model, prompt: text }})
      }});
      if (!r.ok) throw new Error("Ollama Embed Error: " + r.status);
      const j = await r.json();
      embeddings.push(j.embedding);
    }}
    return embeddings;
  }}
}}

async function sendRagMessage() {{
  const box = document.getElementById("rag-input-box");
  const q = box.value.trim();
  if (!q) return;

  addChatMessage("user", q);
  box.value = "";

  const provider = document.getElementById("rag-provider-select").value;
  const apiKey = document.getElementById("rag-api-key").value.trim();
  const ollamaUrl = document.getElementById("rag-ollama-url").value.trim() || "http://localhost:11434";

  if (provider === "openai" && !apiKey) {{
    addChatMessage("bot", "❌ Please enter an OpenAI API key.");
    return;
  }}

  try {{
    if (!store.vectors || store.vectors.length === 0) {{
      if (!store.texts || store.texts.length === 0) {{
        addChatMessage("bot", "❌ No documents uploaded to query.");
        return;
      }}
      store.vectors = await embedBatch(store.texts, provider, apiKey, ollamaUrl);
    }}

    const qv = (await embedBatch([q], provider, apiKey, ollamaUrl))[0];
    const scored = store.vectors.map((v, i) => ({{ i, s: cosine(v, qv) }}))
                                .sort((a, b) => b.s - a.s)
                                .slice(0, 3);

    const context = scored.map(x => store.texts[x.i]).join("\\n\\n---\\n\\n");
    const topCitation = store.texts[scored[0].i].substring(0, 90) + "...";

    let answer = "";
    if (provider === "openai") {{
      const r = await fetch("https://api.openai.com/v1/chat/completions", {{
        method: "POST",
        headers: {{ "Content-Type":"application/json", "Authorization":"Bearer " + apiKey }},
        body: JSON.stringify({{
          model: "gpt-4o-mini",
          messages: [
            {{ role: "system", content: "Answer strictly from context. If missing, say 'Information not found in provided documents'." }},
            {{ role: "user", content: "CONTEXT:\\n" + context + "\\n\\nQUESTION:\\n" + q }}
          ]
        }})
      }});
      const j = await r.json();
      answer = j.choices?.[0]?.message?.content || "(No response)";
    }} else {{
      const model = document.getElementById("rag-ollama-model").value || "{DEFAULT_OLLAMA_MODEL}";
      const r = await fetch(ollamaUrl.replace(/\\/+$/, "") + "/v1/chat/completions", {{
        method: "POST",
        headers: {{ "Content-Type":"application/json" }},
        body: JSON.stringify({{
          model: model,
          messages: [
            {{ role: "system", content: "Answer strictly from context. If missing, say 'Information not found in provided documents'." }},
            {{ role: "user", content: "CONTEXT:\\n" + context + "\\n\\nQUESTION:\\n" + q }}
          ]
        }})
      }});
      const j = await r.json();
      answer = j.choices?.[0]?.message?.content || "(No response)";
      answer = answer.replace(/<think>[\\s\\S]*?<\\/think>/g, "").trim();
    }}

    addChatMessage("bot", answer, topCitation);
  }} catch (e) {{
    addChatMessage("bot", "❌ Error: " + e.message);
  }}
}}
</script>
"""
    if "</body>" in base_html:
        return base_html.replace("</body>", rag_ui + "\n</body>")
    return base_html + rag_ui

def inject_all(base_html: str, rag_enabled: bool, doc_chunks: List[str]) -> str:
    html = inject_brand_header(base_html)
    if rag_enabled:
        html = inject_rag_bot(html, doc_chunks)
    return html
