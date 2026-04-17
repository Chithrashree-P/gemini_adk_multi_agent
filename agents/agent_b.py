# import json
# import re
# from utils.llm import call_llm


# def clean_code(raw_output: str) -> str:
#     if not raw_output:
#         return ""

#     # Remove markdown
#     code = raw_output.replace("```python", "").replace("```", "")

#     lines = code.splitlines()
#     cleaned = []

#     for line in lines:
#         stripped = line.strip()

#         if not stripped:
#             continue

#         # Remove unwanted LLM text
#         if stripped.lower().startswith((
#             "sure,", "here is", "here's", "below is",
#             "i have generated", "the following code",
#             "here's the code", "the code is"
#         )):
#             continue

#         if stripped.startswith(("*", "-", "•", "Explanation:", "Note:")):
#             continue

#         cleaned.append(line.rstrip())

#     final_code = "\n".join(cleaned).strip()

#     # Remove extra blank lines
#     final_code = re.sub(r'\n{3,}', '\n\n', final_code)

#     return final_code


# def generate_playwright_code(requirements: str):
#     if not requirements:
#         return "def test_empty(): assert True"

#     prompt = f"""You are a senior QA automation engineer expert in Playwright and pytest.

# Generate complete, valid, and runnable Python code.

# Use correct locators from https://the-internet.herokuapp.com/login


# Requirements:
# {requirements}

# STRICT RULES:
# - Return ONLY Python code
# - No explanations, no markdown
# - Start with imports
# - Use pytest
# - Use: from playwright.sync_api import Page, expect
# - Include browser & page fixtures
# - Define BASE_URL
# - Use expect() assertions

# Generate now:
# """

#     raw_output = call_llm(prompt)

#     if not raw_output or "Fallback" in raw_output:
#         return """from playwright.sync_api import Page, expect

# def test_sample():
#     assert True
# """

#     code = clean_code(raw_output)

#     if not code.strip():
#         return "def test_empty(): assert True"

#     return code


# # -------------------------------
# # Fix Code
# # -------------------------------
# def fix_code(requirements: str, existing_code: str, issues: list):
#     issues_text = json.dumps(issues, indent=2)

#     prompt = f"""
#     You are Agent B - Playwright Code Generator. 
#     Generate production-ready Playwright Python code.
#     You are an expert Python code fixer for Playwright tests.

#         Fix ONLY the issues mentioned below.
#         Do NOT regenerate full code unless necessary.

#         Requirements:
#         {requirements}

#         Issues:
#         {issues_text}

#         Existing Code:
#         {existing_code}

#         Return ONLY fixed Python code.

#         RULES:
#         1. Use proper locators: page.get_by_role(), page.get_by_text(), page.locator()
#         2. Include assertions using expect()
#         3. Add proper waits and error handling
#         4. Use test.describe() and test() blocks
#         5. Include setup and teardown
#         6. DO NOT regenerate working scenarios - only add/fix the ones in requirements
#         7. Make code executable with `pytest`

#         Return ONLY the complete Python code.
# """

#     raw_output = call_llm(prompt)

#     if not raw_output or "Fallback" in raw_output:
#         return existing_code

#     code = clean_code(raw_output)

#     if not code.strip():
#         return existing_code

#     return code
import json
import re
from utils.llm import call_llm


def clean_code(raw_output: str) -> str:
    if not raw_output:
        return ""

    code = raw_output.replace("```python", "").replace("```", "")

    lines = code.splitlines()
    cleaned = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.lower().startswith((
            "sure,", "here is", "here's", "below is",
            "i have generated", "the following code",
            "here's the code", "the code is"
        )):
            continue

        if stripped.startswith(("*", "-", "•", "Explanation:", "Note:")):
            continue

        cleaned.append(line.rstrip())

    final_code = "\n".join(cleaned).strip()
    final_code = re.sub(r'\n{3,}', '\n\n', final_code)

    return final_code


# Merge Agent A + Agent K
def build_combined_context(agent_a_output: dict, agent_k_output: dict):
    """
    Merge scenarios with locators
    """
    locator_map = {
        item["id"]: item["locators"]
        for item in agent_k_output.get("locators", [])
    }

    enriched = []

    for scenario in agent_a_output.get("scenarios", []):
        scenario_id = scenario["id"]

        enriched.append({
            "id": scenario_id,
            "title": scenario.get("title"),
            "steps": scenario.get("steps", []),
            "expected": scenario.get("expected"),
            "locators": locator_map.get(scenario_id, [])
        })

    return enriched


# UPDATED MAIN FUNCTION
def generate_playwright_code(agent_a_output: dict, agent_k_output: dict):
    if not agent_a_output:
        return "def test_empty(): assert True"

    base_url = agent_a_output.get("url", "")

    enriched_scenarios = build_combined_context(agent_a_output, agent_k_output)

    prompt = f"""
You are Agent B - Playwright Code Generator.

Generate production-ready Playwright Python code using pytest.

Base URL:
{base_url}

Scenarios with Locators:
{json.dumps(enriched_scenarios, indent=2)}

STRICT RULES:
- Use ONLY provided locators (DO NOT guess)
- Use pytest
- Start with imports
- Use: from playwright.sync_api import Page, expect
- Use BASE_URL
- Each scenario → one test function
- Use correct actions:
    fill → .fill()
    click → .click()
- Add assertions using expect()
- Add waits where needed
- Clean, readable, maintainable code

Return ONLY Python code.
"""

    raw_output = call_llm(prompt)

    if not raw_output or "Fallback" in raw_output:
        return """from playwright.sync_api import Page, expect

def test_sample():
    assert True
"""

    code = clean_code(raw_output)

    if not code.strip():
        return "def test_empty(): assert True"

    return code



# FIX CODE (UPDATED)

def fix_code(agent_a_output: dict, agent_k_output: dict, existing_code: str, issues: list):
    issues_text = json.dumps(issues, indent=2)

    enriched_scenarios = build_combined_context(agent_a_output, agent_k_output)

    prompt = f"""
You are an expert Playwright test fixer.

Fix ONLY the issues mentioned.

Scenarios with Locators:
{json.dumps(enriched_scenarios, indent=2)}

Issues:
{issues_text}

Existing Code:
{existing_code}

RULES:
1. Use ONLY provided locators
2. Do NOT break working tests
3. Add missing assertions using expect()
4. Fix waits, selectors, failures
5. Keep pytest structure intact

Return ONLY fixed Python code.
"""

    raw_output = call_llm(prompt)

    if not raw_output or "Fallback" in raw_output:
        return existing_code

    code = clean_code(raw_output)

    if not code.strip():
        return existing_code

    return code