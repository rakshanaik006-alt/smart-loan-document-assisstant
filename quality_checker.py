from PIL import Image
import cv2
import numpy as np
import os
from pdf2image import convert_from_path


# File validation
def validate_file(filename):
    allowed = ['.jpg', '.jpeg', '.png', '.pdf']

    for ext in allowed:
        if filename.lower().endswith(ext):
            return True, "Valid file ✅"

    return False, "Invalid file type ❌"


# Convert PDF to image
def convert_pdf_to_image(pdf_path):
    pages = convert_from_path(pdf_path)

    first_page = pages[0]
    image_path = "temp_doc.jpg"

    first_page.save(image_path, "JPEG")

    return image_path


# Resolution check
def check_resolution(image_path):
    img = Image.open(image_path)
    width, height = img.size

    if width < 500 or height < 500:
        return False, "Low resolution ❌"

    return True, "Good resolution ✅"


# Blur detection
def check_blur(image_path):
    img = cv2.imread(image_path)
    
    if img is None:
        return False, "Unable to read image ❌"

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

    if blur_score < 100:
        return False, "Blurry image ❌"

    return True, "Clear image ✅"


# Brightness check
def check_brightness(image_path):
    img = cv2.imread(image_path)

    if img is None:
        return False, "Unable to read image ❌"

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    brightness = np.mean(gray)

    if brightness < 50:
        return False, "Too dark ❌"
    elif brightness > 200:
        return False, "Too bright ⚠️"

    return True, "Good brightness ✅"


# Main function for integration
def document_quality_report(file):

    if not os.path.exists(file):
        return {"error": "File not found ❌"}

    file_status, file_msg = validate_file(file)

    if not file_status:
        return {"error": file_msg}

    # PDF support
    if file.lower().endswith(".pdf"):
        file = convert_pdf_to_image(file)

    resolution_status, resolution_msg = check_resolution(file)
    blur_status, blur_msg = check_blur(file)
    brightness_status, brightness_msg = check_brightness(file)

    final_status = (
        file_status and
        resolution_status and
        blur_status and
        brightness_status
    )

    if final_status:
        final_msg = "Document acceptable for submission ✅"
    else:
        final_msg = "Please re-upload better document ❌"

    return {
        "file_validation": file_msg,
        "resolution": resolution_msg,
        "blur": blur_msg,
        "brightness": brightness_msg,
        "final_result": final_msg
    }