# ⚡ AETHERIS‑WEBFORGE

**AI‑Powered Web Application Generator, Hardened RAG, & One‑Click GCP Deployment Engine**

---

## 📖 Overview

AETHERIS‑WEBFORGE is a production‑ready platform that turns natural language prompts into **complete, self‑contained HTML5 web applications**.  
It uses a **local GPU‑accelerated AI brain** (Qwen2.5‑Coder 32B via Ollama) to generate professional, functional websites entirely on‑premise.

Every generated application is:
- **Client‑side ready** – single HTML file with all CSS/JS embedded.
- **Deployable in one click** – directly to Google Cloud Storage with a public URL.
- **Security‑hardened** – prompt injection guard, output sanitisation, and rate limiting.
- **Royalty‑free** – no branding, logos, or proprietary assets added.

The system demonstrates a full AI‑to‑production pipeline:  
`Prompt → AI Generation → Live Website`

---

## 🚀 Features

- **🧠 Local AI Brain** – Qwen2.5‑Coder 32B (or any Ollama model) running on GPU.
- **🛡️ Security Guardrails** – Prompt injection detection and output filtering.
- **📦 One‑Click GCP Deploy** – Uploads generated HTML to a Cloud Storage bucket (no API keys required).
- **⚡ Zero‑Setup Deployment** – The VM’s built‑in identity handles authentication automatically.
- **🎨 Clean, Modern UI** – Responsive dashboard with live preview iframe.
- **📂 Support for External Libraries** – The AI can use CDN‑based frameworks (Tailwind, Bootstrap, PDF‑lib, jsPDF, etc.) when appropriate.

---

## 🧠 Technology Stack

| Component         | Technology                                      |
|-------------------|-------------------------------------------------|
| Language          | Python 3.10                                     |
| Backend           | FastAPI, Uvicorn                                |
| Frontend          | Vanilla HTML/CSS/JS (served directly)           |
| AI Inference      | Ollama, Qwen2.5‑Coder 32B (GPU)                 |
| Security          | Custom prompt injection guard (regex + heuristics) |
| Deployment        | Google Cloud Storage (Python client)            |
| Infrastructure    | Docker, Google Cloud GPU VM (L4)                |

---

## 📸 Live Demonstration – PDF World

*The following screenshots show a complete end‑to‑end workflow using AETHERIS‑WEBFORGE to generate a **PDF toolkit website** similar to iLovePDF.*

### 1. Main Interface & Prompt
The user enters a detailed prompt describing the desired application.
![AETHERIS Interface](./lov1.png)

### 2. AI‑Generated Web Application
The Qwen2.5‑Coder model generates a fully functional HTML file with PDF manipulation tools (merge, split, compress, convert, etc.).
![Generated PDF Tool Website](./lov2.png)

### 3. One‑Click GCP Deployment
With a single click, the generated website is uploaded to Google Cloud Storage and a public URL is returned.
![Deployed on GCP](./lov3gcpdeployed.png)



---

## ⚡ Quick Start (Deploy on a GPU VM)

1. **Clone the repository**
   ```bash
   git clone https://github.com/shubham-61291/aetheris-webforge.git
   cd aetheris-webforge



2. **🚀 Configure Environment**

Copy the example environment file and update the required values.

```bash
cp .env.example .env
```

Edit the `.env` file and set:

```env
OLLAMA_BASE_URL=
OLLAMA_MODEL=qwen2.5-coder:32b
```

---

3. **🐳 Build & Start the Docker Container**

Build the Docker image:

```bash
docker build -t aetheris-webforge .
```

Run the container:

```bash
docker run -d \
  --name aetheris \
  -p 7860:7860 \
  --env-file .env \
  --restart unless-stopped \
  aetheris-webforge
```

---

## 🌐 Access the Dashboard

Open the following URL in your browser:

```text
http://<your-vm-ip>:7860
```

---

# 🛠️ Usage

## ✨ Generate a Website

1. Type a detailed description of the website you want.

   Example:

   > Create a PDF tool page like iLovePDF with merge, split, compress functions.

2. Click **✨ Generate Website**.

3. Wait approximately **30–60 seconds**.

4. The generated website will appear in the **live preview** panel.

---

## 🚀 Deploy to Google Cloud Storage (GCP)

Click the **🚀 Deploy to GCP** button.

The generated HTML is uploaded directly to your **Google Cloud Storage** bucket.

### Features

- No service account key required.
- Uses the VM's built-in identity for authentication.
- Default bucket:

```text
aetheris-generated-sites
```

You can change the bucket name in the `.env` file.

### Make the Website Public

Run the following command **once** in **Cloud Shell**:

```bash
gsutil iam ch allUsers:objectViewer gs://aetheris-generated-sites
```

---

# ⚠️ Important Notes

- The system prompt is optimized for **enterprise-grade code generation**.
  You can customize it in:

  ```text
  core/generator.py
  ```

- The AI **never** adds:
  - Branding
  - Logos
  - External links

  unless they are explicitly requested.

- No user data is collected or stored.
  All website generation happens **locally on your VM**.

- GCP deployment requires the VM to have the **Storage Admin** IAM role.
  This is already available when using the configured `http-server` service account.

---

# 👨‍💻 Author

**Shubham Singh**

---

# 📜 License

MIT License
