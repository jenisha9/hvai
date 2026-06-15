import os
from typing import List, Optional

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB total request limit

ALLOWED_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/heic",
    "image/heif",
}


class Difference(BaseModel):
    area: str = Field(description="The image area, component, or asset feature being compared.")
    image_1_observation: str = Field(description="What is visible in the first image.")
    image_2_observation: str = Field(description="What is visible in the second image.")
    severity: str = Field(description="One of: low, medium, high, critical.")


class MaintenanceItem(BaseModel):
    issue: str = Field(description="A concise issue or maintenance concern.")
    recommendation: str = Field(description="Recommended maintenance action.")
    priority: str = Field(description="One of: low, medium, high, urgent.")


class ImageComparison(BaseModel):
    summary: str
    differences: List[Difference]
    confidence: float = Field(ge=0, le=1, description="Overall confidence from 0 to 1.")
    maintenance_report: List[MaintenanceItem]
    limitations: Optional[str] = Field(default=None, description="Any caveats about image quality or uncertainty.")


def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY. Add it to your .env file.")
    return genai.Client(api_key=api_key)


def read_upload(file_storage):
    mime_type = file_storage.mimetype
    if mime_type not in ALLOWED_MIME_TYPES:
        raise ValueError(f"Unsupported file type: {mime_type}")
    return types.Part.from_bytes(data=file_storage.read(), mime_type=mime_type)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compare", methods=["POST"])
def compare_images():
    try:
        image_1 = request.files.get("image1")
        image_2 = request.files.get("image2")

        if not image_1 or not image_2:
            return jsonify({"error": "Please upload two images."}), 400

        image_1_part = read_upload(image_1)
        image_2_part = read_upload(image_2)

        prompt = """
Compare these two images as if they are inspection or maintenance photos of the same asset, area, or object.

Return a practical maintenance-focused comparison. Identify visible differences only. Do not invent hidden defects.
For the maintenance report, include action-oriented recommendations and priorities.
Set confidence based on image clarity, angle similarity, and how obvious the differences are.
""".strip()

        client = get_client()
        model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

        response = client.models.generate_content(
            model=model,
            contents=[prompt, image_1_part, image_2_part],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ImageComparison,
            ),
        )

        result = ImageComparison.model_validate_json(response.text)
        return jsonify(result.model_dump())

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
