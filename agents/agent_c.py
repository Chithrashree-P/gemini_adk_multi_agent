# import json
# import re
# import ast
# from utils.llm import call_llm


# def validate_code(code: str, requirements: dict) -> dict:
#     print(" [Agent C] Validating code...")

#     # Handle empty code

#     if not code or not code.strip():
#         return {
#             "issues": [{
#                 "scenario": "all",
#                 "problem": "Code is empty",
#                 "severity": "high",
#                 "action": "regenerate"
#             }]
#         }

#     prompt = f"""You are a strict QA automation reviewer.

# STRICT RULES:
# - Code MUST be valid Python
# - DO NOT allow JavaScript syntax (e.g., {{ key: value }})
# - Ensure Playwright Python syntax is correct
# - Detect syntax errors and invalid API usage
# - Ensure all test scenarios are covered

# Requirements:
# {requirements}

# Code:
# {code}

# Return ONLY JSON in format:
# {{
#   "issues": [
#     {{
#       "scenario": "TC01",
#       "problem": "description",
#       "severity": "high/medium/low",
#       "action": "fix/generate"
#     }}
#   ]
# }}
# """

#     response = call_llm(prompt)

#     print("\n RAW VALIDATION RESPONSE:\n", response)

#     # -----------------------------
#     # Extract JSON safely
#     # -----------------------------
#     try:
#         match = re.search(r"\{.*\}", response, re.DOTALL)
#         if match:
#             parsed = json.loads(match.group(0))
#         else:
#             raise ValueError("No JSON found in response")

#     except Exception as e:
#         print(" JSON Parse Error:", e)
#         parsed = {
#             "issues": [{
#                 "scenario": "validation",
#                 "problem": "LLM response parsing failed",
#                 "severity": "high",
#                 "action": "regenerate"
#             }]
#         }

#     # Ensure issues key exists
#     if not parsed.get("issues"):
#         parsed["issues"] = []

#     # -----------------------------
#     # Syntax Validation (CRITICAL)
#     # -----------------------------
#     try:
#         ast.parse(code)
#     except SyntaxError as e:
#         parsed["issues"].append({
#             "scenario": "syntax",
#             "problem": f"Syntax error: {str(e)}",
#             "severity": "high",
#             "action": "fix"
#         })

#     # -----------------------------
#     # Detect JavaScript Syntax
#     # -----------------------------
#     if re.search(r"\{.*?:.*?\}", code):
#         parsed["issues"].append({
#             "scenario": "syntax",
#             "problem": "JavaScript-style object detected in Python code",
#             "severity": "high",
#             "action": "fix"
#         })

#     # -----------------------------
#     # Playwright-specific Checks
#     # -----------------------------
#     if "mouse.move" in code and "{" in code:
#         parsed["issues"].append({
#             "scenario": "playwright",
#             "problem": "Invalid mouse.move syntax (JS-style object used)",
#             "severity": "high",
#             "action": "fix"
#         })

#     # Detect JS arrow functions (extra safety)
#     if "=>" in code:
#         parsed["issues"].append({
#             "scenario": "syntax",
#             "problem": "JavaScript arrow function detected",
#             "severity": "high",
#             "action": "fix"
#         })

#     # -----------------------------
#     # Scenario Coverage Check
#     # -----------------------------
#     for scenario in requirements.get("scenarios", []):
#         if scenario.get("id") and scenario["id"] not in code:
#             parsed["issues"].append({
#                 "scenario": scenario["id"],
#                 "problem": "Missing test case",
#                 "severity": "medium",
#                 "action": "generate"
#             })

#     return parsed

import json
import re
import ast
from utils.llm import call_llm


def validate_code(code: str, requirements: dict, locators: dict = None, test_results: dict = None) -> dict:
    print(" [Agent C] Validating code...")

    
    # Handle empty code
  
    if not code or not code.strip():
        return {
            "issues": [{
                "scenario": "all",
                "problem": "Code is empty",
                "severity": "high",
                "action": "regenerate"
            }]
        }

    # Extract logs (if available)
    
    logs = ""
    if test_results:
        logs = test_results.get("logs", "")

    # LLM Validation Prompt 
  
    prompt = f"""
You are Agent C - QA Validator & Debugger.

STRICT RULES:
- Code MUST be valid Python
- DO NOT allow JavaScript syntax
- Ensure Playwright Python syntax is correct
- Ensure all test scenarios are covered

Inputs:
Requirements:
{json.dumps(requirements, indent=2)}

Locators:
{json.dumps(locators, indent=2) if locators else "None"}

Execution Logs:
{logs if logs else "No logs available"}

Code:
{code}

Tasks:
1. Detect syntax errors
2. Detect missing scenarios
3. Detect incorrect or unused locators
4. Detect flaky waits or missing waits
5. Analyze logs for:
   - TimeoutError
   - locator not found
   - assertion failures

Return ONLY JSON:
{{
  "issues": [
    {{
      "scenario": "TC01",
      "problem": "description",
      "severity": "high/medium/low",
      "action": "fix/generate"
    }}
  ]
}}
"""

    response = call_llm(prompt)

    print("\n RAW VALIDATION RESPONSE:\n", response)

    
    # Extract JSON safely
    
    try:
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
        else:
            raise ValueError("No JSON found in response")

    except Exception as e:
        print(" JSON Parse Error:", e)
        parsed = {
            "issues": [{
                "scenario": "validation",
                "problem": "LLM response parsing failed",
                "severity": "high",
                "action": "regenerate"
            }]
        }

    if not parsed.get("issues"):
        parsed["issues"] = []

    # Syntax Validation 

    try:
        ast.parse(code)
    except SyntaxError as e:
        parsed["issues"].append({
            "scenario": "syntax",
            "problem": f"Syntax error: {str(e)}",
            "severity": "high",
            "action": "fix"
        })

    
    # Detect JavaScript Syntax

    if re.search(r"\{.*?:.*?\}", code):
        parsed["issues"].append({
            "scenario": "syntax",
            "problem": "JavaScript-style object detected in Python code",
            "severity": "high",
            "action": "fix"
        })

    if "=>" in code:
        parsed["issues"].append({
            "scenario": "syntax",
            "problem": "JavaScript arrow function detected",
            "severity": "high",
            "action": "fix"
        })


    # Playwright-specific Checks
  
    if "mouse.move" in code and "{" in code:
        parsed["issues"].append({
            "scenario": "playwright",
            "problem": "Invalid mouse.move syntax (JS-style object used)",
            "severity": "high",
            "action": "fix"
        })

    # Scenario Coverage Check

    for scenario in requirements.get("scenarios", []):
        if scenario.get("id") and scenario["id"] not in code:
            parsed["issues"].append({
                "scenario": scenario["id"],
                "problem": "Missing test case",
                "severity": "medium",
                "action": "generate"
            })

    # NEW: Locator Validation

    if locators:
        for item in locators.get("locators", []):
            scenario_id = item.get("id")

            for loc in item.get("locators", []):
                locator_value = loc.get("locator", "")

                if locator_value and locator_value not in code:
                    parsed["issues"].append({
                        "scenario": scenario_id,
                        "problem": f"Locator not used in code: {locator_value}",
                        "severity": "medium",
                        "action": "fix"
                    })

  
    # NEW: Log-Based Validation
  
    if logs:
        if "TimeoutError" in logs:
            parsed["issues"].append({
                "scenario": "execution",
                "problem": "Timeout detected - possible missing wait or wrong locator",
                "severity": "high",
                "action": "fix"
            })

        if "not found" in logs.lower():
            parsed["issues"].append({
                "scenario": "execution",
                "problem": "Element not found - locator may be incorrect",
                "severity": "high",
                "action": "fix"
            })

        if "AssertionError" in logs:
            parsed["issues"].append({
                "scenario": "execution",
                "problem": "Assertion failure detected",
                "severity": "medium",
                "action": "fix"
            })

    return parsed