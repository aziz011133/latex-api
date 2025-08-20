from flask import Flask, request, send_file
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 Welcome to the LaTeX API. Use POST /latex with JSON to compile LaTeX."

@app.route("/latex", methods=["POST"])
def compile_latex():
    data = request.get_json()
    if not data or "latex" not in data:
        return {"error": "Missing 'latex' field in JSON"}, 400

    latex_code = data["latex"]

    with open("doc.tex", "w") as f:
        f.write(latex_code)

    try:
        subprocess.run(["pdflatex", "doc.tex"], check=True)
        return send_file("doc.pdf", as_attachment=True)
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
