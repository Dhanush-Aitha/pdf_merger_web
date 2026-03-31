from flask import Flask, render_template, request, send_file
import os
from pypdf import PdfWriter
from collections import defaultdict
print("RUNNING THIS APP.PY FILE")
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def group_pdfs(files):
    pdf_groups = defaultdict(list)

    for file in files:
        filename = file.filename
        digits = ''.join(filter(str.isdigit, filename))

        first_10 = digits[:10]
        last_15 = digits[-15:]

        pdf_groups[last_15].append((filename, first_10))

    return pdf_groups


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_files = request.files.getlist("pdfs")

        saved_files = []
        for file in uploaded_files:
            path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(path)
            saved_files.append(file)

        pdf_groups = group_pdfs(saved_files)

        output_files = []

        for last_15, files in pdf_groups.items():
            writer = PdfWriter()

            first_10_digits = files[0][1]
            output_pdf_path = os.path.join(
                OUTPUT_FOLDER,
                f"{first_10_digits}_{last_15}.pdf"
            )

            for filename, _ in sorted(files):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                with open(file_path, "rb") as f:
                    writer.append(f)

            with open(output_pdf_path, "wb") as out:
                writer.write(out)

            output_files.append(output_pdf_path)

        return send_file(output_files[0], as_attachment=True)

    return render_template("index.html")


# ✅ Production server
from waitress import serve

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080)
