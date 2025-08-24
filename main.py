import os, base64
import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

MAX_LATEX_CHARS = int(os.getenv("MAX_LATEX_CHARS", "200000"))  # حد أقصى اختياري

@app.get("/")
def index():
    return "🚀 Welcome to the LaTeX API. Use POST /latex with JSON to compile LaTeX."

@app.get("/health")
def health():
    return {"status": "ok"}

def _compile_via_upstream(latex: str, compiler: str = "pdflatex"):
    payload = {
        "compiler": compiler,  # pdflatex | xelatex | lualatex ...
        "resources": [
            {"main": True, "content": latex}
        ]
    }
    return requests.post(
        "https://latex.ytotech.com/builds/sync",
        json=payload,
        timeout=60
    )

@app.post("/latex")
def latex_base64():
    data = request.get_json(force=True, silent=True) or {}
    latex = data.get("latex")
    compiler = data.get("compiler", "pdflatex")

    if not latex or not isinstance(latex, str):
        return jsonify({"error": "Missing 'latex' (string)"}), 400
    if len(latex) > MAX_LATEX_CHARS:
        return jsonify({"error": "LaTeX too large"}), 413

    try:
        r = _compile_via_upstream(latex, compiler)
    except requests.RequestException as e:
        return jsonify({"error": f"upstream_error: {e}"}), 502

    if r.status_code == 200 and r.headers.get("Content-Type","").startswith("application/pdf"):
        pdf_b64 = base64.b64encode(r.content).decode("utf-8")
        return jsonify({"pdf_base64": pdf_b64})
    else:
        # حاول إرجاع لوج الخطأ من السيرفر الخارجي
        try:
            err = r.json()
        except Exception:
            err = {"message": r.text[:2000]}
        return jsonify({"error": "compile_failed", "upstream": err}), 400

@app.post("/latex/pdf")
def latex_pdf():
    data = request.get_json(force=True, silent=True) or {}
    latex = data.get("latex")
    compiler = data.get("compiler", "pdflatex")

    if not latex:
        return jsonify({"error":"Missing 'latex'"}), 400

    try:
        r = _compile_via_upstream(latex, compiler)
    except requests.RequestException as e:
        return jsonify({"error": f"upstream_error: {e}"}), 502

    if r.status_code == 200 and r.headers.get("Content-Type","").startswith("application/pdf"):
        return Response(r.content, content_type="application/pdf")
    else:
        try:
            err = r.json()
        except Exception:
            err = {"message": r.text[:2000]}
        return jsonify({"error":"compile_failed", "upstream": err}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
