import base64
import sys
import os

# Add the backend/src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from dal.integrations.gemini_client import GeminiClientSingleton

# 1. Initialize your singleton client
client = GeminiClientSingleton().client

# 2. Choose a model that supports PDF input (Gemini 2.5 Pro or Flash)
model_name = "gemini-2.5-pro"

# 3. Load the PDF and encode it
pdf_path = "western_blott.pdf"
with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()
encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
# 4. Send request to extract text from PDF
response = client.models.generate_content(
    model=model_name,
    contents=[
        {
            "parts": [
                {
                    "inline_data": {
                        "mime_type": "application/pdf",
                        "data": encoded_pdf
                    }
                },
                {
                    "text": "Extract all text from this PDF document. Preserve line breaks, formatting, and structure if possible."
                }
            ]
        }
    ]
)

# 5. Print the extracted text
print("📄 PDF Text Extraction Output:\n")
print(response.text)
