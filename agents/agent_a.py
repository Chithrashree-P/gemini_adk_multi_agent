import pdfplumber
import json
import re
from utils.llm import call_llm


def extract_text(file_path):
    """
    Supports both .pdf and .txt files correctly
    """
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    if file_path.endswith(".pdf"):
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text
        except Exception as e:
            print(" PDF Read Error:", e)
            return ""

    print("Unsupported file format")
    return ""


def clean_json_response(response):
    """
    Gemini sometimes returns text + JSON → extract only JSON part
    """
    try:
        # Extract JSON block using regex
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            return match.group(0)
    except:
        pass
    return response


def extract_requirements(file_path):
    text = extract_text(file_path)

    if not text:
        print(" No text extracted from file")
        return {"url": "", "scenarios": []}

    prompt = f"""
   
    You are Agent A - Requirements Extractor. 
    Extract ALL testable UI requirements from this SRS document.

        SRS Document Content:
        {text}
        Return ONLY VALID JSON. No explanation.

        Format:
        {{
        "url": "https://the-internet.herokuapp.com/",
        "scenarios": [
            {{
            "id": "- IDs must be sequential like TC01, TC02, TC03...
                   - Maintain strict ordering across all scenarios",
            "title": "Valid Login",
            "path": "/login",
            "steps": ["Enter username", "Enter password", "Click login"],
            "expected": "Success message displayed"
            }}
        ]
        }} 
            
    Include:
    - login scenarios
    - valid cases
    - edge cases

    TEXT:
    {text}
    """

    response = call_llm(prompt)

    print("\n RAW LLM RESPONSE:\n", response)  # Debug log

    cleaned = clean_json_response(response)

    try:
        parsed = json.loads(cleaned)
        return parsed
    except Exception as e:
        print(" JSON Parse Error:", e)

        return {
            "url": "https://the-internet.herokuapp.com/",
            "scenarios": []
        }