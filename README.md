# Gemini Image Comparison Prototype - Python

A small complete Flask prototype that lets you upload two images, sends them to Gemini, and displays:

- Summary
- Differences
- Confidence
- Maintenance report

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Gemini API key to `.env`:

```bash
GEMINI_API_KEY=your_api_key_here
```

## Run

```bash
python app.py
```

Then open:

```text
http://localhost:5000
```

## Notes

- Supported upload types: PNG, JPEG, WEBP, HEIC, HEIF.
- The app uses structured output via Pydantic so the frontend receives predictable fields.
- Uploaded images are processed in memory and are not saved to disk.
