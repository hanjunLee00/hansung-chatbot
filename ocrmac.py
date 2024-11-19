import pymysql  # pymysql로 변경
import requests
import io
import objc
from PIL import Image
import Vision
from typing import List, Tuple
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database credentials from environment variables
db = pymysql.connect(
    host="localhost",
    user="root",
    password="12345678",  # 환경변수 활용으로 보안 강화
    database="crawled"
)
cursor = db.cursor()

def pil2buf(pil_image: Image.Image):
    """Convert PIL image to buffer"""
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    return buffer.getvalue()

def load_image_from_url(url: str) -> Image.Image:
    """Load image from a URL into PIL format"""
    response = requests.get(url)
    if response.status_code == 200:
        image = Image.open(io.BytesIO(response.content))
        return image
    else:
        raise Exception(f"Failed to retrieve image from {url}")

def text_from_image(
    image, recognition_level="accurate", language_preference=None, confidence_threshold=0.0
) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
    """Extract text from image using Apple's Vision framework."""
    if not isinstance(image, Image.Image):
        raise ValueError("Invalid image format. Image must be a PIL image.")

    if recognition_level not in {"accurate", "fast"}:
        raise ValueError("Invalid recognition level. Must be 'accurate' or 'fast'.")

    if language_preference is not None and not isinstance(language_preference, list):
        raise ValueError("Language preference must be a list.")

    with objc.autorelease_pool():
        req = Vision.VNRecognizeTextRequest.alloc().init()
        req.setRecognitionLevel_(1 if recognition_level == "fast" else 0)

        if language_preference is not None:
            available_languages = req.supportedRecognitionLanguagesAndReturnError_(None)[0]
            if not set(language_preference).issubset(set(available_languages)):
                raise ValueError(
                    f"Invalid language preference. Must be a subset of {available_languages}."
                )
            req.setRecognitionLanguages_(language_preference)

        handler = Vision.VNImageRequestHandler.alloc().initWithData_options_(
            pil2buf(image), None
        )

        success = handler.performRequests_error_([req], None)
        res = []
        if success:
            for result in req.results():
                confidence = result.confidence()
                if confidence >= confidence_threshold:
                    bbox = result.boundingBox()
                    x, y = bbox.origin.x, bbox.origin.y
                    w, h = bbox.size.width, bbox.size.height
                    res.append((result.text(), confidence, (x, y, w, h)))
            
        return res

# Query images with content field that needs to be updated
cursor.execute("SELECT id, image, content FROM swpre WHERE image IS NOT NULL")
image_rows = cursor.fetchall()

if not image_rows:
    print("No images found.")
else:
    for row in image_rows:
        id, image_url, existing_content = row
        try:
            # Load image from URL
            image = load_image_from_url(image_url)

            # Perform OCR
            recognized_text = text_from_image(image, recognition_level="accurate", language_preference=["ko-KR"], confidence_threshold=0.8)
            extracted_text = " ".join([text for text, _, _ in recognized_text])

            # Prepare SQL query to concatenate existing content with extracted text
            if existing_content:
                new_content = f"{existing_content} {extracted_text}"
            else:
                new_content = extracted_text

            # Print and update content in the database
            print(f"Extracted text for ID {id}: {extracted_text}")
            cursor.execute("UPDATE swpre SET content = CONCAT(content, %s) WHERE id = %s", (f" {extracted_text.strip()}", id))
            db.commit()
            print(f"Updated content for ID {id}")

        except requests.exceptions.RequestException as e:
            print(f"Failed to download image for ID {id}: {e}")
        except Exception as e:
            print(f"Error for ID {id}: {e}")

# Close database connection
cursor.close()
db.close()
