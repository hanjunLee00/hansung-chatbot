import requests
import io
import objc
from PIL import Image
import Vision
from typing import List, Tuple
from dotenv import load_dotenv
from datetime import datetime
import mysql.connector

# Load environment variables
load_dotenv()

# Database credentials from environment variables
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",
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
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            return image
        else:
            raise Exception(f"Failed to retrieve image from {url}, status code: {response.status_code}")
    except Exception as e:
        print(f"Error loading image from URL: {e}")
        return None

def text_from_image(image, recognition_level="accurate", language_preference=None, confidence_threshold=0.0):
    """Extract text from image using Apple's Vision framework."""
    if not isinstance(image, Image.Image):
        print("Invalid image format.")
        return []

    with objc.autorelease_pool():
        req = Vision.VNRecognizeTextRequest.alloc().init()
        req.setRecognitionLevel_(1 if recognition_level == "fast" else 0)
        if language_preference:
            req.setRecognitionLanguages_(language_preference)

        handler = Vision.VNImageRequestHandler.alloc().initWithData_options_(
            pil2buf(image), None
        )

        success = handler.performRequests_error_([req], None)
        results = []
        if success:
            for result in req.results():
                if result.confidence() >= confidence_threshold:
                    results.append((result.text(), result.confidence()))
        return results

# 기준 날짜 설정 (날짜만 비교)
reference_date = datetime(2024, 11, 26)
print(f"Reference date: {reference_date}")

# SQL 쿼리 결과 확인
cursor.execute("""
    SELECT id, image, content, date FROM swpre
    WHERE image IS NOT NULL AND date >= %s
    """, (reference_date,))
image_rows = cursor.fetchall()

print(f"Fetched {len(image_rows)} rows from the database.")

updated_count = 0

if not image_rows:
    print("No images found after the reference date.")
else:
    for row in image_rows:
        id, image_url, existing_content, pub_date = row
        print(f"Processing ID: {id}, Date: {pub_date}, Image URL: {image_url}")

        try:
            # 이미지 다운로드
            image = load_image_from_url(image_url)
            if image is None:
                print(f"Skipping ID {id} due to image load failure.")
                continue

            # OCR 수행
            recognized_text = text_from_image(image, recognition_level="accurate", language_preference=["ko-KR"], confidence_threshold=0.8)
            extracted_text = " ".join([text for text, _ in recognized_text])

            if not extracted_text:
                print(f"No text recognized for ID {id}.")
                continue

            # 기존 내용과 합쳐서 업데이트
            if existing_content:
                new_content = f"{existing_content} {extracted_text}"
            else:
                new_content = extracted_text

            print(f"Extracted text for ID {id}: {extracted_text}")

            cursor.execute("UPDATE swpre SET content = CONCAT(content, %s) WHERE id = %s", (f" {extracted_text.strip()}", id))
            db.commit()
            updated_count += 1
            print(f"Updated content for ID {id}")

        except Exception as e:
            print(f"Error processing ID {id}: {e}")

# 데이터베이스 연결 종료
cursor.close()
db.close()

print(f"{updated_count}개의 공지사항 이미지가 성공적으로 변환되었습니다.")
