import os
import base64
import json
import fitz  # PyMuPDF
from flask import Flask, request, jsonify
from flask_cors import CORS
from docx import Document
from werkzeug.utils import secure_filename
from groq import Groq

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "docx"}
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def pdf_to_base64_images(filepath):
    doc = fitz.open(filepath)
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        images.append(base64.standard_b64encode(img_bytes).decode("utf-8"))
    return images

def image_to_base64(filepath):
    with open(filepath, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")

def docx_to_text(filepath):
    doc = Document(filepath)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

EXTRACTION_PROMPT = """
You are a loan document analysis expert. Extract ALL possible fields from this document.
Return ONLY a valid JSON object with these fields (use null if not found):

{
  "borrower_name": "",
  "co_borrower_name": "",
  "loan_account_number": "",
  "loan_type": "",
  "loan_amount": "",
  "sanctioned_amount": "",
  "disbursed_amount": "",
  "outstanding_amount": "",
  "interest_rate": "",
  "loan_tenure": "",
  "emi_amount": "",
  "emi_start_date": "",
  "loan_start_date": "",
  "loan_end_date": "",
  "next_due_date": "",
  "repayment_mode": "",
  "bank_name": "",
  "branch_name": "",
  "branch_code": "",
  "account_number": "",
  "ifsc_code": "",
  "processing_fee": "",
  "prepayment_charges": "",
  "collateral_type": "",
  "collateral_value": "",
  "guarantor_name": "",
  "pan_number": "",
  "aadhaar_number": "",
  "address": "",
  "city": "",
  "state": "",
  "pincode": "",
  "mobile_number": "",
  "email": "",
  "income": "",
  "employment_type": "",
  "employer_name": "",
  "credit_score": "",
  "document_type": "",
  "document_date": "",
  "overdue_amount": "",
  "penalty_charges": "",
  "loan_status": ""
}

Return ONLY the JSON. No explanation, no markdown.
"""

def extract_with_groq(filepath, file_ext):
    if file_ext == "docx":
        text = docx_to_text(filepath)
        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[{
                "role": "user",
                "content": f"{EXTRACTION_PROMPT}\n\nDocument text:\n{text}"
            }]
        )
        raw = response.choices[0].message.content

    elif file_ext == "pdf":
        images = pdf_to_base64_images(filepath)
        img_b64 = images[0]  # use first page
        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": EXTRACTION_PROMPT
                    }
                ]
            }]
        )
        raw = response.choices[0].message.content

    else:  # image files
        img_b64 = image_to_base64(filepath)
        ext_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png"}
        media_type = ext_map.get(file_ext, "image/png")
        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{img_b64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": EXTRACTION_PROMPT
                    }
                ]
            }]
        )
        raw = response.choices[0].message.content

    cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(cleaned)


@app.route("/extract", methods=["POST"])
def extract():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not supported"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    file_ext = filename.rsplit(".", 1)[1].lower()

    try:
        extracted_data = extract_with_groq(filepath, file_ext)
        return jsonify({
            "success": True,
            "filename": filename,
            "extracted_fields": extracted_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)