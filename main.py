from flask import Flask, request, send_file
import subprocess
import tempfile
import os

app = Flask(__name__)

@app.route("/latex", methods=["POST"])
def compile_latex():
    data = request.get_json()
    latex_code = data.get("latex")

    # مجلد مؤقت لحفظ الملفات
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "doc.tex")
        pdf_path = os.path.join(tmpdir, "doc.pdf")

        # كتابة الكود LaTeX في ملف
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_code)

        # تشغيل pdflatex
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_path],
            cwd=tmpdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # لو فيه خطأ
        if result.returncode != 0 or not os.path.exists(pdf_path):
            return {
                "error": "compile_failed",
                "log": result.stdout.decode("utf-8", errors="ignore")
            }

        # إرجاع PDF للمتصفح أو Postman
        return send_file(pdf_path, mimetype="application/pdf")

