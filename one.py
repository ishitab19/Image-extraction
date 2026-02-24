import cv2  
import numpy as np
import pytesseract
from PIL import Image
import io
import re
import base64
import pandas as pd

print("All libraries installed successfully")

from PIL import Image
from bs4 import BeautifulSoup
from mistralai import Mistral
from unstructured.partition.image import partition_image

# --- Configuration ---
MISTRAL_API_KEY = "Af4fp6qI2wqBA8RP87E1eunikYiEYss3"


def preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None: return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
   
    # sharpening 
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(gray, -1, kernel)

    # Maintain original aspect ratio but ensure a minimum width of 2000px
    # Mistral handles larger images with better numerical accuracy
    height, width = sharpened.shape
    if width < 2000:
        scale = 2000 / width
        sharpened = cv2.resize(sharpened, None, fx=scale, fy=scale, interpolation=cv2.INTER_LANCZOS4)
    return sharpened


def encode_image_with_pillow(processed_cv_image):
    """Converts OpenCV image to Pillow, then to base64 for API."""
    # Convert OpenCV (BGR/Grayscale) to Pillow Image
    color_coverted = cv2.cvtColor(processed_cv_image, cv2.COLOR_GRAY2RGB)
    pil_image = Image.fromarray(color_coverted)
   
    # Save to buffer
    buffered = io.BytesIO()
    pil_image.save(buffered, format="PNG") 
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def is_low_quality(elements):
    """Strategy 1 & 2: Validates Unstructured output via BeautifulSoup."""
    tables = [el for el in elements if el.category == "Table"]
    if not tables:
        return True

    for table in tables:
        html_str = table.metadata.text_as_html
        if not html_str: return True
       
        soup = BeautifulSoup(html_str, "html.parser")
        rows = soup.find_all("tr")
        cells = soup.find_all("td")
       
        # Quality Gate: Min 2 rows and less than 50% empty cells
        if len(rows) < 2: return True
        if cells:
            empty = [c for c in cells if not c.get_text(strip=True)]
            if len(empty) / len(cells) > 0.5: return True    
    return False


def extract_with_mistral(processed_image):
    """Calls Mistral API using the Pillow-encoded image."""
    print("[Action] Falling back to Mistral OCR...")
    client = Mistral(api_key=MISTRAL_API_KEY)
    base64_img = encode_image_with_pillow(processed_image)
   
    response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "image_url",
            "image_url": f"data:image/png;base64,{base64_img}"
        }
    )
    return response.pages[0].markdown


def process_and_extract(image_path):
    # 1. OpenCV Preprocessing
    processed = preprocess_image(image_path)
    if processed is None: return "Failed to process image."

    # 2. Local Extraction Attempt
    print(f"[System] Attempting local extraction...")
    elements = partition_image(filename=image_path, strategy="hi_res")  #unstructed

    # 3. Quality Validation
    if is_low_quality(elements):
        # 4. Mistral Fallback
        final_output = extract_with_mistral(processed)
    else:
        print("[System] Local extraction passed.")
        final_output = "\n\n".join([str(el) for el in elements])


    # 5. Visualization with OpenCV
    cv2.imshow("Processed for OCR", processed)
    print("\n=== FINAL OUTPUT ===\n", final_output)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return final_output


if __name__ == "__main__":
    process_and_extract("datatable.png")


