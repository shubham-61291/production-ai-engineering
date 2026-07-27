import os
import zipfile
from typing import Tuple, Dict, Any
from google.cloud import storage

def create_404_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - Page Not Found | AETHERIS</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b0f17; color: #f8fafc; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; text-align: center; }
        .container { max-width: 500px; padding: 40px; background: rgba(22, 30, 46, 0.75); border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); }
        h1 { font-size: 72px; margin: 0; color: #6366f1; }
        p { font-size: 18px; color: #94a3b8; }
        a { display: inline-block; margin-top: 20px; padding: 12px 24px; background: #4f46e5; color: #fff; text-decoration: none; border-radius: 8px; font-weight: 600; }
    </style>
</head>
<body>
    <div class="container">
        <h1>404</h1>
        <h2>Resource Not Found</h2>
        <p>The requested page or resource could not be found on this GCP hosted AETHERIS application.</p>
        <a href="/index.html">Return to Homepage</a>
    </div>
</body>
</html>"""

def save_site(html: str, site_dir: str = "./generated_site", zip_path: str = "./generated_site.zip") -> Tuple[str, str]:
    os.makedirs(site_dir, exist_ok=True)
    index_path = os.path.join(site_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    error_path = os.path.join(site_dir, "404.html")
    with open(error_path, "w", encoding="utf-8") as f:
        f.write(create_404_html())

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(index_path, arcname="index.html")
        z.write(error_path, arcname="404.html")

    return zip_path, index_path

def deploy_to_gcp_bucket(html: str, json_key_path: str, bucket_name: str) -> Dict[str, Any]:
    bucket_name = bucket_name.strip()
    try:
        if not os.path.exists(json_key_path):
            return {
                "success": False,
                "message": f"Deployment Error: GCP Service Account Key file not found at '{json_key_path}'"
            }

        client = storage.Client.from_service_account_json(json_key_path)
        bucket = client.bucket(bucket_name)

        if not bucket.exists():
            bucket = client.create_bucket(bucket_name, location="ASIA-SOUTH1")

        bucket.configure_website(main_page_suffix="index.html", not_found_page="404.html")
        bucket.cors = [{
            "origin": ["*"],
            "method": ["GET", "POST", "HEAD", "OPTIONS"],
            "responseHeader": ["Content-Type", "Access-Control-Allow-Origin"],
            "maxAgeSeconds": 3600
        }]
        bucket.patch()

        blob_index = bucket.blob("index.html")
        blob_index.upload_from_string(html, content_type="text/html", cache_control="public, max-age=3600")

        blob_404 = bucket.blob("404.html")
        blob_404.upload_from_string(create_404_html(), content_type="text/html", cache_control="public, max-age=3600")

        public_url = f"https://storage.googleapis.com/{bucket_name}/index.html"
        website_endpoint = f"http://{bucket_name}.storage.googleapis.com/index.html"

        return {
            "success": True,
            "public_url": public_url,
            "website_endpoint": website_endpoint,
            "message": f"✅ AETHERIS DEPLOYMENT SUCCESSFUL!\nWeb Application live on GCP Bucket.\nURL: {public_url}\nEndpoint: {website_endpoint}"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"❌ GCP DEPLOYMENT ERROR: {str(e)}"
        }
